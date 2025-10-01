import React, { useState, useCallback, useEffect } from 'react';
import { GoogleMap, LoadScript, Marker, InfoWindow, Circle } from '@react-google-maps/api';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  Satellite,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus,
  Loader2,
  X,
  RefreshCw,
  Download,
  AlertTriangle,
  CheckCircle,
  Eye,
  ArrowLeft,
  Home
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

// Load API keys from environment variables (secure!)
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
const AI_SERVICE_URL = process.env.REACT_APP_AI_SERVICE_URL || 'http://localhost:8000';

const containerStyle = {
  width: '100%',
  height: '100%',
  minHeight: '600px'
};

const ForestAtlasGoogleMaps = () => {
  const navigate = useNavigate();
  const [map, setMap] = useState(null);
  const [center, setCenter] = useState({ lat: 18.9217285, lng: 77.0038332 }); // Maharashtra, India
  const [zoom, setZoom] = useState(14);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showAnalysisPanel, setShowAnalysisPanel] = useState(false);
  const [analysisRadius, setAnalysisRadius] = useState(500); // meters
  
  // Debug: Check if API key is loaded
  useEffect(() => {
    console.log('Google Maps API Key loaded:', GOOGLE_MAPS_API_KEY ? 'Yes ✓' : 'No ✗');
    console.log('API Key length:', GOOGLE_MAPS_API_KEY?.length || 0);
    if (!GOOGLE_MAPS_API_KEY) {
      toast.error('Google Maps API key is missing! Check your .env file.');
    }
  }, []);
  
  const onLoad = useCallback((map) => {
    setMap(map);
  }, []);

  const onUnmount = useCallback(() => {
    setMap(null);
  }, []);

  // Handle map click to analyze location
  const handleMapClick = async (event) => {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    
    setSelectedLocation({ lat, lng });
    await analyzeSatellite(lat, lng);
  };

  // Perform satellite analysis
  const analyzeSatellite = async (lat, lng, radius = analysisRadius) => {
    setLoading(true);
    setShowAnalysisPanel(true);
    
    try {
      console.log('🛰️ Sending request to:', `${AI_SERVICE_URL}/api/analyze-satellite`);
      console.log('📍 Coordinates:', { latitude: lat, longitude: lng, radius });
      
      const response = await axios.post(`${AI_SERVICE_URL}/api/analyze-satellite`, {
        latitude: lat,
        longitude: lng,
        radius: radius
      });

      console.log('✅ Raw API response:', response.data);

      // Check if response is successful (API returns "success": true)
      if (response.data.success) {
        // Transform API response to match frontend expectations
        const transformedData = {
          status: 'success',
          location: {
            latitude: response.data.coordinates.lat,
            longitude: response.data.coordinates.lon,
            radius_meters: radius
          },
          analysis: {
            vegetation_index: response.data.ndvi.value,
            vegetation_health: response.data.ndvi.health,
            forest_cover_percentage: response.data.land_cover.forest_cover_percentage,
            primary_land_type: response.data.land_cover.primary_type,
            is_forest: response.data.land_cover.is_forest,
            // Keep nested structure for compatibility with UI
            land_cover: {
              primary_type: response.data.land_cover.primary_type,
              forest_type: response.data.land_cover.is_forest ? 'Forest Area' : 'Non-Forest',
              confidence: response.data.land_cover.classification_confidence || 'Medium',
              is_forest: response.data.land_cover.is_forest
            },
            change_detection: {
              deforestation_risk: response.data.change_detection.deforestation_risk,
              trend: response.data.change_detection.trend,
              last_6_months_change: response.data.change_detection.change_percentage || 0,
              encroachment_detected: response.data.change_detection.encroachment_detected,
              vegetation_loss: response.data.change_detection.vegetation_loss
            }
          },
          land_classification: response.data.land_classification,
          change_detection: response.data.change_detection,
          recommendations: response.data.recommendations,
          data_quality: response.data.data_quality,
          metadata: {
            analysis_date: response.data.analysis_date,
            date_range: response.data.date_range,
            imagery_count: response.data.imagery_count,
            data_source: response.data.data_source
          }
        };

        console.log('🔄 Transformed data:', transformedData);
        setAnalysisResult(transformedData);
        
        // Show success toast with quick stats
        const ndvi = transformedData.analysis.vegetation_index;
        const forestCover = transformedData.analysis.forest_cover_percentage;
        toast.success(
          `Analysis Complete! NDVI: ${ndvi.toFixed(2)}, Forest: ${forestCover.toFixed(1)}%`
        );
      } else {
        throw new Error('Analysis failed - API returned unsuccessful response');
      }
    } catch (error) {
      console.error('❌ Satellite analysis error:', error);
      console.error('Error details:', error.response?.data || error.message);
      
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      toast.error(`Failed to analyze location: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  // Get NDVI color based on value
  const getNDVIColor = (ndvi) => {
    if (ndvi >= 0.7) return '#22c55e'; // Green - Healthy
    if (ndvi >= 0.5) return '#84cc16'; // Light green - Moderate
    if (ndvi >= 0.3) return '#eab308'; // Yellow - Sparse
    if (ndvi >= 0.1) return '#f97316'; // Orange - Very sparse
    return '#ef4444'; // Red - No vegetation
  };

  // Get risk color
  const getRiskColor = (risk) => {
    if (risk === 'low') return 'green';
    if (risk === 'medium') return 'yellow';
    return 'red';
  };

  // Get confidence color
  const getConfidenceColor = (confidence) => {
    if (confidence === 'high') return 'green';
    if (confidence === 'medium') return 'yellow';
    return 'orange';
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header with Back Button */}
      <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          {/* Back Button */}
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(-1)}
              className="flex items-center gap-2 hover:bg-gray-100"
              title="Go back"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/dashboard')}
              className="flex items-center gap-2 hover:bg-gray-100"
              title="Go to dashboard"
            >
              <Home className="w-4 h-4" />
              Home
            </Button>
          </div>
          
          <div className="border-l border-gray-300 pl-4">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Satellite className="w-6 h-6 text-blue-600" />
              Forest Atlas - Satellite Analysis
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Click anywhere on the map to analyze vegetation and forest cover
            </p>
          </div>
        </div>
        
        {selectedLocation && (
          <div className="text-right">
            <div className="text-sm text-gray-600">Selected Location</div>
            <div className="font-mono text-sm">
              {selectedLocation.lat.toFixed(6)}°N, {selectedLocation.lng.toFixed(6)}°E
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Map Container */}
        <div className="flex-1 relative">
          {!GOOGLE_MAPS_API_KEY ? (
            <div className="flex items-center justify-center h-full bg-gray-100">
              <div className="text-center p-8 bg-white rounded-lg shadow-lg max-w-md">
                <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                <h2 className="text-xl font-bold text-gray-900 mb-2">Google Maps API Key Missing</h2>
                <p className="text-gray-600 mb-4">
                  The Google Maps API key is not configured. Please check your .env file.
                </p>
                <div className="text-left bg-gray-50 p-4 rounded text-sm">
                  <p className="font-mono text-xs mb-2">Check: frontend-main/.env</p>
                  <p className="font-mono text-xs">
                    REACT_APP_GOOGLE_MAPS_API_KEY=your_key_here
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <LoadScript 
              googleMapsApiKey={GOOGLE_MAPS_API_KEY}
              loadingElement={<div className="flex items-center justify-center h-full">Loading Google Maps...</div>}
            >
              <GoogleMap
                mapContainerStyle={containerStyle}
                center={center}
                zoom={zoom}
                onClick={handleMapClick}
                onLoad={onLoad}
                onUnmount={onUnmount}
                options={{
                mapTypeId: 'hybrid', // Satellite view with labels
                mapTypeControl: true,
                mapTypeControlOptions: {
                  style: window.google?.maps?.MapTypeControlStyle?.HORIZONTAL_BAR,
                  position: window.google?.maps?.ControlPosition?.TOP_RIGHT,
                  mapTypeIds: ['roadmap', 'satellite', 'hybrid', 'terrain']
                },
                streetViewControl: false,
                fullscreenControl: true,
                zoomControl: true,
              }}
            >
              {/* Selected location marker */}
              {selectedLocation && (
                <>
                  <Marker
                    position={selectedLocation}
                    icon={{
                      path: window.google?.maps?.SymbolPath?.CIRCLE,
                      scale: 8,
                      fillColor: '#3b82f6',
                      fillOpacity: 1,
                      strokeWeight: 2,
                      strokeColor: '#ffffff',
                    }}
                  />
                  
                  {/* Analysis radius circle */}
                  <Circle
                    center={selectedLocation}
                    radius={analysisRadius}
                    options={{
                      fillColor: analysisResult 
                        ? getNDVIColor(analysisResult.analysis?.vegetation_index)
                        : '#3b82f6',
                      fillOpacity: 0.2,
                      strokeColor: analysisResult 
                        ? getNDVIColor(analysisResult.analysis?.vegetation_index)
                        : '#3b82f6',
                      strokeOpacity: 0.8,
                      strokeWeight: 2,
                    }}
                  />
                </>
              )}
            </GoogleMap>
          </LoadScript>
          )}

          {/* Loading overlay */}
          {loading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
              <div className="bg-white rounded-lg p-6 flex flex-col items-center gap-3">
                <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
                <p className="text-gray-700 font-medium">Analyzing satellite data...</p>
                <p className="text-sm text-gray-500">Fetching NDVI and land cover data</p>
              </div>
            </div>
          )}
        </div>

        {/* Analysis Panel */}
        {showAnalysisPanel && (
          <div className="w-96 bg-white border-l shadow-lg overflow-y-auto">
            <div className="sticky top-0 bg-white border-b p-4 flex items-center justify-between z-10">
              <h2 className="font-bold text-lg flex items-center gap-2">
                <Satellite className="w-5 h-5 text-blue-600" />
                Analysis Results
              </h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAnalysisPanel(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>

            {analysisResult && (
              <div className="p-4 space-y-4">
                {/* Location Info */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      Location
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Latitude:</span>
                      <span className="font-mono">{analysisResult.location.latitude.toFixed(6)}°N</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Longitude:</span>
                      <span className="font-mono">{analysisResult.location.longitude.toFixed(6)}°E</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Radius:</span>
                      <span className="font-mono">{analysisResult.location.radius_meters}m</span>
                    </div>
                    {analysisResult.metadata && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Region:</span>
                          <span className="font-medium">{analysisResult.metadata.region}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Season:</span>
                          <span className="font-medium">{analysisResult.metadata.season}</span>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* NDVI Analysis */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center justify-between">
                      <span className="flex items-center gap-2">
                        <Eye className="w-4 h-4" />
                        Vegetation Health (NDVI)
                      </span>
                      <Badge
                        style={{
                          backgroundColor: getNDVIColor(analysisResult.analysis.vegetation_index),
                          color: 'white'
                        }}
                      >
                        {analysisResult.analysis.vegetation_index.toFixed(3)}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {/* NDVI Bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-gray-600">
                        <span>No Vegetation</span>
                        <span>Dense Forest</span>
                      </div>
                      <div className="h-6 bg-gradient-to-r from-red-500 via-yellow-500 via-green-400 to-green-600 rounded-full relative">
                        <div
                          className="absolute h-full w-1 bg-white border-2 border-gray-900 rounded-full"
                          style={{
                            left: `${(analysisResult.analysis.vegetation_index * 100)}%`,
                            transform: 'translateX(-50%)'
                          }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>0.0</span>
                        <span>0.5</span>
                        <span>1.0</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Health Status:</span>
                        <Badge variant="outline">
                          {analysisResult.analysis.vegetation_health}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Forest Cover:</span>
                        <span className="font-bold text-green-700">
                          {analysisResult.analysis.forest_cover_percentage.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Land Cover Classification */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm">Land Cover Classification</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Primary Type:</span>
                        <Badge variant="secondary">
                          {analysisResult.analysis.land_cover.primary_type}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Forest Type:</span>
                        <span className="font-medium">
                          {analysisResult.analysis.land_cover.forest_type}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Confidence:</span>
                        <Badge
                          variant={getConfidenceColor(analysisResult.analysis.land_cover.confidence)}
                        >
                          {analysisResult.analysis.land_cover.confidence}
                        </Badge>
                      </div>
                    </div>

                    {/* Detailed breakdown */}
                    {analysisResult.analysis.classification && (
                      <div className="mt-3 pt-3 border-t space-y-2">
                        <p className="text-xs font-medium text-gray-700">Breakdown:</p>
                        {Object.entries(analysisResult.analysis.classification).map(([key, value]) => (
                          <div key={key} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-600 capitalize">
                                {key.replace(/_/g, ' ')}
                              </span>
                              <span className="font-medium">{value.toFixed(1)}%</span>
                            </div>
                            <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-green-500"
                                style={{ width: `${value}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Change Detection */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center justify-between">
                      <span>Change Detection</span>
                      <Badge
                        variant={getRiskColor(analysisResult.analysis.change_detection.deforestation_risk)}
                      >
                        {analysisResult.analysis.change_detection.deforestation_risk} risk
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Trend:</span>
                      <span className="flex items-center gap-1 font-medium">
                        {analysisResult.analysis.change_detection.trend === 'increasing' && (
                          <TrendingUp className="w-4 h-4 text-green-600" />
                        )}
                        {analysisResult.analysis.change_detection.trend === 'decreasing' && (
                          <TrendingDown className="w-4 h-4 text-red-600" />
                        )}
                        {analysisResult.analysis.change_detection.trend === 'stable' && (
                          <Minus className="w-4 h-4 text-gray-600" />
                        )}
                        {analysisResult.analysis.change_detection.trend}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">6-Month Change:</span>
                      <span className={`font-bold ${
                        analysisResult.analysis.change_detection.last_6_months_change > 0
                          ? 'text-green-600'
                          : analysisResult.analysis.change_detection.last_6_months_change < 0
                          ? 'text-red-600'
                          : 'text-gray-600'
                      }`}>
                        {analysisResult.analysis.change_detection.last_6_months_change > 0 && '+'}
                        {analysisResult.analysis.change_detection.last_6_months_change.toFixed(1)}%
                      </span>
                    </div>

                    {analysisResult.analysis.change_detection.deforestation_risk !== 'low' && (
                      <div className="mt-3 p-2 bg-orange-50 border border-orange-200 rounded flex gap-2">
                        <AlertTriangle className="w-4 h-4 text-orange-600 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-orange-800">
                          This area shows signs of vegetation decline. Consider monitoring closely.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Recommendations */}
                {analysisResult.analysis.recommendations && (
                  <Card>
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm">FRA Recommendations</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {analysisResult.analysis.recommendations.map((rec, idx) => (
                          <li key={idx} className="flex gap-2 text-sm">
                            <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
                            <span className="text-gray-700">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                {/* Data Source Info */}
                {analysisResult.metadata && (
                  <Card className="bg-blue-50 border-blue-200">
                    <CardContent className="pt-4">
                      <div className="flex items-start gap-2">
                        <Satellite className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div className="text-xs text-blue-800 space-y-1">
                          <p className="font-medium">Data Quality: {analysisResult.metadata.data_quality}</p>
                          {analysisResult.metadata.data_quality === 'enhanced_fallback' && (
                            <p>
                              Using geographic analysis. 
                              <a
                                href="https://code.earthengine.google.com/register"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="underline ml-1"
                              >
                                Register GEE for real satellite data
                              </a>
                            </p>
                          )}
                          {analysisResult.metadata.data_quality === 'satellite' && (
                            <p>Using real Sentinel-2 satellite imagery (10m resolution)</p>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => selectedLocation && analyzeSatellite(selectedLocation.lat, selectedLocation.lng)}
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Re-analyze
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => {
                      const data = JSON.stringify(analysisResult, null, 2);
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `satellite-analysis-${Date.now()}.json`;
                      a.click();
                    }}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </div>
              </div>
            )}

            {!analysisResult && !loading && (
              <div className="p-8 text-center text-gray-500">
                <Satellite className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                <p className="text-sm">Click anywhere on the map to analyze satellite data</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ForestAtlasGoogleMaps;
