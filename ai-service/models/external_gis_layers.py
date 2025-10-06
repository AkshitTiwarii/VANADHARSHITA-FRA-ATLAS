"""
External GIS Layer Integration
Supports WMS/WFS layers from FSI, Bhuvan, and other Indian geospatial services
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WMSLayerConfig:
    """Configuration for WMS layer"""
    name: str
    title: str
    url: str
    layers: str
    version: str = "1.1.1"
    format: str = "image/png"
    transparent: bool = True
    attribution: str = ""
    description: str = ""
    min_zoom: int = 5
    max_zoom: int = 18


@dataclass
class WFSLayerConfig:
    """Configuration for WFS layer"""
    name: str
    title: str
    url: str
    type_name: str
    version: str = "1.1.0"
    output_format: str = "application/json"
    attribution: str = ""
    description: str = ""


class ExternalGISLayers:
    """
    Catalog of external GIS layers for FRA Atlas
    Includes Forest Survey of India, ISRO Bhuvan, and other government sources
    """
    
    # Forest Survey of India (FSI) Layers
    FSI_LAYERS = {
        'forest_cover': WMSLayerConfig(
            name='fsi_forest_cover',
            title='Forest Cover (FSI)',
            url='https://fsi.nic.in/geoserver/wms',
            layers='fsi:forest_cover_2021',
            attribution='Forest Survey of India',
            description='Latest forest cover classification from FSI State of Forest Report'
        ),
        'forest_type': WMSLayerConfig(
            name='fsi_forest_type',
            title='Forest Type Classification',
            url='https://fsi.nic.in/geoserver/wms',
            layers='fsi:forest_type',
            attribution='Forest Survey of India',
            description='Champion and Seth forest type classification'
        ),
        'forest_density': WMSLayerConfig(
            name='fsi_forest_density',
            title='Forest Density',
            url='https://fsi.nic.in/geoserver/wms',
            layers='fsi:canopy_density',
            attribution='Forest Survey of India',
            description='Forest canopy density classification (Very Dense, Moderately Dense, Open)'
        ),
        'mangroves': WMSLayerConfig(
            name='fsi_mangroves',
            title='Mangrove Cover',
            url='https://fsi.nic.in/geoserver/wms',
            layers='fsi:mangrove_cover',
            attribution='Forest Survey of India',
            description='Mangrove forest distribution'
        )
    }
    
    # ISRO Bhuvan Layers
    BHUVAN_LAYERS = {
        'forest_type_bhuvan': WMSLayerConfig(
            name='bhuvan_forest',
            title='Forest Cover (Bhuvan)',
            url='https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms',
            layers='india3_forest_type',
            attribution='ISRO Bhuvan',
            description='Forest type layer from ISRO Bhuvan'
        ),
        'lulc': WMSLayerConfig(
            name='bhuvan_lulc',
            title='Land Use Land Cover',
            url='https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms',
            layers='india3_lulc',
            attribution='ISRO Bhuvan',
            description='Land use and land cover classification'
        ),
        'wasteland': WMSLayerConfig(
            name='bhuvan_wasteland',
            title='Wasteland Atlas',
            url='https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms',
            layers='india3_wasteland',
            attribution='ISRO Bhuvan',
            description='Wasteland mapping from NRSC'
        ),
        'cadastral': WMSLayerConfig(
            name='bhuvan_cadastral',
            title='Cadastral Maps',
            url='https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms',
            layers='india3_cadastral',
            attribution='ISRO Bhuvan',
            description='Village and plot boundaries'
        ),
        'tribal_areas': WMSLayerConfig(
            name='bhuvan_tribal',
            title='Scheduled Areas',
            url='https://bhuvan-vec1.nrsc.gov.in/bhuvan/gwc/service/wms',
            layers='india3_scheduled_areas',
            attribution='ISRO Bhuvan',
            description='Fifth and Sixth Schedule areas'
        )
    }
    
    # Ministry of Tribal Affairs Layers
    TRIBAL_AFFAIRS_LAYERS = {
        'fra_boundaries': WMSLayerConfig(
            name='mota_fra_boundaries',
            title='FRA Recognition Areas',
            url='https://tribal.gov.in/geoserver/wms',
            layers='mota:fra_recognized_areas',
            attribution='Ministry of Tribal Affairs',
            description='Community forest resource rights recognized areas'
        ),
        'tribal_villages': WMSLayerConfig(
            name='mota_tribal_villages',
            title='Tribal Villages',
            url='https://tribal.gov.in/geoserver/wms',
            layers='mota:tribal_villages',
            attribution='Ministry of Tribal Affairs',
            description='Villages with tribal population'
        )
    }
    
    # Protected Areas (Wildlife Institute of India)
    PROTECTED_AREAS_LAYERS = {
        'national_parks': WMSLayerConfig(
            name='wii_national_parks',
            title='National Parks',
            url='https://wiienvis.nic.in/geoserver/wms',
            layers='wii:national_parks',
            attribution='Wildlife Institute of India',
            description='National Parks of India'
        ),
        'wildlife_sanctuaries': WMSLayerConfig(
            name='wii_sanctuaries',
            title='Wildlife Sanctuaries',
            url='https://wiienvis.nic.in/geoserver/wms',
            layers='wii:wildlife_sanctuaries',
            attribution='Wildlife Institute of India',
            description='Wildlife Sanctuaries of India'
        ),
        'tiger_reserves': WMSLayerConfig(
            name='wii_tiger_reserves',
            title='Tiger Reserves',
            url='https://wiienvis.nic.in/geoserver/wms',
            layers='wii:tiger_reserves',
            attribution='Wildlife Institute of India',
            description='Project Tiger reserves'
        ),
        'critical_wildlife_habitat': WMSLayerConfig(
            name='wii_cwh',
            title='Critical Wildlife Habitat',
            url='https://wiienvis.nic.in/geoserver/wms',
            layers='wii:critical_wildlife_habitat',
            attribution='Wildlife Institute of India',
            description='Critical Wildlife Habitats (CWH) notified under FRA'
        )
    }
    
    # Survey of India Administrative Boundaries
    SOI_LAYERS = {
        'state_boundaries': WMSLayerConfig(
            name='soi_states',
            title='State Boundaries',
            url='https://soinakshe.uk.gov.in/geoserver/wms',
            layers='soi:india_states',
            attribution='Survey of India',
            description='Official state administrative boundaries'
        ),
        'district_boundaries': WMSLayerConfig(
            name='soi_districts',
            title='District Boundaries',
            url='https://soinakshe.uk.gov.in/geoserver/wms',
            layers='soi:india_districts',
            attribution='Survey of India',
            description='Official district administrative boundaries'
        ),
        'tehsil_boundaries': WMSLayerConfig(
            name='soi_tehsils',
            title='Tehsil/Block Boundaries',
            url='https://soinakshe.uk.gov.in/geoserver/wms',
            layers='soi:india_tehsils',
            attribution='Survey of India',
            description='Tehsil/Block administrative boundaries'
        )
    }
    
    @classmethod
    def get_all_layers(cls) -> Dict[str, Dict[str, WMSLayerConfig]]:
        """Get all available external layers organized by category"""
        return {
            'forest_survey_india': cls.FSI_LAYERS,
            'bhuvan': cls.BHUVAN_LAYERS,
            'tribal_affairs': cls.TRIBAL_AFFAIRS_LAYERS,
            'protected_areas': cls.PROTECTED_AREAS_LAYERS,
            'administrative': cls.SOI_LAYERS
        }
    
    @classmethod
    def get_layer_config(cls, layer_name: str) -> Optional[WMSLayerConfig]:
        """Get configuration for specific layer by name"""
        all_layers = cls.get_all_layers()
        for category, layers in all_layers.items():
            if layer_name in layers:
                return layers[layer_name]
        return None
    
    @classmethod
    def get_layers_by_category(cls, category: str) -> Dict[str, WMSLayerConfig]:
        """Get all layers in a specific category"""
        all_layers = cls.get_all_layers()
        return all_layers.get(category, {})
    
    @classmethod
    def get_openlayers_config(cls, layer_name: str) -> Optional[Dict]:
        """
        Get OpenLayers-compatible configuration for a layer
        
        Returns dict ready to use in frontend OpenLayers
        """
        config = cls.get_layer_config(layer_name)
        if not config:
            return None
        
        return {
            'type': 'TileWMS',
            'name': config.name,
            'title': config.title,
            'url': config.url,
            'params': {
                'LAYERS': config.layers,
                'VERSION': config.version,
                'FORMAT': config.format,
                'TRANSPARENT': config.transparent
            },
            'attribution': config.attribution,
            'description': config.description,
            'minZoom': config.min_zoom,
            'maxZoom': config.max_zoom
        }
    
    @classmethod
    def get_leaflet_config(cls, layer_name: str) -> Optional[Dict]:
        """Get Leaflet-compatible configuration"""
        config = cls.get_layer_config(layer_name)
        if not config:
            return None
        
        return {
            'type': 'wms',
            'name': config.name,
            'title': config.title,
            'url': config.url,
            'options': {
                'layers': config.layers,
                'version': config.version,
                'format': config.format,
                'transparent': config.transparent,
                'attribution': config.attribution
            }
        }
    
    @classmethod
    def export_catalog_json(cls) -> Dict:
        """Export complete layer catalog as JSON for frontend"""
        catalog = {}
        all_layers = cls.get_all_layers()
        
        for category, layers in all_layers.items():
            catalog[category] = {}
            for layer_name, config in layers.items():
                catalog[category][layer_name] = {
                    'name': config.name,
                    'title': config.title,
                    'url': config.url,
                    'layers': config.layers,
                    'attribution': config.attribution,
                    'description': config.description,
                    'openlayers': cls.get_openlayers_config(layer_name)
                }
        
        return catalog


# Alternative base map sources
ALTERNATIVE_BASEMAPS = {
    'satellite_esri': {
        'name': 'Esri World Imagery',
        'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attribution': 'Esri, DigitalGlobe, GeoEye, Earthstar Geographics, CNES/Airbus DS, USDA, USGS, AeroGRID',
        'max_zoom': 19
    },
    'topo_osm': {
        'name': 'OpenTopoMap',
        'url': 'https://{a-c}.tile.opentopomap.org/{z}/{x}/{y}.png',
        'attribution': 'Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap',
        'max_zoom': 17
    },
    'satellite_google': {
        'name': 'Google Satellite (Hybrid)',
        'url': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        'attribution': 'Google',
        'max_zoom': 20,
        'note': 'Usage subject to Google Maps terms'
    },
    'terrain': {
        'name': 'Terrain (Stamen)',
        'url': 'https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg',
        'attribution': 'Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap',
        'max_zoom': 16
    }
}


def get_recommended_layers_for_fra() -> List[str]:
    """
    Get recommended layers for FRA implementation
    
    Returns list of layer names most relevant for FRA Atlas
    """
    return [
        'fsi_forest_cover',
        'fsi_forest_density',
        'bhuvan_forest',
        'bhuvan_tribal_areas',
        'bhuvan_cadastral',
        'mota_fra_boundaries',
        'mota_tribal_villages',
        'wii_critical_wildlife_habitat',
        'soi_district_boundaries'
    ]


if __name__ == "__main__":
    # Export catalog for frontend
    import json
    catalog = ExternalGISLayers.export_catalog_json()
    print(json.dumps(catalog, indent=2))
    
    print("\n=== Recommended Layers for FRA ===")
    for layer in get_recommended_layers_for_fra():
        config = ExternalGISLayers.get_layer_config(layer)
        if config:
            print(f"✓ {config.title}")
