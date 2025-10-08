import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import {
  AlertTriangle,
  CheckCircle,
  TrendingDown,
  Satellite,
  MapPin,
  Calendar,
  Phone,
  Mail,
  RefreshCw,
  Play,
  Bell,
  Loader2,
  Eye,
  Download,
  Filter,
  ArrowLeft,
  Map as MapIcon,
  TreePine,
  Waves,
  Settings
} from 'lucide-react';
import { GoogleMap, LoadScript, Marker, InfoWindow, Circle, Polygon } from '@react-google-maps/api';
import axios from 'axios';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import ManageLocationsModal from './ManageLocationsModal';

const AI_SERVICE_URL = process.env.REACT_APP_AI_SERVICE_URL || 'http://localhost:8000';
const GOOGLE_MAPS_API_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

const mapContainerStyle = {
  width: '100%',
  height: '600px'
};

const mapOptions = {
  mapTypeId: 'hybrid', // Show satellite + labels
  zoomControl: true,
  streetViewControl: false,
  fullscreenControl: true,
  mapTypeControl: true,
  mapTypeControlOptions: {
    style: window.google?.maps?.MapTypeControlStyle?.HORIZONTAL_BAR,
    position: window.google?.maps?.ControlPosition?.TOP_RIGHT,
  }
};

