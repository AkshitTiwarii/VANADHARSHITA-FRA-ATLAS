import React, { useState, useEffect } from 'react';
import { useTranslation } from '../contexts/LanguageContext';
import { 
  FileText, 
  MapPin, 
  User, 
  Calendar,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Upload,
  Camera,
  Mic,
  Volume2,
  Languages,
  HelpCircle,
  Phone
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const CitizenPortal = () => {
  const { t, currentLanguage } = useTranslation();
  const [activeTab, setActiveTab] = useState('file-claim');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [claims, setClaims] = useState([]);
  const [newClaim, setNewClaim] = useState({
    claimType: '',
    landArea: '',
    locationDescription: '',
    beneficiaryName: '',
    fatherName: '',
    documents: []
  });

  // Mock user claims data with realistic FRA scenarios
  const mockClaims = [
    {
      id: 'FRA-2024-ABC123',
      claimType: 'Individual Forest Rights',
      landArea: '2.5 hectares',
      status: 'under_review',
      submittedDate: '2024-01-15',
      lastUpdate: '2024-02-01',
      village: 'Khargone Village, Madhya Pradesh',
      officerName: 'Shri Ram Kumar',
      nextAction: 'Field verification scheduled for 15th Feb',
      documents: ['Land records', 'Residence proof', 'Photo ID'],
      timeline: [
        { date: '2024-01-15', action: 'Claim submitted', status: 'completed' },
        { date: '2024-01-22', action: 'Initial review', status: 'completed' },
        { date: '2024-02-01', action: 'Document verification', status: 'completed' },
        { date: '2024-02-15', action: 'Field verification', status: 'pending' },
        { date: 'TBD', action: 'Final approval', status: 'pending' }
      ]
    },
    {
      id: 'FRA-2023-XYZ789',
      claimType: 'Community Forest Rights',
      landArea: '45 hectares',
      status: 'approved',
      submittedDate: '2023-08-20',
      lastUpdate: '2023-11-30',
      village: 'Bastar Village, Chhattisgarh',
      officerName: 'Smt. Priya Sharma',
      nextAction: 'Title deed collection - visit office',
      documents: ['Community resolution', 'Land survey', 'Forest clearance'],
      timeline: [
        { date: '2023-08-20', action: 'Claim submitted', status: 'completed' },
        { date: '2023-09-05', action: 'Community hearing', status: 'completed' },
        { date: '2023-10-15', action: 'Forest department approval', status: 'completed' },
        { date: '2023-11-30', action: 'Final approval granted', status: 'completed' }
      ]
    }
  ];

  const claimTypes = [
    { value: 'ifr', label: t('individualForestRights'), description: t('ifrDescription') },
    { value: 'cfr', label: t('communityForestRights'), description: t('cfrDescription') },
    { value: 'habitat', label: t('habitatRights'), description: t('habitatDescription') },
    { value: 'development', label: t('developmentRights'), description: t('developmentDescription') }
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'under_review': return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'pending': return <Clock className="w-5 h-5 text-blue-600" />;
      case 'disputed': return <AlertTriangle className="w-5 h-5 text-red-600" />;
      default: return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'under_review': return 'bg-yellow-100 text-yellow-800';
      case 'pending': return 'bg-blue-100 text-blue-800';
      case 'disputed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-IN';
      speechSynthesis.speak(utterance);
    }
  };

  const startVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        // Process voice input for form filling
        console.log('Voice input:', transcript);
      };
      recognition.start();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{t('citizenPortal')}</h1>
              <p className="text-sm text-gray-600">{t('citizenPortalSubtitle')}</p>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => speakText(t('welcomeToCitizenPortal'))}
                className="flex items-center gap-2"
              >
                <Volume2 className="w-4 h-4" />
                {t('hearInstructions')}
              </Button>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Phone className="w-4 h-4" />
                {t('helpline')}: 1800-XXX-XXXX
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="flex gap-1 bg-gray-100 p-1 rounded-lg mb-6">
          <button
            onClick={() => setActiveTab('file-claim')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'file-claim'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-2" />
            {t('fileNewClaim')}
          </button>
          <button
            onClick={() => setActiveTab('track-claims')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'track-claims'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <MapPin className="w-4 h-4 inline mr-2" />
            {t('trackClaims')}
          </button>
          <button
            onClick={() => setActiveTab('guidance')}
            className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors ${
              activeTab === 'guidance'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <HelpCircle className="w-4 h-4 inline mr-2" />
            {t('legalGuidance')}
          </button>
        </div>

        {/* File New Claim Tab */}
        {activeTab === 'file-claim' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  {t('fileNewClaim')}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Claim Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    {t('selectClaimType')}
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {claimTypes.map((type) => (
                      <div
                        key={type.value}
                        onClick={() => setNewClaim({...newClaim, claimType: type.value})}
                        className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                          newClaim.claimType === type.value
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <h3 className="font-medium text-gray-900">{type.label}</h3>
                        <p className="text-sm text-gray-600 mt-1">{type.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('beneficiaryName')}
                    </label>
                    <input
                      type="text"
                      value={newClaim.beneficiaryName}
                      onChange={(e) => setNewClaim({...newClaim, beneficiaryName: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={t('enterFullName')}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('fatherName')}
                    </label>
                    <input
                      type="text"
                      value={newClaim.fatherName}
                      onChange={(e) => setNewClaim({...newClaim, fatherName: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={t('enterFatherName')}
                    />
                  </div>
                </div>

                {/* Land Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('landArea')} ({t('hectares')})
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      value={newClaim.landArea}
                      onChange={(e) => setNewClaim({...newClaim, landArea: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="0.0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('locationDescription')}
                    </label>
                    <input
                      type="text"
                      value={newClaim.locationDescription}
                      onChange={(e) => setNewClaim({...newClaim, locationDescription: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={t('describeLandLocation')}
                    />
                  </div>
                </div>

                {/* Document Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    {t('uploadDocuments')}
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <div className="flex justify-center gap-4 mb-4">
                      <Button variant="outline" className="flex items-center gap-2">
                        <Upload className="w-4 h-4" />
                        {t('chooseFiles')}
                      </Button>
                      <Button variant="outline" className="flex items-center gap-2">
                        <Camera className="w-4 h-4" />
                        {t('takePhoto')}
                      </Button>
                    </div>
                    <p className="text-sm text-gray-600">
                      {t('supportedFormats')}: PDF, JPG, PNG ({t('maxSize')}: 5MB)
                    </p>
                  </div>
                </div>

                {/* Voice Input */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Mic className="w-5 h-5 text-blue-600" />
                      <span className="font-medium text-blue-900">{t('voiceAssistance')}</span>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={startVoiceRecognition}
                      className="flex items-center gap-2"
                    >
                      <Mic className="w-4 h-4" />
                      {t('speakToFillForm')}
                    </Button>
                  </div>
                  <p className="text-sm text-blue-700 mt-2">
                    {t('voiceInstructions')}
                  </p>
                </div>

                {/* Submit Button */}
                <div className="flex justify-end">
                  <Button className="px-8 py-2 bg-green-600 hover:bg-green-700">
                    {t('submitClaim')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Track Claims Tab */}
        {activeTab === 'track-claims' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mockClaims.map((claim) => (
                <Card key={claim.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-lg">{claim.id}</CardTitle>
                      <Badge className={getStatusColor(claim.status)}>
                        {t(claim.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(claim.status)}
                      <span className="text-sm font-medium">{t(claim.claimType)}</span>
                    </div>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t('landArea')}:</span>
                        <span className="font-medium">{claim.landArea}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t('village')}:</span>
                        <span className="font-medium text-xs">{claim.village}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">{t('officer')}:</span>
                        <span className="font-medium">{claim.officerName}</span>
                      </div>
                    </div>

                    <div className="bg-yellow-50 p-3 rounded-lg">
                      <h4 className="text-sm font-medium text-yellow-800 mb-1">
                        {t('nextAction')}
                      </h4>
                      <p className="text-xs text-yellow-700">{claim.nextAction}</p>
                    </div>

                    {/* Timeline */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium text-gray-900">{t('timeline')}</h4>
                      <div className="space-y-1">
                        {claim.timeline.slice(-3).map((item, index) => (
                          <div key={index} className="flex items-center gap-2 text-xs">
                            <div className={`w-2 h-2 rounded-full ${
                              item.status === 'completed' ? 'bg-green-500' : 'bg-gray-300'
                            }`} />
                            <span className="text-gray-600">{item.date}</span>
                            <span className="text-gray-800">{item.action}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Button variant="outline" size="sm" className="w-full">
                      {t('viewFullDetails')}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Legal Guidance Tab */}
        {activeTab === 'guidance' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>{t('legalGuidance')}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">{t('eligibilityCriteria')}</h3>
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {t('criteria1')}
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {t('criteria2')}
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {t('criteria3')}
                      </li>
                    </ul>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">{t('requiredDocuments')}</h3>
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('document1')}
                      </li>
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('document2')}
                      </li>
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('document3')}
                      </li>
                    </ul>
                  </div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">{t('grievanceRedressal')}</h4>
                  <p className="text-sm text-green-800 mb-3">
                    {t('grievanceInstructions')}
                  </p>
                  <Button variant="outline" size="sm" className="text-green-700 border-green-700">
                    {t('fileGrievance')}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default CitizenPortal;