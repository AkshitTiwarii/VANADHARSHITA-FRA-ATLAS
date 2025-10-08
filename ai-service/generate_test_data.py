"""
Generate Sample FRA Boundary Shapefiles for Testing
Creates realistic test data for Maharashtra tribal areas
"""

import geopandas as gpd
from shapely.geometry import Polygon, Point
import pandas as pd
import random
from pathlib import Path
import json

def generate_sample_fra_boundaries():
    """
    Generate sample FRA boundary shapefiles for testing
    Based on actual Maharashtra tribal districts
    """
    
    # Sample villages in Maharashtra tribal areas (Gadchiroli, Chandrapur, Gondia)
    sample_villages = [
        {
            'village_name': 'Kheda',
            'patta_number': 'MH/GDC/2023/001',
            'holder_name': 'Kheda Gram Sabha',
            'area_hectares': 245.5,
            'district': 'Gadchiroli',
            'state': 'Maharashtra',
            'grant_date': '2023-03-15',
            'right_type': 'Community Forest Resource',
            'population': 1250,
            'tribal_population': 980,
            'center_lat': 19.8,
            'center_lon': 80.2
        },
        {
            'village_name': 'Etapalli',
            'patta_number': 'MH/GDC/2023/002',
            'holder_name': 'Etapalli Forest Rights Committee',
            'area_hectares': 312.8,
            'district': 'Gadchiroli',
            'state': 'Maharashtra',
            'grant_date': '2023-04-20',
            'right_type': 'Community Forest Resource',
            'population': 1580,
            'tribal_population': 1320,
            'center_lat': 19.95,
            'center_lon': 80.05
        },
        {
            'village_name': 'Bhamragad',
            'patta_number': 'MH/GDC/2023/003',
            'holder_name': 'Bhamragad Tribal Cooperative',
            'area_hectares': 428.3,
            'district': 'Gadchiroli',
            'state': 'Maharashtra',
            'grant_date': '2023-05-10',
            'right_type': 'Community Forest Resource',
            'population': 2100,
            'tribal_population': 1890,
            'center_lat': 19.7,
            'center_lon': 80.3
        },
        {
            'village_name': 'Chamorshi',
            'patta_number': 'MH/CDP/2023/004',
            'holder_name': 'Chamorshi Gram Sabha',
            'area_hectares': 189.2,
            'district': 'Chandrapur',
            'state': 'Maharashtra',
            'grant_date': '2023-06-05',
            'right_type': 'Community Forest Resource',
            'population': 950,
            'tribal_population': 720,
            'center_lat': 20.1,
            'center_lon': 79.8
        },
        {
            'village_name': 'Mul',
            'patta_number': 'MH/CDP/2023/005',
            'holder_name': 'Mul Forest Rights Committee',
            'area_hectares': 267.9,
            'district': 'Chandrapur',
            'state': 'Maharashtra',
            'grant_date': '2023-07-15',
            'right_type': 'Community Forest Resource',
            'population': 1340,
            'tribal_population': 1050,
            'center_lat': 20.05,
            'center_lon': 79.95
        },
        {
            'village_name': 'Rajura',
            'patta_number': 'MH/CDP/2023/006',
            'holder_name': 'Rajura Tribal Welfare Society',
            'area_hectares': 198.7,
            'district': 'Chandrapur',
            'state': 'Maharashtra',
            'grant_date': '2023-08-22',
            'right_type': 'Individual Forest Rights',
            'population': 1100,
            'tribal_population': 850,
            'center_lat': 19.85,
            'center_lon': 79.9
        },
        {
            'village_name': 'Deori',
            'patta_number': 'MH/GON/2023/007',
            'holder_name': 'Deori Gram Sabha',
            'area_hectares': 354.2,
            'district': 'Gondia',
            'state': 'Maharashtra',
            'grant_date': '2023-09-10',
            'right_type': 'Community Forest Resource',
            'population': 1680,
            'tribal_population': 1290,
            'center_lat': 21.5,
            'center_lon': 80.1
        },
        {
            'village_name': 'Salekasa',
            'patta_number': 'MH/GON/2023/008',
            'holder_name': 'Salekasa Forest Rights Committee',
            'area_hectares': 276.5,
            'district': 'Gondia',
            'state': 'Maharashtra',
            'grant_date': '2023-10-01',
            'right_type': 'Community Forest Resource',
            'population': 1420,
            'tribal_population': 1150,
            'center_lat': 21.45,
            'center_lon': 80.15
        }
    ]
    
    # Create polygons for each village (approximate boundaries)
    geometries = []
    for village in sample_villages:
        # Create a polygon around the center point
        # Size based on area (rough approximation)
        center_lon = village['center_lon']
        center_lat = village['center_lat']
        
        # Calculate approximate polygon size from hectares
        # 1 hectare ≈ 0.01 km² ≈ 0.0001 degrees (rough approximation)
        size = (village['area_hectares'] * 0.0001) ** 0.5
        
        # Create irregular polygon (more realistic than perfect square)
        angles = [random.uniform(0, 360) for _ in range(8)]
        angles.sort()
        
        coords = []
        for angle in angles:
            import math
            rad = math.radians(angle)
            radius = size * random.uniform(0.8, 1.2)
            lon = center_lon + radius * math.cos(rad)
            lat = center_lat + radius * math.sin(rad)
            coords.append((lon, lat))
        
        # Close the polygon
        coords.append(coords[0])
        
        polygon = Polygon(coords)
        geometries.append(polygon)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(sample_villages, geometry=geometries, crs='EPSG:4326')
    
    return gdf


