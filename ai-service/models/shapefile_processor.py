"""
Shapefile Processor for FRA Atlas
Handles shapefile uploads, processing, and conversion to GeoJSON
"""

import os
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# Try importing geospatial libraries
try:
    import geopandas as gpd
    import shapely
    from shapely.geometry import shape, mapping, Point, Polygon, MultiPolygon
    from shapely.ops import unary_union
    GEOSPATIAL_AVAILABLE = True
except ImportError:
    GEOSPATIAL_AVAILABLE = False
    logging.warning("GeoPandas not available. Install with: pip install geopandas shapely")

logger = logging.getLogger(__name__)


class ShapefileProcessor:
    """Process shapefiles for FRA patta holder boundaries"""
    
    def __init__(self, upload_dir: str = "uploads/shapefiles"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        if not GEOSPATIAL_AVAILABLE:
            logger.warning("Geospatial libraries not available. Shapefile processing disabled.")
    
    def extract_shapefile(self, zip_path: str) -> Optional[str]:
        """
        Extract shapefile from ZIP archive
        
        Returns:
            Path to extracted .shp file or None if extraction fails
        """
        if not GEOSPATIAL_AVAILABLE:
            return None
            
        try:
            # Create temporary directory for extraction
            temp_dir = tempfile.mkdtemp(dir=self.upload_dir)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find .shp file
            shp_files = list(Path(temp_dir).rglob("*.shp"))
            
            if not shp_files:
                logger.error("No .shp file found in ZIP archive")
                shutil.rmtree(temp_dir)
                return None
            
            logger.info(f"Found shapefile: {shp_files[0]}")
            return str(shp_files[0])
            
        except Exception as e:
            logger.error(f"Error extracting shapefile: {e}")
            return None
    
    def validate_shapefile(self, shp_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate shapefile structure and required files
        
        Returns:
            (is_valid, error_message)
        """
        if not GEOSPATIAL_AVAILABLE:
            return False, "Geospatial libraries not installed"
            
        try:
            # Check for required files
            base_path = Path(shp_path).with_suffix('')
            required_extensions = ['.shp', '.shx', '.dbf']
            
            missing_files = []
            for ext in required_extensions:
                if not (base_path.with_suffix(ext)).exists():
                    missing_files.append(ext)
            
            if missing_files:
                return False, f"Missing required files: {', '.join(missing_files)}"
            
            # Try reading with GeoPandas
            gdf = gpd.read_file(shp_path)
            
            # Check if has geometry
            if gdf.geometry.empty.all():
                return False, "Shapefile contains no geometries"
            
            # Check coordinate reference system
            if gdf.crs is None:
                logger.warning("Shapefile has no CRS defined. Assuming EPSG:4326")
            
            logger.info(f"Shapefile validation passed. Records: {len(gdf)}, CRS: {gdf.crs}")
            return True, None
            
        except Exception as e:
            return False, f"Error reading shapefile: {str(e)}"
    
    def shapefile_to_geojson(
        self, 
        shp_path: str,
        simplify: bool = True,
        tolerance: float = 0.001
    ) -> Optional[Dict]:
        """
        Convert shapefile to GeoJSON format
        
        Args:
            shp_path: Path to .shp file
            simplify: Whether to simplify geometries (reduces file size)
            tolerance: Simplification tolerance in degrees (higher = more simplified)
        
        Returns:
            GeoJSON FeatureCollection or None
        """
        if not GEOSPATIAL_AVAILABLE:
            logger.error("GeoPandas not available")
            return None
            
        try:
            # Read shapefile
            gdf = gpd.read_file(shp_path)
            
            # Convert to WGS84 (EPSG:4326) if needed
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                logger.info(f"Converting from {gdf.crs} to EPSG:4326")
                gdf = gdf.to_crs(epsg=4326)
            
            # Simplify geometries if requested
            if simplify:
                logger.info(f"Simplifying geometries with tolerance {tolerance}")
                gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
            
            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())
            
            # Add metadata
            geojson['metadata'] = {
                'record_count': len(gdf),
                'crs': 'EPSG:4326',
                'bounds': gdf.total_bounds.tolist(),
                'geometry_types': gdf.geom_type.unique().tolist()
            }
            
            logger.info(f"Converted shapefile to GeoJSON: {len(gdf)} features")
            return geojson
            
        except Exception as e:
            logger.error(f"Error converting shapefile to GeoJSON: {e}")
            return None
    
    def merge_boundaries(self, shp_path: str, group_by: Optional[str] = None) -> Optional[Dict]:
        """
        Merge multiple boundaries into single features
        
        Args:
            shp_path: Path to shapefile
            group_by: Column name to group boundaries by (e.g., 'village_name')
        
        Returns:
            GeoJSON with merged boundaries
        """
        if not GEOSPATIAL_AVAILABLE:
            return None
            
        try:
            gdf = gpd.read_file(shp_path)
            
            # Convert to WGS84
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs(epsg=4326)
            
            if group_by and group_by in gdf.columns:
                # Group and merge geometries
                logger.info(f"Merging boundaries by {group_by}")
                merged = gdf.dissolve(by=group_by, aggfunc='first')
                merged = merged.reset_index()
            else:
                # Merge all into single boundary
                logger.info("Merging all boundaries into one")
                merged_geom = unary_union(gdf.geometry)
                merged = gpd.GeoDataFrame(
                    {'geometry': [merged_geom]},
                    crs=gdf.crs
                )
            
            geojson = json.loads(merged.to_json())
            geojson['metadata'] = {
                'original_count': len(gdf),
                'merged_count': len(merged),
                'group_by': group_by
            }
            
            return geojson
            
        except Exception as e:
            logger.error(f"Error merging boundaries: {e}")
            return None
    
    def extract_attributes(self, shp_path: str) -> Optional[Dict]:
        """
        Extract attribute table from shapefile
        
        Returns:
            Dictionary with column names and sample values
        """
        if not GEOSPATIAL_AVAILABLE:
            return None
            
        try:
            gdf = gpd.read_file(shp_path)
            
            # Get column info
            columns = {}
            for col in gdf.columns:
                if col != 'geometry':
                    columns[col] = {
                        'dtype': str(gdf[col].dtype),
                        'sample_values': gdf[col].head(5).tolist(),
                        'unique_count': gdf[col].nunique(),
                        'null_count': gdf[col].isnull().sum()
                    }
            
            return {
                'record_count': len(gdf),
                'columns': columns,
                'geometry_type': gdf.geom_type.unique().tolist()
            }
            
        except Exception as e:
            logger.error(f"Error extracting attributes: {e}")
            return None
    
    def spatial_join_with_villages(
        self, 
        boundary_shp: str,
        villages: List[Dict]
    ) -> Optional[List[Dict]]:
        """
        Perform spatial join to match villages with FRA boundaries
        
        Args:
            boundary_shp: Path to FRA boundary shapefile
            villages: List of village dictionaries with lat/lon
        
        Returns:
            Villages enriched with boundary information
        """
        if not GEOSPATIAL_AVAILABLE:
            return None
            
        try:
            # Load boundaries
            boundaries = gpd.read_file(boundary_shp)
            if boundaries.crs and boundaries.crs.to_epsg() != 4326:
                boundaries = boundaries.to_crs(epsg=4326)
            
            # Convert villages to GeoDataFrame
            village_points = []
            for v in villages:
                point = Point(v.get('longitude', 0), v.get('latitude', 0))
                village_points.append(point)
            
            villages_gdf = gpd.GeoDataFrame(
                villages,
                geometry=village_points,
                crs='EPSG:4326'
            )
            
            # Spatial join
            joined = gpd.sjoin(villages_gdf, boundaries, how='left', predicate='within')
            
            # Convert back to dict
            enriched_villages = json.loads(joined.to_json())['features']
            
            logger.info(f"Spatial join completed: {len(enriched_villages)} villages matched")
            return enriched_villages
            
        except Exception as e:
            logger.error(f"Error in spatial join: {e}")
            return None
    
    def create_buffer_zone(
        self,
        shp_path: str,
        buffer_distance_km: float = 1.0
    ) -> Optional[Dict]:
        """
        Create buffer zones around FRA boundaries
        
        Args:
            shp_path: Path to boundary shapefile
            buffer_distance_km: Buffer distance in kilometers
        
        Returns:
            GeoJSON with buffered boundaries
        """
        if not GEOSPATIAL_AVAILABLE:
            return None
            
        try:
            gdf = gpd.read_file(shp_path)
            
            # Convert to projected CRS for accurate buffering (meters)
            # Using India-specific projection (UTM Zone 43N)
            gdf_projected = gdf.to_crs(epsg=32643)
            
            # Create buffer (convert km to meters)
            buffer_distance_m = buffer_distance_km * 1000
            gdf_projected['geometry'] = gdf_projected.geometry.buffer(buffer_distance_m)
            
            # Convert back to WGS84
            gdf_buffered = gdf_projected.to_crs(epsg=4326)
            
            geojson = json.loads(gdf_buffered.to_json())
            geojson['metadata'] = {
                'buffer_distance_km': buffer_distance_km,
                'feature_count': len(gdf_buffered)
            }
            
            logger.info(f"Created {buffer_distance_km}km buffer zones")
            return geojson
            
        except Exception as e:
            logger.error(f"Error creating buffer zone: {e}")
            return None
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Remove temporary extracted shapefiles older than max_age_hours"""
        try:
            import time
            current_time = time.time()
            
            for item in self.upload_dir.iterdir():
                if item.is_dir():
                    item_age = current_time - item.stat().st_mtime
                    if item_age > (max_age_hours * 3600):
                        logger.info(f"Removing old temp directory: {item}")
                        shutil.rmtree(item)
                        
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")


# Installation check
def check_dependencies():
    """Check if required geospatial dependencies are installed"""
    if GEOSPATIAL_AVAILABLE:
        return {
            'status': 'ready',
            'message': 'All geospatial dependencies installed',
            'libraries': {
                'geopandas': gpd.__version__,
                'shapely': shapely.__version__
            }
        }
    else:
        return {
            'status': 'missing',
            'message': 'Install geospatial libraries: pip install geopandas shapely pyproj',
            'libraries': {}
        }


if __name__ == "__main__":
    # Test dependency check
    print(json.dumps(check_dependencies(), indent=2))
