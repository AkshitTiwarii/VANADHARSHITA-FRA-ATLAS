"""
Sample data seeder for FRA Atlas MongoDB
Creates villages, forest claims, and other necessary data for demonstration
"""

import pymongo
from pymongo import MongoClient
from datetime import datetime, timezone
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['fra_db']

def seed_villages():
    """Create sample village data"""
    villages_collection = db.villages
    
    # Clear existing data
    villages_collection.delete_many({})
    
    sample_villages = [
        {
            "id": "village_001",
            "name": "Banswara",
            "state": "Madhya Pradesh",
            "district": "Chhindwara",
            "tehsil": "Chourai",
            "village_code": "MP001",
            "population": 1250,
            "total_area": 800.5,
            "forest_area": 450.5,
            "coordinates": {
                "type": "Point",
                "coordinates": [78.9629, 22.0697]  # [longitude, latitude]
            },
            "tribal_population": 850,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "village_002", 
            "name": "Khermai",
            "state": "Madhya Pradesh",
            "district": "Chhindwara",
            "tehsil": "Chourai", 
            "village_code": "MP002",
            "population": 892,
            "total_area": 650.8,
            "forest_area": 320.8,
            "coordinates": {
                "type": "Point",
                "coordinates": [78.9729, 22.0797]  # [longitude, latitude]
            },
            "tribal_population": 645,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "village_003",
            "name": "Dhangaon",
            "state": "Maharashtra", 
            "district": "Gadchiroli",
            "tehsil": "Etapalli",
            "village_code": "MH001",
            "population": 1540,
            "total_area": 950.2,
            "forest_area": 720.3,
            "coordinates": {
                "type": "Point",
                "coordinates": [80.0982, 19.8762]  # [longitude, latitude]
            },
            "tribal_population": 1120,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "village_004",
            "name": "Mendha-Lekha",
            "state": "Maharashtra",
            "district": "Gadchiroli", 
            "tehsil": "Etapalli",
            "village_code": "MH002", 
            "population": 430,
            "total_area": 1800.5,
            "forest_area": 1650.2,
            "coordinates": {
                "type": "Point",
                "coordinates": [80.1182, 19.8562]  # [longitude, latitude]
            },
            "tribal_population": 380,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "village_005",
            "name": "Jamguri",
            "state": "Assam",
            "district": "Golaghat",
            "tehsil": "Golaghat",
            "village_code": "AS001",
            "population": 920,
            "total_area": 580.8,
            "forest_area": 340.5,
            "coordinates": {
                "type": "Point",
                "coordinates": [93.9474, 26.1445]  # [longitude, latitude]
            },
            "tribal_population": 680,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    result = villages_collection.insert_many(sample_villages)
    print(f"✅ Inserted {len(result.inserted_ids)} villages")

def seed_forest_claims():
    """Create sample forest claims data"""
    claims_collection = db.forest_claims
    
    # Clear existing data
    claims_collection.delete_many({})
    
    sample_claims = [
        {
            "id": "claim_001",
            "claim_number": "FRA-20240901-A1B2C3D4",
            "village_id": "village_001",
            "village_name": "Banswara",
            "claim_type": "Individual Forest Rights",
            "beneficiary_name": "Rajesh Kumar",
            "beneficiary_father_name": "Ramesh Kumar",
            "area_claimed": 2.5,
            "coordinates": {
                "type": "Point",
                "coordinates": [78.9629, 22.0697]  # [longitude, latitude]
            },
            "status": "pending",
            "submitted_date": datetime(2024, 9, 1, 10, 30, 0, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "claim_002",
            "claim_number": "FRA-20240905-E5F6G7H8",
            "village_id": "village_002", 
            "village_name": "Khermai",
            "claim_type": "Community Forest Resource",
            "beneficiary_name": "Priya Devi",
            "beneficiary_father_name": "Govind Singh",
            "area_claimed": 1.8,
            "coordinates": {
                "type": "Point",
                "coordinates": [78.9729, 22.0797]  # [longitude, latitude]
            },
            "status": "approved",
            "submitted_date": datetime(2024, 9, 5, 14, 15, 0, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "claim_003",
            "claim_number": "FRA-20240910-I9J0K1L2",
            "village_id": "village_003",
            "village_name": "Dhangaon", 
            "claim_type": "Community Forest Resource",
            "beneficiary_name": "Santosh Madavi",
            "beneficiary_father_name": "Dhondu Madavi",
            "area_claimed": 5.2,
            "coordinates": {
                "type": "Point",
                "coordinates": [80.0982, 19.8762]  # [longitude, latitude]
            },
            "status": "disputed",
            "submitted_date": datetime(2024, 9, 10, 9, 45, 0, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "claim_004",
            "claim_number": "FRA-20240912-M3N4O5P6", 
            "village_id": "village_004",
            "village_name": "Mendha-Lekha",
            "claim_type": "Community Forest Resource",
            "beneficiary_name": "Devidas Tofa",
            "beneficiary_father_name": "Ramesh Tofa",
            "area_claimed": 12.5,
            "coordinates": {
                "type": "Point",
                "coordinates": [80.1182, 19.8562]  # [longitude, latitude]
            },
            "status": "approved",
            "submitted_date": datetime(2024, 9, 12, 11, 20, 0, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "claim_005",
            "claim_number": "FRA-20240913-Q7R8S9T0",
            "village_id": "village_005",
            "village_name": "Jamguri",
            "claim_type": "Individual Forest Rights",
            "beneficiary_name": "Ritu Borah",
            "beneficiary_father_name": "Mohan Borah", 
            "area_claimed": 3.1,
            "coordinates": {
                "type": "Point",
                "coordinates": [93.9474, 26.1445]  # [longitude, latitude]
            },
            "status": "pending",
            "submitted_date": datetime(2024, 9, 13, 16, 10, 0, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    result = claims_collection.insert_many(sample_claims)
    print(f"✅ Inserted {len(result.inserted_ids)} forest claims")

def create_indexes():
    """Create necessary indexes for performance"""
    # Village indexes
    db.villages.create_index([("village_id", 1)])
    db.villages.create_index([("state", 1)])
    db.villages.create_index([("district", 1)])
    db.villages.create_index([("coordinates", "2dsphere")])
    
    # Claims indexes  
    db.forest_claims.create_index([("claim_number", 1)])
    db.forest_claims.create_index([("village_id", 1)])
    db.forest_claims.create_index([("status", 1)])
    db.forest_claims.create_index([("coordinates", "2dsphere")])
    
    print("✅ Created database indexes")

if __name__ == "__main__":
    print("🌱 Seeding FRA Atlas database...")
    
    # Seed all collections
    seed_villages()
    seed_forest_claims()
    create_indexes()
    
    # Print summary
    villages_count = db.villages.count_documents({})
    claims_count = db.forest_claims.count_documents({})
    
    print(f"\n📊 Database Summary:")
    print(f"   Villages: {villages_count}")
    print(f"   Forest Claims: {claims_count}")
    print(f"\n✅ Database seeding completed successfully!")
    
    client.close()