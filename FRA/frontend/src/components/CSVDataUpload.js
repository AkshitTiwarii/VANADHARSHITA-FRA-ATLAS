import React, { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Upload, FileText, AlertCircle, CheckCircle, XCircle, Eye, Download } from 'lucide-react';

const CSVDataUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedDatasetType, setSelectedDatasetType] = useState('');
  const [validationResults, setValidationResults] = useState({});
  const [uploading, setUploading] = useState(false);
  const [validating, setValidating] = useState({});

  const datasetTypes = [
    { value: 'panchayat_data', label: 'Gram Panchayat Data' },
    { value: 'forest_land_records', label: 'Forest Land Records' },
    { value: 'tribal_demographics', label: 'Tribal Demographics' },
    { value: 'land_ownership', label: 'Land Ownership Records' },
    { value: 'forest_rights_claims', label: 'Forest Rights Claims' },
    { value: 'village_boundaries', label: 'Village Boundary Data' },
    { value: 'government_schemes', label: 'Government Schemes Data' },
    { value: 'satellite_imagery_meta', label: 'Satellite Imagery Metadata' },
    { value: 'environmental_data', label: 'Environmental Monitoring Data' },
    { value: 'socioeconomic_survey', label: 'Socioeconomic Survey Data' }
  ];

  const handleFileUpload = useCallback(async (event) => {
    const files = Array.from(event.target.files);
    if (!selectedDatasetType) {
      alert('Please select a dataset type first');
      return;
    }

    setUploading(true);
    
    for (const file of files) {
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        alert(`${file.name} is not a CSV file`);
        continue;
      }

      const fileInfo = {
        id: Date.now() + Math.random(),
        name: file.name,
        size: file.size,
        type: selectedDatasetType,
        uploadedAt: new Date(),
        status: 'uploaded',
        file: file
      };

      setUploadedFiles(prev => [...prev, fileInfo]);
      
      // Start validation automatically
      await validateFile(fileInfo);
    }
    
    setUploading(false);
    event.target.value = ''; // Reset input
  }, [selectedDatasetType]);

  const validateFile = async (fileInfo) => {
    setValidating(prev => ({ ...prev, [fileInfo.id]: true }));
    
    try {
      const formData = new FormData();
      formData.append('file', fileInfo.file);
      formData.append('dataset_type', fileInfo.type);

      const response = await fetch('/api/data/validate-csv', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      setValidationResults(prev => ({
        ...prev,
        [fileInfo.id]: result
      }));

      // Update file status
      setUploadedFiles(prev =>
        prev.map(f =>
          f.id === fileInfo.id
            ? { ...f, status: 'validated', validationId: result.id }
            : f
        )
      );
    } catch (error) {
      console.error('Validation error:', error);
      setValidationResults(prev => ({
        ...prev,
        [fileInfo.id]: {
          validation_status: 'fail',
          confidence_score: 0,
          issues_found: ['Validation failed'],
          record_count: 0
        }
      }));
    } finally {
      setValidating(prev => ({ ...prev, [fileInfo.id]: false }));
    }
  };

  const downloadSampleData = (datasetType) => {
    // Generate sample CSV based on dataset type
    let sampleData = '';
    
    switch (datasetType) {
      case 'panchayat_data':
        sampleData = 'panchayat_id,panchayat_name,block,district,state,population,households,area_hectares\n' +
                    'PAN001,Ramgarh GP,Ramgarh Block,Surguja,Chhattisgarh,2500,450,1200.5\n' +
                    'PAN002,Kharsia GP,Kharsia Block,Raigarh,Chhattisgarh,1800,320,890.2';
        break;
      case 'forest_rights_claims':
        sampleData = 'claim_id,beneficiary_name,village,block,district,claim_type,area_claimed,status,submission_date\n' +
                    'FRC001,Ram Singh,Chandrapur,Chandrapur Block,Chandrapur,Individual,2.5,pending,2024-01-15\n' +
                    'FRC002,Village Committee,Gadchiroli,Gadchiroli Block,Gadchiroli,Community,50.0,approved,2024-01-20';
        break;
      case 'tribal_demographics':
        sampleData = 'village_id,village_name,total_population,tribal_population,scheduled_tribe_households,literacy_rate\n' +
                    'VIL001,Bastar Village,1200,980,180,45.2\n' +
                    'VIL002,Kondagaon Village,850,720,140,38.7';
        break;
      default:
        sampleData = 'column1,column2,column3\nvalue1,value2,value3\nvalue4,value5,value6';
    }

    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${datasetType}_sample.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const getStatusIcon = (status, validationResult) => {
    if (status === 'uploaded') return <Upload className="w-4 h-4 text-blue-500" />;
    if (!validationResult) return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    
    if (validationResult.validation_status === 'pass') {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else if (validationResult.validation_status === 'fail') {
      return <XCircle className="w-4 h-4 text-red-500" />;
    } else {
      return <AlertCircle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status, validationResult) => {
    if (status === 'uploaded') {
      return <Badge className="bg-blue-100 text-blue-800">Uploaded</Badge>;
    }
    
    if (!validationResult) {
      return <Badge className="bg-yellow-100 text-yellow-800">Validating...</Badge>;
    }
    
    const statusConfig = {
      'pass': { color: 'bg-green-100 text-green-800', text: 'Valid Data' },
      'fail': { color: 'bg-red-100 text-red-800', text: 'Issues Found' },
      'pending': { color: 'bg-yellow-100 text-yellow-800', text: 'Review Needed' }
    };
    
    const config = statusConfig[validationResult.validation_status] || { 
      color: 'bg-gray-100 text-gray-800', 
      text: 'Unknown' 
    };
    
    return <Badge className={config.color}>{config.text}</Badge>;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="w-5 h-5" />
            Upload CSV Datasets
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Dataset Type</label>
              <Select value={selectedDatasetType} onValueChange={setSelectedDatasetType}>
                <SelectTrigger>
                  <SelectValue placeholder="Select dataset type" />
                </SelectTrigger>
                <SelectContent>
                  {datasetTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex items-end gap-2">
              <Button
                variant="outline"
                onClick={() => selectedDatasetType && downloadSampleData(selectedDatasetType)}
                disabled={!selectedDatasetType}
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download Sample
              </Button>
            </div>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              multiple
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              id="csv-upload"
              disabled={!selectedDatasetType || uploading}
            />
            <label
              htmlFor="csv-upload"
              className={`cursor-pointer ${
                !selectedDatasetType || uploading ? 'cursor-not-allowed opacity-50' : ''
              }`}
            >
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg font-medium text-gray-900 mb-2">
                {uploading ? 'Uploading...' : 'Choose CSV files to upload'}
              </p>
              <p className="text-sm text-gray-600">
                {selectedDatasetType 
                  ? `Upload ${datasetTypes.find(t => t.value === selectedDatasetType)?.label} files`
                  : 'Select a dataset type first'
                }
              </p>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Uploaded Files & Validation Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {uploadedFiles.map((file) => {
                const validationResult = validationResults[file.id];
                const isValidating = validating[file.id];
                
                return (
                  <div key={file.id} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {getStatusIcon(file.status, validationResult)}
                        <div>
                          <div className="font-medium">{file.name}</div>
                          <div className="text-sm text-gray-600">
                            {datasetTypes.find(t => t.value === file.type)?.label} • {formatFileSize(file.size)}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        {isValidating ? (
                          <Badge className="bg-blue-100 text-blue-800">Validating...</Badge>
                        ) : (
                          getStatusBadge(file.status, validationResult)
                        )}
                      </div>
                    </div>

                    {validationResult && (
                      <div className="bg-gray-50 rounded p-3 space-y-2">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Records:</span>
                            <div className="font-medium">{validationResult.record_count?.toLocaleString()}</div>
                          </div>
                          <div>
                            <span className="text-gray-600">Confidence:</span>
                            <div className="font-medium text-blue-600">
                              {(validationResult.confidence_score * 100)?.toFixed(1)}%
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Issues:</span>
                            <div className="font-medium text-red-600">
                              {validationResult.issues_found?.length || 0}
                            </div>
                          </div>
                          <div>
                            <span className="text-gray-600">Quality:</span>
                            <div className={`font-medium ${
                              validationResult.validation_status === 'pass' 
                                ? 'text-green-600' 
                                : 'text-red-600'
                            }`}>
                              {validationResult.validation_status === 'pass' ? 'Good' : 'Poor'}
                            </div>
                          </div>
                        </div>

                        {validationResult.issues_found?.length > 0 && (
                          <div className="space-y-1">
                            <span className="text-sm font-medium text-gray-700">Issues Found:</span>
                            <div className="flex flex-wrap gap-1">
                              {validationResult.issues_found.map((issue, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {issue}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex items-center gap-2"
                          >
                            <Eye className="w-3 h-3" />
                            Inspect Data
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CSVDataUpload;