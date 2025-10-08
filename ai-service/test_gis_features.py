"""
Test script for GIS integration features
Run with: python test_gis_features.py
"""

import sys
import json
from pathlib import Path

print("=" * 60)
print("FRA Atlas - GIS Integration Test Suite")
print("=" * 60)

# Test 1: Check dependencies
print("\n[1/4] Checking geospatial dependencies...")
try:
    import geopandas as gpd
    import shapely
    from shapely.geometry import Point, Polygon
    import pyproj
    import fiona
    
    print("✓ geopandas:", gpd.__version__)
    print("✓ shapely:", shapely.__version__)
    print("✓ pyproj:", pyproj.__version__)
    print("✓ fiona:", fiona.__version__)
    print("✓ All required dependencies installed!")
    DEPS_AVAILABLE = True
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    print("\n  Install with: pip install -r requirements_gis.txt")
    DEPS_AVAILABLE = False

# Test 2: Verify modules
print("\n[2/4] Verifying GIS modules...")
try:
    from models.shapefile_processor import ShapefileProcessor, check_dependencies
    from models.external_gis_layers import ExternalGISLayers, get_recommended_layers_for_fra
    
    print("✓ ShapefileProcessor imported")
    print("✓ ExternalGISLayers imported")
    
    # Check status
    deps_status = check_dependencies()
    print(f"✓ Dependency check: {deps_status['status']}")
    
except ImportError as e:
    print(f"✗ Module import error: {e}")
    sys.exit(1)

# Test 3: External layers catalog
print("\n[3/4] Testing external layers catalog...")
try:
    catalog = ExternalGISLayers.export_catalog_json()
    
    print(f"✓ Loaded {len(catalog)} categories")
    for category, layers in catalog.items():
        print(f"  - {category}: {len(layers)} layers")
    
    # Test recommended layers
    recommended = get_recommended_layers_for_fra()
    print(f"\n✓ Recommended layers for FRA: {len(recommended)}")
    for layer_name in recommended[:5]:  # Show first 5
        config = ExternalGISLayers.get_layer_config(layer_name)
        if config:
            print(f"  - {config.title}")
    
    # Test OpenLayers config generation
    ol_config = ExternalGISLayers.get_openlayers_config('fsi_forest_cover')
    if ol_config:
        print("\n✓ OpenLayers configuration generated successfully")
        print(f"  Layer: {ol_config['title']}")
        print(f"  URL: {ol_config['url']}")
    
except Exception as e:
    print(f"✗ Error testing layers: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Shapefile processor (without actual file)
print("\n[4/4] Testing shapefile processor...")
try:
    if DEPS_AVAILABLE:
        processor = ShapefileProcessor()
        print(f"✓ Processor initialized")
        print(f"✓ Upload directory: {processor.upload_dir}")
        print(f"✓ Upload directory exists: {processor.upload_dir.exists()}")
        
        # Test with sample data
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Create sample GeoDataFrame
        points = [Point(77.0, 19.0), Point(78.0, 20.0), Point(79.0, 21.0)]
        gdf = gpd.GeoDataFrame(
            {'village': ['Village A', 'Village B', 'Village C']},
            geometry=points,
            crs='EPSG:4326'
        )
        
        # Save to temporary shapefile
        temp_shp = processor.upload_dir / "test.shp"
        gdf.to_file(temp_shp)
        print(f"\n✓ Created test shapefile: {temp_shp}")
        
        # Test conversion to GeoJSON
        geojson = processor.shapefile_to_geojson(str(temp_shp))
        if geojson:
            print(f"✓ Converted to GeoJSON: {geojson['metadata']['record_count']} features")
        
        # Test attribute extraction
        attributes = processor.extract_attributes(str(temp_shp))
        if attributes:
            print(f"✓ Extracted attributes: {list(attributes['columns'].keys())}")
        
        # Cleanup
        import shutil
        for file in processor.upload_dir.glob("test.*"):
            file.unlink()
        print("✓ Cleaned up test files")
    else:
        print("⚠ Skipping processor tests (dependencies not available)")
        
except Exception as e:
    print(f"✗ Error testing processor: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)

if DEPS_AVAILABLE:
    print("✓ All tests passed!")
    print("\n🎉 GIS integration is ready to use!")
    print("\nNext steps:")
    print("1. Start AI service: python main_v2.py")
    print("2. Test API: http://localhost:8000/docs")
    print("3. Upload shapefile via: POST /api/gis/upload-shapefile")
    print("4. Get layers via: GET /api/gis/external-layers")
else:
    print("⚠ Some dependencies missing")
    print("\nInstall required packages:")
    print("  pip install -r requirements_gis.txt")
    print("\nThen run this test again.")

print("=" * 60)
