import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { 
  Layers, 
  MapPin, 
  Eye, 
  EyeOff, 
  Info, 
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Search,
  Filter,
  Download,
  Upload,
  Satellite,
  TreePine,
  Shield,
  Map
} from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const AI_SERVICE_URL = process.env.REACT_APP_AI_SERVICE_URL || 'http://localhost:8000';

/**
 * Layer Manager Component for External GIS Layers
 * Integrates FSI, Bhuvan, and other government WMS/WFS services
 */
const ExternalLayerManager = ({ map, onLayerToggle }) => {
  const [layerCatalog, setLayerCatalog] = useState(null);
  const [activeLayers, setActiveLayers] = useState(new Set());
  const [expandedCategories, setExpandedCategories] = useState(new Set(['forest_survey_india']));
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [layerOpacity, setLayerOpacity] = useState({});

  // Load layer catalog on mount
  useEffect(() => {
    loadLayerCatalog();
  }, []);

  const loadLayerCatalog = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${AI_SERVICE_URL}/api/gis/external-layers`);
      setLayerCatalog(response.data);
      toast.success('Layer catalog loaded successfully');
    } catch (error) {
      console.error('Error loading layer catalog:', error);
      toast.error('Failed to load layer catalog');
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (category) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleLayer = async (layerName, category) => {
    const isActive = activeLayers.has(layerName);
    
    if (isActive) {
      // Remove layer from map
      const newActive = new Set(activeLayers);
      newActive.delete(layerName);
      setActiveLayers(newActive);
      
      if (onLayerToggle) {
        onLayerToggle(layerName, false);
      }
      
      toast.info(`Layer ${layerName} hidden`);
    } else {
      // Add layer to map
      try {
        // Get OpenLayers configuration
        const response = await axios.get(
          `${AI_SERVICE_URL}/api/gis/layer-config/${layerName}?format=openlayers`
        );
        
        const config = response.data;
        
        const newActive = new Set(activeLayers);
        newActive.add(layerName);
        setActiveLayers(newActive);
        
        if (onLayerToggle) {
          onLayerToggle(layerName, true, config);
        }
        
        toast.success(`Layer ${layerName} added to map`);
      } catch (error) {
        console.error('Error loading layer:', error);
        toast.error(`Failed to load layer ${layerName}`);
      }
    }
  };

  const setOpacity = (layerName, opacity) => {
    setLayerOpacity(prev => ({
      ...prev,
      [layerName]: opacity
    }));
    
    if (onLayerToggle) {
      onLayerToggle(layerName, true, { opacity });
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'forest_survey_india': return <TreePine className="w-4 h-4" />;
      case 'bhuvan': return <Satellite className="w-4 h-4" />;
      case 'tribal_affairs': return <MapPin className="w-4 h-4" />;
      case 'protected_areas': return <Shield className="w-4 h-4" />;
      case 'administrative': return <Map className="w-4 h-4" />;
      default: return <Layers className="w-4 h-4" />;
    }
  };

  const getCategoryTitle = (category) => {
    const titles = {
      'forest_survey_india': 'Forest Survey of India',
      'bhuvan': 'ISRO Bhuvan',
      'tribal_affairs': 'Ministry of Tribal Affairs',
      'protected_areas': 'Protected Areas (WII)',
      'administrative': 'Administrative Boundaries'
    };
    return titles[category] || category;
  };

  const filterLayers = (layers) => {
    if (!searchTerm) return layers;
    
    const filtered = {};
    Object.entries(layers).forEach(([name, config]) => {
      if (
        config.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        config.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        name.toLowerCase().includes(searchTerm.toLowerCase())
      ) {
        filtered[name] = config;
      }
    });
    return filtered;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Layers className="w-5 h-5" />
            External Layers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-2"></div>
              <p className="text-sm text-gray-600">Loading layer catalog...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!layerCatalog) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>External Layers</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">Failed to load layer catalog</p>
          <Button onClick={loadLayerCatalog} className="mt-2">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="max-h-[600px] overflow-hidden flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5" />
            External Layers
          </div>
          <Badge variant="outline">{activeLayers.size} active</Badge>
        </CardTitle>
        <CardDescription>
          Government GIS layers from FSI, Bhuvan, and other sources
        </CardDescription>
      </CardHeader>
      
      <div className="px-6 pb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search layers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      <CardContent className="flex-1 overflow-y-auto space-y-3">
        {/* Recommended Layers */}
        {layerCatalog.recommended && layerCatalog.recommended.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="default">
                Recommended for FRA
              </Badge>
            </div>
            <div className="space-y-2 text-xs text-gray-600">
              {layerCatalog.recommended.map((layerName) => {
                // Find the layer in catalog
                let layerConfig = null;
                let category = null;
                Object.entries(layerCatalog.catalog).forEach(([cat, layers]) => {
                  if (layers[layerName]) {
                    layerConfig = layers[layerName];
                    category = cat;
                  }
                });
                
                if (!layerConfig) return null;
                
                const isActive = activeLayers.has(layerName);
                
                return (
                  <div key={layerName} className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleLayer(layerName, category)}
                      className="flex-1 justify-start"
                    >
                      {isActive ? (
                        <Eye className="w-3 h-3 mr-2 text-green-600" />
                      ) : (
                        <EyeOff className="w-3 h-3 mr-2 text-gray-400" />
                      )}
                      {layerConfig.title}
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Layer Categories */}
        {Object.entries(layerCatalog.catalog).map(([category, layers]) => {
          const filteredLayers = filterLayers(layers);
          if (Object.keys(filteredLayers).length === 0) return null;
          
          const isExpanded = expandedCategories.has(category);
          
          return (
            <div key={category} className="border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-2">
                  {getCategoryIcon(category)}
                  <span className="font-medium text-sm">{getCategoryTitle(category)}</span>
                  <Badge variant="secondary" className="text-xs">
                    {Object.keys(filteredLayers).length}
                  </Badge>
                </div>
                {isExpanded ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>
              
              {isExpanded && (
                <div className="p-3 space-y-2">
                  {Object.entries(filteredLayers).map(([layerName, config]) => {
                    const isActive = activeLayers.has(layerName);
                    const opacity = layerOpacity[layerName] || 1;
                    
                    return (
                      <div key={layerName} className="space-y-2">
                        <div className="flex items-start gap-2">
                          <Button
                            variant={isActive ? "default" : "outline"}
                            size="sm"
                            onClick={() => toggleLayer(layerName, category)}
                            className="flex-shrink-0"
                          >
                            {isActive ? (
                              <Eye className="w-4 h-4" />
                            ) : (
                              <EyeOff className="w-4 h-4" />
                            )}
                          </Button>
                          
                          <div className="flex-1 min-w-0">
                            <h4 className="text-sm font-medium text-gray-900 truncate">
                              {config.title}
                            </h4>
                            <p className="text-xs text-gray-600 line-clamp-2">
                              {config.description}
                            </p>
                            <p className="text-xs text-gray-400 mt-1">
                              {config.attribution}
                            </p>
                          </div>
                          
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => window.open(config.url, '_blank')}
                          >
                            <Info className="w-4 h-4" />
                          </Button>
                        </div>
                        
                        {isActive && (
                          <div className="ml-12 space-y-1">
                            <label className="text-xs text-gray-600">
                              Opacity: {Math.round(opacity * 100)}%
                            </label>
                            <input
                              type="range"
                              min="0"
                              max="1"
                              step="0.1"
                              value={opacity}
                              onChange={(e) => setOpacity(layerName, parseFloat(e.target.value))}
                              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};

export default ExternalLayerManager;