def save_shapefile(gdf, output_path='uploads/shapefiles/sample_fra_boundaries'):
    """Save GeoDataFrame as shapefile"""
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    gdf.to_file(f"{output_path}.shp")
    print(f"✓ Shapefile saved: {output_path}.shp")
    print(f"  Records: {len(gdf)}")
    print(f"  Total area: {gdf['area_hectares'].sum():.2f} hectares")
    
    return output_path


def create_zip_file(shp_path):
    """Create ZIP file containing all shapefile components"""
    import zipfile
    from pathlib import Path
    
    base_path = Path(shp_path)
    zip_path = base_path.with_suffix('.zip')
    
    # Files to include in ZIP
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.cpg']
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for ext in extensions:
            file_path = base_path.with_suffix(ext)
            if file_path.exists():
                zipf.write(file_path, file_path.name)
    
    print(f"✓ ZIP created: {zip_path}")
    return zip_path


def generate_additional_test_data():
    """Generate additional test data files"""
    
    # Sample claims data (to test spatial joins)
    claims = [
        {
            'claim_id': 'CLM-2024-001',
            'applicant_name': 'Rama Gond',
            'latitude': 19.81,
            'longitude': 80.21,
            'status': 'pending',
            'claim_type': 'individual'
        },
        {
            'claim_id': 'CLM-2024-002',
            'applicant_name': 'Sita Madavi',
            'latitude': 19.96,
            'longitude': 80.06,
            'status': 'approved',
            'claim_type': 'community'
        },
        {
            'claim_id': 'CLM-2024-003',
            'applicant_name': 'Laxman Pardhi',
            'latitude': 19.71,
            'longitude': 80.31,
            'status': 'pending',
            'claim_type': 'individual'
        }
    ]
    
    claims_path = Path('uploads/test_data/sample_claims.json')
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(claims_path, 'w') as f:
        json.dump(claims, f, indent=2)
    
    print(f"✓ Claims data saved: {claims_path}")
    
    return claims


if __name__ == "__main__":
    print("=" * 60)
    print("FRA Boundary Shapefile Generator")
    print("=" * 60)
    
    print("\n[1/3] Generating sample FRA boundaries...")
    gdf = generate_sample_fra_boundaries()
    
    print("\n[2/3] Saving shapefile...")
    shp_path = save_shapefile(gdf)
    
    print("\n[3/3] Creating ZIP file...")
    zip_path = create_zip_file(shp_path)
    
    print("\n[4/4] Generating additional test data...")
    claims = generate_additional_test_data()
    
    print("\n" + "=" * 60)
    print("✅ Test data generation complete!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  1. Shapefile: {shp_path}.shp")
    print(f"  2. ZIP file: {zip_path}")
    print(f"  3. Sample claims: uploads/test_data/sample_claims.json")
    print(f"\nVillages created: {len(gdf)}")
    print(f"Districts covered: {gdf['district'].unique().tolist()}")
    print(f"\nYou can now test:")
    print(f"  1. Upload {zip_path} via API")
    print(f"  2. Test spatial join with claims")
    print(f"  3. Visualize boundaries on map")
    print("=" * 60)
