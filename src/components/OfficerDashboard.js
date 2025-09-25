import React, { useState, useEffect } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { 
  AlertTriangle,
  CheckCircle2,
  Clock,
  Eye,
  Map,
  FileText,
  TrendingUp,
  Users,
  MapPin,
  Calendar,
  Filter,
  Search,
  Download,
  Camera,
  Satellite,
  Shield
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const OfficerDashboard = () => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState('verification');
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data for high-priority claims needing verification
  const priorityClaims = [
    {
      id: 'FRA-2024-001',
      beneficiary: 'Ram Singh',
      village: 'Khargone Village',
      district: 'Khargone, MP',
      claimType: 'Individual Forest Rights',
      landArea: 2.5,
      status: 'pending_verification',
      priority: 'high',
      submittedDate: '2024-02-01',
      aiRisk: 'medium',
      fraudFlags: ['Overlapping coordinates', 'Document quality issues'],
      coordinates: { lat: 21.8256, lng: 75.6108 },
      documents: [
        { name: 'Land Records', status: 'verified', confidence: 0.92 },
        { name: 'Residence Proof', status: 'flagged', confidence: 0.67 },
        { name: 'Survey Settlement', status: 'pending', confidence: null }
      ],
      aiRecommendation: {
        decision: 'requires_field_verification',
        confidence: 0.73,
        reasons: ['Boundary discrepancy detected', 'Need GPS verification']
      }
    },
    {
      id: 'FRA-2024-002',
      beneficiary: 'Sita Devi',
      village: 'Bastar Village',
      district: 'Bastar, CG',
      claimType: 'Community Forest Rights',
      landArea: 45.0,
      status: 'under_review',
      priority: 'urgent',
      submittedDate: '2024-01-28',
      aiRisk: 'low',
      fraudFlags: [],
      coordinates: { lat: 19.0164, lng: 81.9630 },
      documents: [
        { name: 'Community Resolution', status: 'verified', confidence: 0.95 },
        { name: 'Forest Clearance', status: 'verified', confidence: 0.88 },
        { name: 'Survey Map', status: 'verified', confidence: 0.91 }
      ],
      aiRecommendation: {
        decision: 'approve',
        confidence: 0.91,
        reasons: ['All documents verified', 'No boundary conflicts']
      }
    },
    {
      id: 'FRA-2024-003',
      beneficiary: 'Tribal Cooperative',
      village: 'Gadchiroli Village',
      district: 'Gadchiroli, MH',
      claimType: 'Development Rights',
      landArea: 12.0,
      status: 'disputed',
      priority: 'high',
      submittedDate: '2024-01-25',
      aiRisk: 'high',
      fraudFlags: ['Duplicate claim detected', 'Suspicious documents', 'Conflicting surveys'],
      coordinates: { lat: 20.1829, lng: 80.0066 },
      documents: [
        { name: 'Project Proposal', status: 'flagged', confidence: 0.42 },
        { name: 'Environmental Clearance', status: 'pending', confidence: null },
        { name: 'Community Consent', status: 'flagged', confidence: 0.38 }
      ],
      aiRecommendation: {
        decision: 'reject',
        confidence: 0.84,
        reasons: ['Multiple fraud indicators', 'Document authenticity issues']
      }
    }
  ];

  // Analytics data
  const analyticsData = {
    todayStats: {
      pendingVerification: 23,
      completedToday: 8,
      fraudDetected: 3,
      fieldVisitsScheduled: 5
    },
    weeklyTrends: {
      claimsProcessed: [12, 15, 18, 22, 19, 25, 28],
      fraudDetected: [1, 2, 0, 3, 1, 2, 3],
      avgProcessingTime: 4.2 // days
    },
    budgetTracking: {
      allocated: 12500000,
      utilized: 8750000,
      pending: 2300000,
      available: 1450000
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'high': return 'text-red-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const openSatelliteView = (coordinates) => {
    // Integration with ISRO Bhuvan or Google Earth
    const bhuvanUrl = `https://bhuvan-app1.nrsc.gov.in/bhuvan2d/bhuvan/bhuvan2d.php?lat=${coordinates.lat}&lon=${coordinates.lng}&zoom=16`;
    window.open(bhuvanUrl, '_blank');
  };

  const generateFieldReport = (claim) => {
    // Generate field verification report
    console.log('Generating field report for:', claim.id);
  };

  const quickApprove = (claimId) => {
    // Quick approval for low-risk claims
    console.log('Quick approving claim:', claimId);
  };

  const flagForInvestigation = (claimId) => {
    // Flag high-risk claims for detailed investigation
    console.log('Flagging claim for investigation:', claimId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('officerDashboard')}</h1>
              <p className="text-sm text-gray-600">{t('verificationAndProcessing')}</p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-sm">
                <span className="text-gray-600">{t('pendingVerification')}: </span>
                <span className="font-bold text-red-600">{analyticsData.todayStats.pendingVerification}</span>
              </div>
              <div className="text-sm">
                <span className="text-gray-600">{t('completedToday')}: </span>
                <span className="font-bold text-green-600">{analyticsData.todayStats.completedToday}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('pendingVerification')}</p>
                  <p className="text-2xl font-bold text-red-600">{analyticsData.todayStats.pendingVerification}</p>
                </div>
                <Clock className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('completedToday')}</p>
                  <p className="text-2xl font-bold text-green-600">{analyticsData.todayStats.completedToday}</p>
                </div>
                <CheckCircle2 className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('fraudDetected')}</p>
                  <p className="text-2xl font-bold text-red-600">{analyticsData.todayStats.fraudDetected}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{t('avgProcessingTime')}</p>
                  <p className="text-2xl font-bold text-blue-600">{analyticsData.weeklyTrends.avgProcessingTime}d</p>
                </div>
                <TrendingUp className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Claims List */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-5 h-5" />
                {t('priorityClaimsVerification')}
              </CardTitle>
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <Search className="w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder={t('searchClaims')}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="px-3 py-1 border rounded-md text-sm"
                  />
                </div>
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value="all">{t('allStatus')}</option>
                  <option value="pending_verification">{t('pendingVerification')}</option>
                  <option value="under_review">{t('underReview')}</option>
                  <option value="disputed">{t('disputed')}</option>
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {priorityClaims.map((claim) => (
                <div key={claim.id} className={`p-4 border rounded-lg ${
                  claim.aiRisk === 'high' ? 'border-red-200 bg-red-50' : 
                  claim.aiRisk === 'medium' ? 'border-yellow-200 bg-yellow-50' : 
                  'border-gray-200 bg-white'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-gray-900">{claim.id}</h3>
                        <Badge className={getPriorityColor(claim.priority)}>
                          {t(claim.priority)} {t('priority')}
                        </Badge>
                        <Badge className={`bg-gray-100 ${getRiskColor(claim.aiRisk)}`}>
                          {t('aiRisk')}: {t(claim.aiRisk)}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                        <div>
                          <p className="text-sm text-gray-600">{t('beneficiary')}</p>
                          <p className="font-medium">{claim.beneficiary}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">{t('location')}</p>
                          <p className="font-medium">{claim.village}, {claim.district}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">{t('landArea')}</p>
                          <p className="font-medium">{claim.landArea} {t('hectares')}</p>
                        </div>
                      </div>

                      {/* AI Recommendation */}
                      <div className="bg-blue-50 p-3 rounded-lg mb-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Shield className="w-4 h-4 text-blue-600" />
                          <span className="font-medium text-blue-900">
                            {t('aiRecommendation')}: {t(claim.aiRecommendation.decision)}
                          </span>
                          <span className="text-sm text-blue-700">
                            ({Math.round(claim.aiRecommendation.confidence * 100)}% {t('confidence')})
                          </span>
                        </div>
                        <ul className="text-sm text-blue-800 space-y-1">
                          {claim.aiRecommendation.reasons.map((reason, index) => (
                            <li key={index} className="flex items-center gap-2">
                              <div className="w-1 h-1 bg-blue-600 rounded-full" />
                              {reason}
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Fraud Flags */}
                      {claim.fraudFlags.length > 0 && (
                        <div className="bg-red-50 p-3 rounded-lg mb-3">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-4 h-4 text-red-600" />
                            <span className="font-medium text-red-900">{t('fraudAlerts')}</span>
                          </div>
                          <ul className="text-sm text-red-800 space-y-1">
                            {claim.fraudFlags.map((flag, index) => (
                              <li key={index} className="flex items-center gap-2">
                                <div className="w-1 h-1 bg-red-600 rounded-full" />
                                {flag}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Document Status */}
                      <div className="flex flex-wrap gap-2 mb-3">
                        {claim.documents.map((doc, index) => (
                          <Badge key={index} variant="outline" className={
                            doc.status === 'verified' ? 'border-green-500 text-green-700' :
                            doc.status === 'flagged' ? 'border-red-500 text-red-700' :
                            'border-gray-500 text-gray-700'
                          }>
                            {doc.name}: {t(doc.status)}
                            {doc.confidence && ` (${Math.round(doc.confidence * 100)}%)`}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2 ml-4">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openSatelliteView(claim.coordinates)}
                        className="flex items-center gap-1"
                      >
                        <Satellite className="w-4 h-4" />
                        {t('satelliteView')}
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => generateFieldReport(claim)}
                        className="flex items-center gap-1"
                      >
                        <FileText className="w-4 h-4" />
                        {t('fieldReport')}
                      </Button>

                      {claim.aiRecommendation.decision === 'approve' && claim.aiRisk === 'low' && (
                        <Button
                          size="sm"
                          onClick={() => quickApprove(claim.id)}
                          className="bg-green-600 hover:bg-green-700 flex items-center gap-1"
                        >
                          <CheckCircle2 className="w-4 h-4" />
                          {t('quickApprove')}
                        </Button>
                      )}

                      {claim.aiRisk === 'high' && (
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => flagForInvestigation(claim.id)}
                          className="flex items-center gap-1"
                        >
                          <AlertTriangle className="w-4 h-4" />
                          {t('flagForInvestigation')}
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Budget Tracking */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardHeader>
              <CardTitle>{t('budgetTracking')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('totalAllocated')}</span>
                  <span className="font-bold">₹{(analyticsData.budgetTracking.allocated / 10000000).toFixed(1)}Cr</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('utilized')}</span>
                  <span className="font-bold text-green-600">₹{(analyticsData.budgetTracking.utilized / 10000000).toFixed(1)}Cr</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('pending')}</span>
                  <span className="font-bold text-yellow-600">₹{(analyticsData.budgetTracking.pending / 10000000).toFixed(1)}Cr</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('available')}</span>
                  <span className="font-bold text-blue-600">₹{(analyticsData.budgetTracking.available / 10000000).toFixed(1)}Cr</span>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full" 
                    style={{ width: `${(analyticsData.budgetTracking.utilized / analyticsData.budgetTracking.allocated) * 100}%` }}
                  ></div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('weeklyPerformance')}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('claimsProcessed')}</span>
                  <span className="font-bold">{analyticsData.weeklyTrends.claimsProcessed.reduce((a, b) => a + b, 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('fraudDetected')}</span>
                  <span className="font-bold text-red-600">{analyticsData.weeklyTrends.fraudDetected.reduce((a, b) => a + b, 0)}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">{t('avgProcessingTime')}</span>
                  <span className="font-bold">{analyticsData.weeklyTrends.avgProcessingTime} {t('days')}</span>
                </div>
                
                <Button variant="outline" className="w-full">
                  <Download className="w-4 h-4 mr-2" />
                  {t('downloadReport')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default OfficerDashboard;