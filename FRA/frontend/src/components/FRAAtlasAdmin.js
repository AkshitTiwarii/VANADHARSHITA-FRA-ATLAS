import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from './ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { AlertTriangle, CheckCircle, XCircle, Upload, FileText, Map, TrendingUp } from 'lucide-react';

const FRAAtlasAdmin = () => {
  const [validations, setValidations] = useState([]);
  const [claims, setClaims] = useState([]);
  const [selectedValidation, setSelectedValidation] = useState(null);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [showValidationDialog, setShowValidationDialog] = useState(false);
  const [showClaimDialog, setShowClaimDialog] = useState(false);
  const [stateProgress, setStateProgress] = useState({});
  const [loading, setLoading] = useState({
    validations: false,
    claims: false,
    stateProgress: false
  });

  // Load data on component mount
  useEffect(() => {
    loadValidations();
    loadClaims();
    loadStateProgress();
  }, []);

  const loadValidations = async () => {
    setLoading(prev => ({ ...prev, validations: true }));
    try {
      const response = await fetch('/api/data/validations');
      const data = await response.json();
      setValidations(data);
    } catch (error) {
      console.error('Error loading validations:', error);
    } finally {
      setLoading(prev => ({ ...prev, validations: false }));
    }
  };

  const loadClaims = async () => {
    setLoading(prev => ({ ...prev, claims: true }));
    try {
      const response = await fetch('/api/claims?limit=100');
      const data = await response.json();
      setClaims(data);
    } catch (error) {
      console.error('Error loading claims:', error);
    } finally {
      setLoading(prev => ({ ...prev, claims: false }));
    }
  };

  const loadStateProgress = async () => {
    setLoading(prev => ({ ...prev, stateProgress: true }));
    try {
      // Load progress for major states
      const states = ['Maharashtra', 'Madhya Pradesh', 'Chhattisgarh', 'Odisha', 'Jharkhand'];
      const progressData = {};
      
      for (const state of states) {
        const response = await fetch(`/api/progress/state/${state}`);
        const data = await response.json();
        progressData[state] = data;
      }
      
      setStateProgress(progressData);
    } catch (error) {
      console.error('Error loading state progress:', error);
    } finally {
      setLoading(prev => ({ ...prev, stateProgress: false }));
    }
  };

  const updateValidationStatus = async (validationId, status, notes) => {
    try {
      const formData = new FormData();
      formData.append('status', status);
      formData.append('notes', notes);
      formData.append('validated_by', 'Admin'); // In real app, get from auth

      const response = await fetch(`/api/data/validations/${validationId}`, {
        method: 'PUT',
        body: formData
      });

      if (response.ok) {
        loadValidations();
        setShowValidationDialog(false);
        setSelectedValidation(null);
      }
    } catch (error) {
      console.error('Error updating validation:', error);
    }
  };

  const updateClaimStatus = async (claimId, status, notes, officer) => {
    try {
      const formData = new FormData();
      formData.append('new_status', status);
      formData.append('notes', notes);
      formData.append('officer', officer || 'Admin');

      const response = await fetch(`/api/claims/${claimId}/status`, {
        method: 'PUT',
        body: formData
      });

      if (response.ok) {
        loadClaims();
        setShowClaimDialog(false);
        setSelectedClaim(null);
      }
    } catch (error) {
      console.error('Error updating claim status:', error);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'pass': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'fail': { color: 'bg-red-100 text-red-800', icon: XCircle },
      'pending': { color: 'bg-yellow-100 text-yellow-800', icon: AlertTriangle },
      'approved': { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      'rejected': { color: 'bg-red-100 text-red-800', icon: XCircle },
      'disputed': { color: 'bg-orange-100 text-orange-800', icon: AlertTriangle },
      'verified': { color: 'bg-blue-100 text-blue-800', icon: CheckCircle }
    };

    const config = statusConfig[status] || { color: 'bg-gray-100 text-gray-800', icon: AlertTriangle };
    const Icon = config.icon;

    return (
      <Badge className={`${config.color} flex items-center gap-1`}>
        <Icon className="w-3 h-3" />
        {status}
      </Badge>
    );
  };

  const ValidationDialog = () => {
    const [status, setStatus] = useState('');
    const [notes, setNotes] = useState('');

    return (
      <Dialog open={showValidationDialog} onOpenChange={setShowValidationDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Update Validation Status</DialogTitle>
            <DialogDescription>
              Review the data validation for "{selectedValidation?.dataset_name}"
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Confidence Score</label>
              <div className="text-lg font-bold text-blue-600">
                {(selectedValidation?.confidence_score * 100)?.toFixed(1)}%
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Issues Found</label>
              <div className="space-y-1">
                {selectedValidation?.issues_found?.map((issue, index) => (
                  <Badge key={index} variant="secondary" className="mr-2">{issue}</Badge>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Record Count</label>
              <div>{selectedValidation?.record_count?.toLocaleString()} records</div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Validation Decision</label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select validation status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pass">Pass - Data Quality Good</SelectItem>
                  <SelectItem value="fail">Fail - Data Quality Poor</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Notes</label>
              <Textarea
                placeholder="Add validation notes..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={() => updateValidationStatus(selectedValidation?.id, status, notes)}
              disabled={!status}
            >
              Update Status
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  };

  const ClaimStatusDialog = () => {
    const [status, setStatus] = useState('');
    const [notes, setNotes] = useState('');
    const [officer, setOfficer] = useState('');

    return (
      <Dialog open={showClaimDialog} onOpenChange={setShowClaimDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Update Claim Status</DialogTitle>
            <DialogDescription>
              Update status for claim #{selectedClaim?.claim_number}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Beneficiary</label>
                <div className="text-sm">{selectedClaim?.beneficiary_name}</div>
              </div>
              <div>
                <label className="text-sm font-medium">Village</label>
                <div className="text-sm">{selectedClaim?.village_name}</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">Claim Type</label>
                <div className="text-sm">{selectedClaim?.claim_type}</div>
              </div>
              <div>
                <label className="text-sm font-medium">Area Claimed</label>
                <div className="text-sm">{selectedClaim?.area_claimed} hectares</div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Current Status</label>
              <div className="mt-1">
                {selectedClaim && getStatusBadge(selectedClaim.status)}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">New Status</label>
              <Select value={status} onValueChange={setStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="under_review">Under Review</SelectItem>
                  <SelectItem value="verified">Verified</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="disputed">Disputed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Assigned Officer</label>
              <Input
                placeholder="Enter officer name..."
                value={officer}
                onChange={(e) => setOfficer(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Status Change Notes</label>
              <Textarea
                placeholder="Add notes about this status change..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              onClick={() => updateClaimStatus(selectedClaim?.id, status, notes, officer)}
              disabled={!status}
            >
              Update Status
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">FRA Atlas Administration</h1>
        <Button className="bg-green-600 hover:bg-green-700">
          <Upload className="w-4 h-4 mr-2" />
          Upload New Dataset
        </Button>
      </div>

      <Tabs defaultValue="validations" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="validations">Data Validations</TabsTrigger>
          <TabsTrigger value="claims">FRA Claims</TabsTrigger>
          <TabsTrigger value="progress">State Progress</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="validations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Dataset Validations
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.validations ? (
                <div className="text-center py-8">Loading validations...</div>
              ) : (
                <div className="space-y-4">
                  {validations.map((validation) => (
                    <div
                      key={validation.id}
                      className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedValidation(validation);
                        setShowValidationDialog(true);
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="font-medium">{validation.dataset_name}</div>
                          <div className="text-sm text-gray-600">
                            {validation.record_count?.toLocaleString()} records
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className="text-lg font-bold text-blue-600">
                              {(validation.confidence_score * 100)?.toFixed(1)}%
                            </div>
                            <div className="text-xs text-gray-500">Confidence</div>
                          </div>
                          {getStatusBadge(validation.validation_status)}
                        </div>
                      </div>
                      {validation.issues_found?.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {validation.issues_found.map((issue, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {issue}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="claims" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Map className="w-5 h-5" />
                FRA Claims Management
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading.claims ? (
                <div className="text-center py-8">Loading claims...</div>
              ) : (
                <div className="space-y-4">
                  {claims.slice(0, 20).map((claim) => (
                    <div
                      key={claim.id}
                      className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                      onClick={() => {
                        setSelectedClaim(claim);
                        setShowClaimDialog(true);
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="space-y-1">
                          <div className="font-medium">
                            Claim #{claim.claim_number}
                          </div>
                          <div className="text-sm text-gray-600">
                            {claim.beneficiary_name} • {claim.village_name}
                          </div>
                          <div className="text-sm text-gray-500">
                            {claim.claim_type} • {claim.area_claimed} hectares
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className="text-sm text-gray-500">
                              {claim.assigned_officer || 'Unassigned'}
                            </div>
                          </div>
                          {getStatusBadge(claim.status)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="progress" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(stateProgress).map(([state, progress]) => (
              <Card key={state}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    {state}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">
                        {progress.progress_percentage?.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Implementation Progress</div>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Total Claims</span>
                        <span className="font-medium">{progress.total_claims}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Approved</span>
                        <span className="font-medium text-green-600">{progress.approved_claims}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Pending</span>
                        <span className="font-medium text-yellow-600">{progress.pending_claims}</span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>FRA Analytics Dashboard</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-600">
                Analytics dashboard coming soon...
                <br />
                Will include claim processing trends, approval rates, and regional insights.
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <ValidationDialog />
      <ClaimStatusDialog />
    </div>
  );
};

export default FRAAtlasAdmin;