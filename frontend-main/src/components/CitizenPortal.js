import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
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
  Phone,
  ArrowLeft,
  Home,
  X,
  Loader2,
  Scan
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import axios from 'axios';
import { toast } from 'sonner';

const CitizenPortal = () => {
  const navigate = useNavigate();
  const { t, currentLanguage } = useTranslation();
  const [activeTab, setActiveTab] = useState('file-claim');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const [claims, setClaims] = useState([]);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [processingOCR, setProcessingOCR] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
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
    { value: 'ifr', label: t('individualForestRights'), description: t('individualForestRightsDesc') },
    { value: 'cfr', label: t('communityForestRights'), description: t('communityForestRightsDesc') },
    { value: 'habitat', label: t('habitatRights'), description: t('habitatRightsDesc') },
    { value: 'development', label: t('developmentRights'), description: t('developmentRightsDesc') }
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

  const getStatusText = (status) => {
    switch (status) {
      case 'approved': return t('approvedStatus');
      case 'under_review': return t('underReviewStatus');
      case 'pending': return t('pendingStatus');
      case 'disputed': return t('disputed');
      default: return status;
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
    if (window.webkitSpeechRecognition || window.SpeechRecognition) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = currentLanguage === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        // Process voice input for form filling
        console.log('Voice input:', transcript);
      };
      recognition.start();
    }
  };

  // Camera and OCR Functions
  const startCamera = async () => {
    try {
      // Check if camera is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        toast.error('Camera not supported', {
          description: 'Your browser does not support camera access. Please use Chrome, Firefox, or Safari.'
        });
        return;
      }

      // Request camera permission with fallback options
      let constraints = { 
        video: { 
          facingMode: 'environment', // Prefer back camera
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        } 
      };

      try {
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        setCameraStream(stream);
        setShowCamera(true);
        
        // Wait for modal to render, then attach stream
        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            videoRef.current.play().catch(err => {
              console.error('Video play error:', err);
            });
          }
        }, 100);
        
        toast.success('Camera ready! Position your document.');
      } catch (err) {
        // Fallback: try with any camera (front or back)
        console.warn('Back camera not available, trying any camera...', err);
        const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true });
        setCameraStream(fallbackStream);
        setShowCamera(true);
        
        setTimeout(() => {
          if (videoRef.current) {
            videoRef.current.srcObject = fallbackStream;
            videoRef.current.play().catch(e => console.error('Video play error:', e));
          }
        }, 100);
        
        toast.success('Camera ready! (Using available camera)');
      }
    } catch (error) {
      console.error('Camera access denied:', error);
      
      let errorMessage = 'Unable to access camera.';
      let errorDescription = 'Please check permissions.';
      
      if (error.name === 'NotAllowedError') {
        errorDescription = 'Camera permission denied. Please allow camera access in browser settings.';
      } else if (error.name === 'NotFoundError') {
        errorDescription = 'No camera found on this device.';
      } else if (error.name === 'NotReadableError') {
        errorDescription = 'Camera is already in use by another application.';
      } else if (error.name === 'SecurityError') {
        errorDescription = 'Camera access blocked. Make sure you are using HTTPS or localhost.';
      }
      
      toast.error(errorMessage, { description: errorDescription });
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    setShowCamera(false);
  };

  const captureImage = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(async (blob) => {
      if (blob) {
        await processOCR(blob);
      }
    }, 'image/jpeg', 0.95);
  };

  const processOCR = async (imageBlob) => {
    setProcessingOCR(true);
    stopCamera();
    
    try {
      const formData = new FormData();
      formData.append('file', imageBlob, 'document.jpg');

      // Call AI service OCR endpoint
      const response = await axios.post('http://localhost:8000/api/ocr/extract', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data && response.data.extracted_data) {
        const data = response.data.extracted_data;
        
        // Auto-fill form fields from OCR data
        setNewClaim(prev => ({
          ...prev,
          beneficiaryName: data.name || prev.beneficiaryName,
          fatherName: data.father_name || prev.fatherName,
          landArea: data.land_area || prev.landArea,
          locationDescription: data.location || prev.locationDescription
        }));

        toast.success('Document scanned successfully! Form fields auto-filled.', {
          description: 'Please review and correct any information if needed.'
        });
      }
    } catch (error) {
      console.error('OCR processing error:', error);
      toast.error('Failed to process document', {
        description: 'Please try again or enter details manually.'
      });
    } finally {
      setProcessingOCR(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (file) {
      await processOCR(file);
    }
  };

  // Cleanup camera on unmount
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [cameraStream]);

  // Connect video stream when camera modal opens
  useEffect(() => {
    if (showCamera && cameraStream && videoRef.current) {
      videoRef.current.srcObject = cameraStream;
      videoRef.current.play().catch(err => {
        console.error('Error playing video:', err);
      });
    }
  }, [showCamera, cameraStream]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Back Button */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                <span className="font-medium">{t('backToHome')}</span>
              </button>
              <div className="h-8 w-px bg-gray-300"></div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{t('citizenPortal')}</h1>
                <p className="text-sm text-gray-600">{t('citizenPortalDesc')}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => speakText(t('citizenPortalDesc'))}
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
                      {t('landAreaHectares')}
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

                {/* Document Upload with OCR */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    {t('uploadDocuments')}
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                    <div className="flex flex-col items-center gap-4">
                      <div className="flex items-center gap-2 text-blue-600">
                        <Scan className="w-5 h-5" />
                        <span className="font-medium">{t('smartDocumentScanner')}</span>
                      </div>
                      <p className="text-sm text-gray-600 text-center mb-2">
                        {t('scanDocumentsToAutofill')}
                      </p>
                      <div className="flex justify-center gap-4">
                        <label htmlFor="file-upload">
                          <Button 
                            variant="outline" 
                            className="flex items-center gap-2"
                            onClick={(e) => {
                              e.preventDefault();
                              document.getElementById('file-upload').click();
                            }}
                            disabled={processingOCR}
                          >
                            <Upload className="w-4 h-4" />
                            {t('chooseFiles')}
                          </Button>
                        </label>
                        <input
                          id="file-upload"
                          type="file"
                          accept="image/*,.pdf"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                        <Button 
                          variant="outline" 
                          className="flex items-center gap-2"
                          onClick={startCamera}
                          disabled={processingOCR}
                        >
                          <Camera className="w-4 h-4" />
                          {t('scanDocument')}
                        </Button>
                      </div>
                      {processingOCR && (
                        <div className="flex items-center gap-2 text-blue-600 mt-2">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          <span className="text-sm">{t('processingDocumentAI')}</span>
                        </div>
                      )}
                      <p className="text-xs text-gray-500 mt-2">
                        {t('supportedDocuments')}
                      </p>
                    </div>
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
                    {t('useVoiceToFill')}
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
                        {getStatusText(claim.status)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(claim.status)}
                      <span className="text-sm font-medium">{claim.claimType}</span>
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
                        {t('mustBeResiding')}
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {t('dependentOnForest')}
                      </li>
                      <li className="flex items-start gap-2">
                        <CheckCircle2 className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                        {t('occupationBefore2005')}
                      </li>
                    </ul>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">{t('requiredDocuments')}</h3>
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('proofOfResidence')}
                      </li>
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('evidenceOfOccupation')}
                      </li>
                      <li className="flex items-start gap-2">
                        <FileText className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                        {t('selfDeclaration')}
                      </li>
                    </ul>
                  </div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">{t('grievanceRedressal')}</h4>
                  <p className="text-sm text-green-800 mb-3">
                    {t('grievanceRedressalDesc')}
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

      {/* Camera Modal */}
      {showCamera && (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center gap-2">
                <Camera className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold text-lg">{t('scanDocument')}</h3>
              </div>
              <button
                onClick={stopCamera}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="relative bg-black min-h-[400px]">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-auto max-h-[60vh] min-h-[400px] object-cover"
                onLoadedMetadata={(e) => {
                  console.log('Video metadata loaded');
                  e.target.play();
                }}
              />
              
              {/* Loading indicator when stream is connecting */}
              {!cameraStream && (
                <div className="absolute inset-0 flex items-center justify-center bg-black">
                  <div className="text-center text-white">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2" />
                    <p>{t('connectingToCamera')}</p>
                  </div>
                </div>
              )}
              
              {/* Capture Guide Overlay */}
              {cameraStream && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="border-2 border-white/50 border-dashed rounded-lg w-4/5 h-3/4 flex items-center justify-center">
                    <span className="text-white bg-black/50 px-4 py-2 rounded-full text-sm">
                      {t('positionDocumentInFrame')}
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-gray-50">
              <div className="flex items-center justify-between mb-3">
                <p className="text-sm text-gray-600">
                  {t('ensureDocumentClear')}
                </p>
                <Button
                  onClick={captureImage}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
                >
                  <Camera className="w-4 h-4" />
                  {t('captureAndProcess')}
                </Button>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <Scan className="w-4 h-4" />
                <span>{t('aiWillExtract')}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Hidden Canvas for Image Processing */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default CitizenPortal;