import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { 
  Search, 
  MapPin, 
  Layers, 
  ZoomIn, 
  ZoomOut, 
  Navigation,
  RotateCcw,
  Download,
  Satellite,
  AlertTriangle
} from 'lucide-react';
import { toast } from 'sonner';
import { useTranslation } from '../contexts/LanguageContext';

// Dynamic OpenLayers imports to handle loading issues
let Map, View, TileLayer, VectorLayer, VectorSource, OSM, XYZ;
let Style, Fill, Stroke, CircleStyle, Text, Feature, Point;
let fromLonLat, toLonLat, Select, click;

const ForestAtlasFixed = () => {
  const { t } = useTranslation();
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const [isMapLibLoaded, setIsMapLibLoaded] = useState(false);
  const [mapError, setMapError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [villages, setVillages] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  // Load OpenLayers dynamically
  useEffect(() => {
    const loadOpenLayers = async () => {
      try {
        console.log('Loading OpenLayers...');
        
        // Import all required OpenLayers modules
        const ol = await import('ol/Map');
        Map = ol.default;
        
        const viewModule = await import('ol/View');
        View = viewModule.default;
        
        const tileLayerModule = await import('ol/layer/Tile');
        TileLayer = tileLayerModule.default;
        
        const vectorLayerModule = await import('ol/layer/Vector');
        VectorLayer = vectorLayerModule.default;
        
        const vectorSourceModule = await import('ol/source/Vector');
        VectorSource = vectorSourceModule.default;
        
        const osmModule = await import('ol/source/OSM');
        OSM = osmModule.default;
        
        const xyzModule = await import('ol/source/XYZ');
        XYZ = xyzModule.default;
        
        const styleModule = await import('ol/style');
        Style = styleModule.Style;
        Fill = styleModule.Fill;
        Stroke = styleModule.Stroke;
        CircleStyle = styleModule.Circle;
        Text = styleModule.Text;
        
        const featureModule = await import('ol/Feature');
        Feature = featureModule.default;
        
        const pointModule = await import('ol/geom/Point');
        Point = pointModule.default;
        
        const projModule = await import('ol/proj');
        fromLonLat = projModule.fromLonLat;
        toLonLat = projModule.toLonLat;
        
        const selectModule = await import('ol/interaction');
        Select = selectModule.Select;
        
        const conditionModule = await import('ol/events/condition');
        click = conditionModule.click;
        
        // Import CSS
        await import('ol/ol.css');
        
        console.log('OpenLayers loaded successfully');
        setIsMapLibLoaded(true);
        
      } catch (error) {
        console.error('Failed to load OpenLayers:', error);
        setMapError(error.message);
        toast.error('Failed to load map library');
      }
    };

    loadOpenLayers();
  }, []);

  // Initialize map after OpenLayers is loaded
  useEffect(() => {
    if (!isMapLibLoaded || !mapRef.current || mapInstance.current) return;

    const initMap = () => {
      try {
        console.log('Initializing map with loaded OpenLayers...');
        
        const map = new Map({
          target: mapRef.current,
          layers: [
            new TileLayer({
              source: new OSM()
            })
          ],
          view: new View({
            center: fromLonLat([78.9629, 20.5937]), // Center of India
            zoom: 6
          })
        });

        mapInstance.current = map;
        setLoading(false);
        
        // Add some mock villages for testing
        const mockVillages = [
          { id: 1, name: 'Khargone Village', lat: 21.8236, lng: 75.6088 },
          { id: 2, name: 'Bastar Village', lat: 19.0144, lng: 81.9610 },
          { id: 3, name: 'Gadchiroli Village', lat: 20.1809, lng: 80.0046 }
        ];
        
        setVillages(mockVillages);
        addVillagesToMap(mockVillages, map);
        
        console.log('Map initialized successfully');
        toast.success('Map loaded successfully');
        
      } catch (error) {
        console.error('Map initialization failed:', error);
        setMapError(error.message);
        setLoading(false);
        toast.error('Failed to initialize map');
      }
    };

    // Small delay to ensure DOM is ready
    setTimeout(initMap, 100);

    return () => {
      if (mapInstance.current) {
        mapInstance.current.setTarget(null);
        mapInstance.current = null;
      }
    };
  }, [isMapLibLoaded]);

  const addVillagesToMap = (villagesData, map) => {
    try {
      const vectorSource = new VectorSource();
      
      villagesData.forEach(village => {
        const feature = new Feature({
          geometry: new Point(fromLonLat([village.lng, village.lat])),
          name: village.name,
          villageData: village
        });
        
        feature.setStyle(new Style({
          image: new CircleStyle({
            radius: 8,
            fill: new Fill({ color: '#2563eb' }),
            stroke: new Stroke({ color: '#ffffff', width: 2 })
          })
        }));
        
        vectorSource.addFeature(feature);
      });
      
      const vectorLayer = new VectorLayer({
        source: vectorSource
      });
      
      map.addLayer(vectorLayer);
      
    } catch (error) {
      console.error('Failed to add villages to map:', error);
    }
  };

  const handleZoomIn = () => {
    if (mapInstance.current) {
      const view = mapInstance.current.getView();
      view.setZoom(view.getZoom() + 1);
    }
  };

  const handleZoomOut = () => {
    if (mapInstance.current) {
      const view = mapInstance.current.getView();
      view.setZoom(view.getZoom() - 1);
    }
  };

  const handleResetView = () => {
    if (mapInstance.current) {
      const view = mapInstance.current.getView();
      view.setCenter(fromLonLat([78.9629, 20.5937]));
      view.setZoom(6);
    }
  };

  if (mapError) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-900">Forest Rights Atlas</h1>
            <p className="text-slate-600">Interactive map of forest villages and claims</p>
          </div>
        </div>
        
        <Card className="h-[600px] flex items-center justify-center">
          <div className="text-center">
            <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-red-800 mb-2">Map Loading Error</h3>
            <p className="text-sm text-red-600 mb-4">
              {mapError}
            </p>
            <p className="text-xs text-gray-500 mb-4">
              This could be due to network issues or browser compatibility.
            </p>
            <Button 
              onClick={() => window.location.reload()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Refresh Page
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-blue-900">Forest Rights Atlas</h1>
          <p className="text-slate-600">Interactive map of forest villages and claims</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export Data
          </Button>
          <Button variant="outline" size="sm">
            <Satellite className="w-4 h-4 mr-2" />
            Satellite View
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          {/* Search */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center">
                <Search className="w-5 h-5 mr-2 text-blue-600" />
                Search Villages
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Input
                placeholder="Search by name or code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center">
                <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-slate-600">Total Villages</span>
                <Badge variant="secondary">{villages.length}</Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-slate-600">Map Status</span>
                <Badge className={`${loading ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                  {loading ? 'Loading' : 'Ready'}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Map Area */}
        <div className="lg:col-span-3">
          <Card className="h-[600px]">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <MapPin className="w-5 h-5 mr-2 text-blue-600" />
                  Interactive Forest Map
                </CardTitle>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={handleZoomOut}>
                    <ZoomOut className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleZoomIn}>
                    <ZoomIn className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleResetView}>
                    <RotateCcw className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-full p-0">
              <div 
                ref={mapRef}
                className="map-container rounded-lg relative bg-gray-100"
                style={{ 
                  height: '520px',
                  width: '100%'
                }}
              >
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-20">
                    <div className="text-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                      <p className="text-sm text-gray-600">
                        {!isMapLibLoaded ? 'Loading map library...' : 'Initializing map...'}
                      </p>
                    </div>
                  </div>
                )}
                
                {/* Map Legend */}
                {!loading && (
                  <div className="absolute bottom-4 left-4 bg-white p-3 rounded-lg shadow-lg z-10 max-w-48">
                    <h4 className="font-medium text-sm mb-2">Legend</h4>
                    <div className="space-y-1 text-xs">
                      <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                        <span>Villages</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ForestAtlasFixed;