const ForestMonitoringDashboard = () => {
  const navigate = useNavigate();
  const mapRef = useRef(null); // Reference to map section
  const [alerts, setAlerts] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFilter, setSelectedFilter] = useState('all'); // all, high, medium, low
  const [showManageLocations, setShowManageLocations] = useState(false);
  
  // Map state
  const [showMap, setShowMap] = useState(false);
  const [mapCenter, setMapCenter] = useState({ lat: 21.1458, lng: 79.0882 }); // Central India
  const [mapZoom, setMapZoom] = useState(6);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [clickedLocation, setClickedLocation] = useState(null);
  const [locationDetails, setLocationDetails] = useState(null);
  const [loadingLocationDetails, setLoadingLocationDetails] = useState(false);
  
  // Fetch alerts on component mount
  useEffect(() => {
    fetchAlerts();
    fetchStatistics();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchAlerts();
      fetchStatistics();
    }, 300000); // 5 minutes
    
    return () => clearInterval(interval);
  }, []);
  
  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/api/monitoring/alerts?limit=100`);
      if (response.data.success) {
        setAlerts(response.data.alerts || []);
      }
    } catch (error) {
      console.error('Error fetching alerts:', error);
      toast.error('Failed to fetch alerts');
    }
  };
  
  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/api/monitoring/statistics`);
      if (response.data.success) {
        setStatistics(response.data.statistics);
      }
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };
  
  const runMonitoringCycle = async () => {
    setLoading(true);
    try {
      toast.info('🛰️ Starting forest monitoring cycle...');
      const response = await axios.post(`${AI_SERVICE_URL}/api/monitoring/run-cycle`);
      
      if (response.data.success) {
        const { villages_analyzed, alerts_generated } = response.data;
        toast.success(`✅ Analyzed ${villages_analyzed} villages. Generated ${alerts_generated} alerts.`);
        
        // Refresh data
        await fetchAlerts();
        await fetchStatistics();
      }
    } catch (error) {
      console.error('Error running monitoring cycle:', error);
      toast.error('Failed to run monitoring cycle');
    } finally {
      setLoading(false);
    }
  };
  
  const sendTestAlert = async () => {
    try {
      toast.info('📧 Sending test alert...');
      const response = await axios.post(`${AI_SERVICE_URL}/api/monitoring/test-alert`);
      
      if (response.data.success) {
        toast.success('✅ Test alert sent successfully!');
      }
    } catch (error) {
      console.error('Error sending test alert:', error);
      toast.error('Failed to send test alert');
    }
  };
  
  const getRiskColor = (risk) => {
    switch (risk) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'medium':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'low':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };
  
  const getRiskBadgeColor = (risk) => {
    switch (risk) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'warning';
      case 'low':
        return 'secondary';
      default:
        return 'default';
    }
  };
  
  const getMarkerIcon = (risk) => {
    const colors = {
      high: '#dc2626',    // red
      medium: '#ea580c',  // orange
      low: '#eab308'      // yellow
    };
    
    return {
      path: window.google?.maps?.SymbolPath?.CIRCLE,
      scale: 10,
      fillColor: colors[risk] || '#gray',
      fillOpacity: 0.8,
      strokeColor: '#ffffff',
      strokeWeight: 2
    };
  };
  
  const handleMapClick = async (event) => {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    
    setClickedLocation({ lat, lng });
    setLoadingLocationDetails(true);
    
    try {
      // Fetch vegetation and forest data for clicked location using satellite analysis
      const response = await axios.post(`${AI_SERVICE_URL}/api/analyze-satellite`, {
        latitude: lat,
        longitude: lng,
        radius: 500
      });
      
      // Transform satellite data to expected format
      const satelliteData = response.data;
      const transformedData = {
        ndvi: satelliteData.ndvi || 0.0,
        forest_type: satelliteData.land_cover_type || 'Forest',
        tree_cover_percentage: satelliteData.tree_cover_percentage || 0,
        water_bodies_nearby: (satelliteData.land_cover_type && 
          satelliteData.land_cover_type.toLowerCase().includes('water')) || false,
        vegetation_density: satelliteData.ndvi > 0.7 ? '🌲 Dense Vegetation' :
                           satelliteData.ndvi > 0.5 ? '🌳 Moderate Vegetation' :
                           satelliteData.ndvi > 0.3 ? '🌾 Sparse Vegetation' : '🏜️ Barren',
        carbon_stock_tonnes_per_ha: Math.round(satelliteData.tree_cover_percentage * 1.8),
        soil_moisture_index: satelliteData.ndvi * 0.7 + 0.2
      };
      
      setLocationDetails(transformedData);
      toast.success('🛰️ Location analyzed via satellite!');
      
    } catch (error) {
      console.error('Error analyzing location:', error);
      toast.error('Failed to analyze location');
      setLocationDetails(null);
    } finally {
      setLoadingLocationDetails(false);
    }
  };
  
  const handleAlertMarkerClick = (alert) => {
    setSelectedAlert(alert);
    setMapCenter({ lat: alert.latitude, lng: alert.longitude });
    setMapZoom(12);
  };
  
  const toggleMapView = () => {
    setShowMap(!showMap);
    if (!showMap && filteredAlerts.length > 0) {
      // Center on first alert
      const firstAlert = filteredAlerts[0];
      setMapCenter({ lat: firstAlert.latitude, lng: firstAlert.longitude });
      setMapZoom(8);
    }
  };
  
  const filteredAlerts = alerts.filter(alert => {
    if (selectedFilter === 'all') return true;
    return alert.deforestation_risk === selectedFilter;
  });
  
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-3 sm:p-4 md:p-6">
      {/* Header */}
      <div className="mb-6 sm:mb-8 space-y-4">
        {/* Back Button */}
        <div>
          <Button
            variant="outline"
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-xs sm:text-sm"
          >
            <ArrowLeft className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Back to Dashboard</span>
            <span className="sm:hidden">Back</span>
          </Button>
        </div>
        
        {/* Title and Actions Row */}
        <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h1 className="text-xl sm:text-2xl md:text-3xl font-bold text-gray-900 flex items-center gap-2 sm:gap-3">
              <Satellite className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-blue-600 flex-shrink-0" />
              <span className="truncate">Forest Monitoring Dashboard</span>
            </h1>
            <p className="text-xs sm:text-sm md:text-base text-gray-600 mt-1 sm:mt-2">
              Real-time deforestation detection using satellite imagery
            </p>
          </div>
          
          <div className="flex flex-wrap gap-2 items-start w-full sm:w-auto">
            <Button
              variant="default"
              onClick={() => setShowManageLocations(true)}
              className="bg-green-600 hover:bg-green-700 text-xs sm:text-sm flex-1 sm:flex-initial"
            >
              <Settings className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              <span className="hidden sm:inline">Manage Locations</span>
              <span className="sm:hidden">Manage</span>
            </Button>
            
            <Button
              variant={showMap ? 'default' : 'outline'}
              onClick={toggleMapView}
              className={`${showMap ? 'bg-green-600 hover:bg-green-700' : ''} text-xs sm:text-sm flex-1 sm:flex-initial`}
            >
              <MapIcon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              {showMap ? 'Hide' : 'Show'} Map
            </Button>
            
            <Button
              variant="outline"
              onClick={fetchAlerts}
              disabled={loading}
              className="text-xs sm:text-sm"
            >
              <RefreshCw className={`w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 ${loading ? 'animate-spin' : ''}`} />
              <span className="hidden sm:inline">Refresh</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={sendTestAlert}
              className="text-xs sm:text-sm hidden md:flex"
            >
              <Bell className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              Test Alert
            </Button>
            
            <Button
              onClick={runMonitoringCycle}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-xs sm:text-sm flex-1 sm:flex-initial"
            >
              {loading ? (
                <>
                  <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 animate-spin" />
                  <span className="hidden sm:inline">Analyzing...</span>
                  <span className="sm:hidden">...</span>
                </>
              ) : (
                <>
                  <Play className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden sm:inline">Run Monitoring Cycle</span>
                  <span className="sm:hidden">Run</span>
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
      
      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <Card className="border-l-4 border-l-gray-500">
            <CardHeader className="pb-2 sm:pb-3 p-3 sm:p-4">
              <CardTitle className="text-xs sm:text-sm font-medium text-gray-600 truncate">
                Total Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {statistics.total_alerts || 0}
              </div>
              <p className="text-xs text-gray-500 mt-1">
                All time detections
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-l-4 border-l-red-500 bg-red-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-red-800 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                High Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-700">
                {statistics.high_risk_count || 0}
              </div>
              <p className="text-xs text-red-600 mt-1">
                Immediate action required
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-l-4 border-l-orange-500 bg-orange-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-orange-800">
                Medium Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-700">
                {statistics.medium_risk_count || 0}
              </div>
              <p className="text-xs text-orange-600 mt-1">
                Monitor closely
              </p>
            </CardContent>
          </Card>
          
          <Card className="border-l-4 border-l-yellow-500 bg-yellow-50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-yellow-800">
                Low Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-700">
                {statistics.low_risk_count || 0}
              </div>
              <p className="text-xs text-yellow-600 mt-1">
                Routine monitoring
              </p>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Interactive Map View */}
      {showMap && (
        <Card className="mb-8" ref={mapRef}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapIcon className="w-5 h-5 text-green-600" />
              Interactive Forest Map
              <Badge variant="secondary" className="ml-2">
                Click anywhere to analyze vegetation
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!GOOGLE_MAPS_API_KEY ? (
              <div className="p-8 bg-yellow-50 border-2 border-yellow-200 rounded-lg text-center">
                <AlertTriangle className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
                <h3 className="text-lg font-bold text-gray-900 mb-2">Google Maps API Key Missing</h3>
                <p className="text-gray-600 mb-4">
                  Please configure your Google Maps API key in the .env file to use the interactive map.
                </p>
                <code className="bg-gray-100 px-3 py-1 rounded text-sm">
                  REACT_APP_GOOGLE_MAPS_API_KEY=your_key_here
                </code>
              </div>
            ) : (
              <LoadScript googleMapsApiKey={GOOGLE_MAPS_API_KEY}>
                <GoogleMap
                  mapContainerStyle={mapContainerStyle}
                  center={mapCenter}
                  zoom={mapZoom}
                  options={mapOptions}
                  onClick={handleMapClick}
                >
                  {/* Alert Markers */}
                  {filteredAlerts.map((alert) => (
                    <Marker
                      key={alert.alert_id}
                      position={{ lat: alert.latitude, lng: alert.longitude }}
                      icon={getMarkerIcon(alert.deforestation_risk)}
                      onClick={() => handleAlertMarkerClick(alert)}
                    />
                  ))}
                  
                  {/* Selected Alert Info Window */}
                  {selectedAlert && (
                    <InfoWindow
                      position={{ lat: selectedAlert.latitude, lng: selectedAlert.longitude }}
                      onCloseClick={() => setSelectedAlert(null)}
                    >
                      <div className="p-2 max-w-sm">
                        <h3 className="font-bold text-lg mb-2">{selectedAlert.village_name}</h3>
                        <p className="text-sm text-gray-600 mb-2">
                          {selectedAlert.district}, {selectedAlert.state}
                        </p>
                        <div className="space-y-1 text-sm">
                          <div className="flex items-center gap-2">
                            <Badge variant={getRiskBadgeColor(selectedAlert.deforestation_risk)}>
                              {selectedAlert.deforestation_risk.toUpperCase()} RISK
                            </Badge>
                          </div>
                          <p>
                            <strong>NDVI:</strong> {selectedAlert.ndvi_previous.toFixed(3)} → {selectedAlert.ndvi_current.toFixed(3)}
                          </p>
                          <p>
                            <strong>Loss:</strong> {selectedAlert.vegetation_loss_percentage.toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatDate(selectedAlert.detection_date || selectedAlert.detected_at)}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          className="mt-3 w-full"
                          onClick={() => {
                            const element = document.getElementById(`alert-${selectedAlert.alert_id}`);
                            element?.scrollIntoView({ behavior: 'smooth' });
                            setSelectedAlert(null);
                          }}
                        >
                          View Details
                        </Button>
                      </div>
                    </InfoWindow>
                  )}
                  
                  {/* Clicked Location Marker */}
                  {clickedLocation && (
                    <>
                      <Marker
                        position={clickedLocation}
                        icon={{
                          path: window.google?.maps?.SymbolPath?.CIRCLE,
                          scale: 8,
                          fillColor: '#3b82f6',
                          fillOpacity: 0.9,
                          strokeColor: '#ffffff',
                          strokeWeight: 2
                        }}
                      />
                      
                      {locationDetails && (
                        <InfoWindow
                          position={clickedLocation}
                          onCloseClick={() => {
                            setClickedLocation(null);
                            setLocationDetails(null);
                          }}
                        >
                          <div className="p-3 max-w-md">
                            <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                              <TreePine className="w-5 h-5 text-green-600" />
                              Location Analysis
                            </h3>
                            
                            <div className="space-y-3">
                              {/* Coordinates */}
                              <div className="text-sm">
                                <p className="text-gray-600 font-medium mb-1">Coordinates:</p>
                                <p className="font-mono text-xs">
                                  {clickedLocation.lat.toFixed(6)}°N, {clickedLocation.lng.toFixed(6)}°E
                                </p>
                              </div>
                              
                              {/* NDVI */}
                              {locationDetails.ndvi !== undefined && (
                                <div className="bg-green-50 p-3 rounded-lg">
                                  <p className="text-sm font-medium text-green-800 mb-1">
                                    Vegetation Index (NDVI)
                                  </p>
                                  <p className="text-2xl font-bold text-green-700">
                                    {locationDetails.ndvi.toFixed(3)}
                                  </p>
                                  <p className="text-xs text-green-600 mt-1">
                                    {locationDetails.ndvi > 0.6 ? '🌲 Dense Vegetation' :
                                     locationDetails.ndvi > 0.3 ? '🌳 Moderate Vegetation' :
                                     locationDetails.ndvi > 0.1 ? '🌾 Sparse Vegetation' :
                                     '🏜️ Barren/Urban'}
                                  </p>
                                </div>
                              )}
                              
                              {/* Forest Type */}
                              {locationDetails.forest_type && (
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-1">Forest Type:</p>
                                  <Badge variant="outline">{locationDetails.forest_type}</Badge>
                                </div>
                              )}
                              
                              {/* Tree Cover */}
                              {locationDetails.tree_cover_percentage !== undefined && (
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-1">Tree Cover:</p>
                                  <div className="flex items-center gap-2">
                                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                                      <div
                                        className="bg-green-600 h-2 rounded-full"
                                        style={{ width: `${locationDetails.tree_cover_percentage}%` }}
                                      />
                                    </div>
                                    <span className="text-sm font-bold text-gray-900">
                                      {locationDetails.tree_cover_percentage.toFixed(1)}%
                                    </span>
                                  </div>
                                </div>
                              )}
                              
                              {/* Water Bodies */}
                              {locationDetails.water_bodies_nearby && (
                                <div className="flex items-center gap-2 text-sm text-blue-600">
                                  <Waves className="w-4 h-4" />
                                  <span>Water bodies detected nearby</span>
                                </div>
                              )}
                              
                              {/* Analysis Date */}
                              <p className="text-xs text-gray-500 mt-2">
                                Analyzed: {new Date().toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </InfoWindow>
                      )}
                      
                      {loadingLocationDetails && (
                        <InfoWindow
                          position={clickedLocation}
                          onCloseClick={() => setClickedLocation(null)}
                        >
                          <div className="p-3 text-center">
                            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
                            <p className="text-sm text-gray-600">Analyzing location...</p>
                          </div>
                        </InfoWindow>
                      )}
                    </>
                  )}
                  
                  {/* Deforestation Risk Circles */}
                  {filteredAlerts.map((alert) => (
                    <Circle
                      key={`circle-${alert.alert_id}`}
                      center={{ lat: alert.latitude, lng: alert.longitude }}
                      radius={alert.deforestation_risk === 'high' ? 2000 : alert.deforestation_risk === 'medium' ? 1500 : 1000}
                      options={{
                        strokeColor: alert.deforestation_risk === 'high' ? '#dc2626' : 
                                    alert.deforestation_risk === 'medium' ? '#ea580c' : '#eab308',
                        strokeOpacity: 0.6,
                        strokeWeight: 2,
                        fillColor: alert.deforestation_risk === 'high' ? '#dc2626' :
                                   alert.deforestation_risk === 'medium' ? '#ea580c' : '#eab308',
                        fillOpacity: 0.2,
                      }}
                    />
                  ))}
                </GoogleMap>
              </LoadScript>
            )}
            
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                How to use the map:
              </h4>
              <ul className="text-sm text-blue-800 space-y-1 ml-6 list-disc">
                <li><strong>Click alert markers</strong> to see deforestation details</li>
                <li><strong>Click anywhere on the map</strong> to analyze forest vegetation and get real-time NDVI data</li>
                <li><strong>Colored circles</strong> show affected area radius (red = high risk, orange = medium, yellow = low)</li>
                <li>Use <strong>map controls</strong> to switch between satellite and terrain views</li>
                <li>Click "View on Map" button in any alert card to jump to that location</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Filters */}
      <div className="mb-6 flex items-center gap-3">
        <Filter className="w-5 h-5 text-gray-600" />
        <span className="text-sm font-medium text-gray-700">Filter by risk:</span>
        
        <div className="flex gap-2">
          {['all', 'high', 'medium', 'low'].map((filter) => (
            <Button
              key={filter}
              variant={selectedFilter === filter ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedFilter(filter)}
              className="capitalize"
            >
              {filter === 'all' ? 'All Alerts' : `${filter} Risk`}
            </Button>
          ))}
        </div>
        
        <span className="ml-auto text-sm text-gray-600">
          Showing {filteredAlerts.length} of {alerts.length} alerts
        </span>
      </div>
      
      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No Alerts Found
              </h3>
              <p className="text-gray-600 mb-6">
                {selectedFilter === 'all' 
                  ? 'No deforestation detected. All monitored forests are healthy.'
                  : `No ${selectedFilter} risk alerts at this time.`}
              </p>
              <Button onClick={runMonitoringCycle} disabled={loading}>
                <Satellite className="w-4 h-4 mr-2" />
                Run Monitoring Cycle
              </Button>
            </CardContent>
          </Card>
        ) : (
          filteredAlerts.map((alert) => (
            <Card
              key={alert.alert_id}
              id={`alert-${alert.alert_id}`}
              className={`border-2 ${getRiskColor(alert.deforestation_risk)} hover:shadow-lg transition-shadow`}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">
                        {alert.village_name}
                      </h3>
                      <Badge variant={getRiskBadgeColor(alert.deforestation_risk)}>
                        {alert.deforestation_risk.toUpperCase()} RISK
                      </Badge>
                      <Badge variant="outline">
                        {alert.alert_id}
                      </Badge>
                    </div>
                    
                    {alert.district && (
                      <p className="text-sm text-gray-600">
                        {alert.district}, {alert.state}
                      </p>
                    )}
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm text-gray-600 flex items-center gap-1 justify-end">
                      <Calendar className="w-4 h-4" />
                      {formatDate(alert.detection_date || alert.detected_at)}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  {/* Location */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700 flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-600" />
                      Location
                    </div>
                    <div className="text-sm text-gray-600 font-mono">
                      {alert.latitude.toFixed(6)}°N
                      <br />
                      {alert.longitude.toFixed(6)}°E
                    </div>
                  </div>
                  
                  {/* NDVI Change */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700">
                      Vegetation Index (NDVI)
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-mono text-green-700">
                        {alert.ndvi_previous.toFixed(3)}
                      </span>
                      <TrendingDown className="w-4 h-4 text-red-600" />
                      <span className="text-sm font-mono text-red-700 font-bold">
                        {alert.ndvi_current.toFixed(3)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Previous → Current
                    </div>
                  </div>
                  
                  {/* Vegetation Loss */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700">
                      Vegetation Loss
                    </div>
                    <div className="text-3xl font-bold text-red-700">
                      {alert.vegetation_loss_percentage.toFixed(1)}%
                    </div>
                    <div className="text-xs text-gray-500">
                      Detected via satellite
                    </div>
                  </div>
                </div>
                
                {/* Contact Information */}
                {(alert.forest_officer_phone || alert.district_collector_email) && (
                  <div className="border-t pt-4 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {alert.forest_officer_phone && (
                        <div className="flex items-center gap-2 text-gray-700">
                          <Phone className="w-4 h-4 text-blue-600" />
                          <span className="font-medium">Forest Officer:</span>
                          <span className="font-mono">{alert.forest_officer_phone}</span>
                        </div>
                      )}
                      
                      {alert.district_collector_email && (
                        <div className="flex items-center gap-2 text-gray-700">
                          <Mail className="w-4 h-4 text-blue-600" />
                          <span className="font-medium">DC Email:</span>
                          <span className="text-blue-600 underline">
                            {alert.district_collector_email}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Actions */}
                <div className="flex gap-3 pt-4 border-t">
                  <Button
                    variant="default"
                    size="sm"
                    onClick={() => {
                      setShowMap(true);
                      handleAlertMarkerClick(alert);
                      // Scroll to map after a short delay to ensure it renders
                      setTimeout(() => {
                        mapRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      }, 100);
                    }}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <MapIcon className="w-4 h-4 mr-2" />
                    View on Map
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/atlas?lat=${alert.latitude}&lng=${alert.longitude}`)}
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Open in Atlas
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const data = JSON.stringify(alert, null, 2);
                      const blob = new Blob([data], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `alert-${alert.alert_id}.json`;
                      a.click();
                    }}
                  >
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                  
                  {alert.deforestation_risk === 'high' && (
                    <Badge variant="destructive" className="ml-auto">
                      <AlertTriangle className="w-3 h-3 mr-1" />
                      IMMEDIATE ACTION REQUIRED
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Manage Locations Modal */}
      <ManageLocationsModal
        isOpen={showManageLocations}
        onClose={() => setShowManageLocations(false)}
        onLocationAdded={() => {
          fetchAlerts();
          fetchStatistics();
        }}
      />
    </div>
  );
};

export default ForestMonitoringDashboard;
