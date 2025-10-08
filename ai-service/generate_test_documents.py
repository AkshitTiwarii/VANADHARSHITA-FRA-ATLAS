from faker import Faker
from datetime import datetime, timedelta
import random
import json
import os

fake = Faker('en_IN')  # Indian locale

def generate_fra_claim():
    """Generate realistic FRA claim data"""
    
    # Indian tribal names
    tribal_surnames = ['Maravi', 'Gond', 'Baiga', 'Korku', 'Bhil', 'Santhal', 'Munda', 'Oraon', 'Kharia', 'Ho']
    
    # Villages in tribal areas (Madhya Pradesh, Odisha, Tripura, Telangana)
    villages = [
        'Kanha Village', 'Pench Village', 'Amarkantak', 'Mandla', 'Dindori',
        'Sukma Village', 'Bijapur Village', 'Dantewada', 'Narayanpur',
        'Gadchiroli Village', 'Balaghat Village', 'Kanker Village',
        'Simlipal Village', 'Mayurbhanj', 'Keonjhar', 'Sundargarh',
        'Khowai', 'Dhalai', 'Gomati', 'Sipahijala',
        'Adilabad', 'Warangal', 'Khammam', 'Bhadradri'
    ]
    
    districts = {
        # Madhya Pradesh
        'Balaghat': {'lat': 21.8046, 'lng': 80.1887, 'state': 'Madhya Pradesh'},
        'Mandla': {'lat': 22.5978, 'lng': 80.3711, 'state': 'Madhya Pradesh'},
        'Dindori': {'lat': 22.9420, 'lng': 81.0792, 'state': 'Madhya Pradesh'},
        'Seoni': {'lat': 22.0853, 'lng': 79.5502, 'state': 'Madhya Pradesh'},
        
        # Odisha
        'Mayurbhanj': {'lat': 21.9320, 'lng': 86.7268, 'state': 'Odisha'},
        'Keonjhar': {'lat': 21.6291, 'lng': 85.5825, 'state': 'Odisha'},
        'Sundargarh': {'lat': 22.1172, 'lng': 84.0266, 'state': 'Odisha'},
        'Kandhamal': {'lat': 20.1333, 'lng': 84.1333, 'state': 'Odisha'},
        
        # Tripura
        'Khowai': {'lat': 24.0633, 'lng': 91.6050, 'state': 'Tripura'},
        'Dhalai': {'lat': 23.8366, 'lng': 91.9387, 'state': 'Tripura'},
        'Gomati': {'lat': 23.5317, 'lng': 91.4717, 'state': 'Tripura'},
        
        # Telangana
        'Adilabad': {'lat': 19.6637, 'lng': 78.5310, 'state': 'Telangana'},
        'Warangal': {'lat': 17.9689, 'lng': 79.5941, 'state': 'Telangana'},
        'Khammam': {'lat': 17.2473, 'lng': 80.1514, 'state': 'Telangana'},
        'Bhadradri': {'lat': 17.5578, 'lng': 80.8936, 'state': 'Telangana'}
    }
    
    district_name = random.choice(list(districts.keys()))
    district_info = districts[district_name]
    
    # Generate GPS coordinates (nearby district center)
    lat = district_info['lat'] + random.uniform(-0.5, 0.5)
    lng = district_info['lng'] + random.uniform(-0.5, 0.5)
    
    claim = {
        "claimant_name": f"{fake.first_name()} {random.choice(tribal_surnames)}",
        "father_name": f"{fake.first_name()} {random.choice(tribal_surnames)}",
        "village": random.choice(villages),
        "district": district_name,
        "state": district_info['state'],
        "gps_coordinates": f"{lat:.4f}, {lng:.4f}",
        "area_hectares": round(random.uniform(1.5, 25.0), 2),
        "claim_type": random.choice(["IFR", "CFR", "CR"]),
        "forest_type": random.choice(["Dense Forest", "Open Forest", "Mixed Forest", "Bamboo Forest", "Sal Forest"]),
        "claim_number": f"FRA/{district_name[:3].upper()}/{random.randint(1000, 9999)}/2024",
        "submission_date": (datetime.now() - timedelta(days=random.randint(1, 730))).strftime("%Y-%m-%d"),
        "tribal_group": random.choice(["Gond", "Baiga", "Korku", "Bhil", "Santhal", "Munda", "Oraon", "Kharia"]),
        "family_members": random.randint(3, 12),
        "phone": f"+91{random.randint(7000000000, 9999999999)}",
        "has_water_source": random.choice([True, False]),
        "has_agriculture": random.choice([True, False]),
        "status": random.choice(["pending", "approved", "under_review", "disputed"])
    }
    
    return claim

def generate_text_document(claim):
    """Generate realistic FRA document text"""
    
    text = f"""
═══════════════════════════════════════════════════════════════
                    FOREST RIGHTS ACT - 2006
            INDIVIDUAL FOREST RIGHTS CLAIM FORM
═══════════════════════════════════════════════════════════════

Claim Number: {claim['claim_number']}
Date of Submission: {claim['submission_date']}
Status: {claim['status'].upper()}

═══════════════════════════════════════════════════════════════
                      CLAIMANT DETAILS
═══════════════════════════════════════════════════════════════

Name of Claimant       : {claim['claimant_name']}
Father's/Husband's Name: {claim['father_name']}
Tribal Group           : {claim['tribal_group']}
Total Family Members   : {claim['family_members']}
Contact Number         : {claim['phone']}

═══════════════════════════════════════════════════════════════
                      LOCATION DETAILS
═══════════════════════════════════════════════════════════════

Village Name : {claim['village']}
District     : {claim['district']}
State        : {claim['state']}
GPS Location : {claim['gps_coordinates']}

═══════════════════════════════════════════════════════════════
                        CLAIM DETAILS
═══════════════════════════════════════════════════════════════

Type of Claim        : {claim['claim_type']}
Area Claimed         : {claim['area_hectares']} hectares
Forest Type          : {claim['forest_type']}

═══════════════════════════════════════════════════════════════
                   ADDITIONAL INFORMATION
═══════════════════════════════════════════════════════════════

Water Source Available : {'Yes - Pond/Stream nearby' if claim['has_water_source'] else 'No'}
Agricultural Activity  : {'Yes - Cultivating crops' if claim['has_agriculture'] else 'No - Forest dwelling only'}

═══════════════════════════════════════════════════════════════
                    DECLARATION
═══════════════════════════════════════════════════════════════

I hereby declare that the information provided above is true and 
correct to the best of my knowledge. I am a member of the Scheduled 
Tribe community and have been residing in the forest area for more 
than three generations.

Signature/Thumb Impression: _______________
Date: {claim['submission_date']}

═══════════════════════════════════════════════════════════════
                 FOR OFFICIAL USE ONLY
═══════════════════════════════════════════════════════════════

Received Date    : {claim['submission_date']}
Verification     : Pending
Forest Officer   : __________________
Revenue Officer  : __________________
Gram Sabha       : __________________

═══════════════════════════════════════════════════════════════
"""
    
    return text

def generate_test_dataset(count=50):
    """Generate multiple test claims"""
    claims = []
    for i in range(count):
        claims.append(generate_fra_claim())
    return claims

def save_to_json(claims, filename="test_fra_claims.json"):
    """Save test data to JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(claims, indent=2, fp=f, ensure_ascii=False)
    print(f"✅ Generated {len(claims)} test claims → {filename}")

if __name__ == "__main__":
    print("\n🌲 FRA Test Data Generator")
    print("═" * 60)
    
    # Generate test claims
    print("\n📊 Generating test claims...")
    claims = generate_test_dataset(50)
    
    # Save to JSON
    save_to_json(claims, "test_fra_claims.json")
    
    # Generate sample text documents
    print("\n📝 Generating sample text documents...")
    os.makedirs("test_documents", exist_ok=True)
    
    for i, claim in enumerate(claims[:10]):  # First 10 as samples
        text = generate_text_document(claim)
        filename = f"test_documents/sample_claim_{i+1}_{claim['district']}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  ✅ {filename}")
    
    # Generate statistics
    print(f"\n📊 TEST DATA STATISTICS")
    print("═" * 60)
    
    states_count = {}
    claim_types_count = {}
    status_count = {}
    
    for claim in claims:
        states_count[claim['state']] = states_count.get(claim['state'], 0) + 1
        claim_types_count[claim['claim_type']] = claim_types_count.get(claim['claim_type'], 0) + 1
        status_count[claim['status']] = status_count.get(claim['status'], 0) + 1
    
    print("\n📍 By State:")
    for state, count in sorted(states_count.items()):
        print(f"  {state}: {count} claims")
    
    print("\n📋 By Claim Type:")
    for ctype, count in sorted(claim_types_count.items()):
        print(f"  {ctype}: {count} claims")
    
    print("\n✅ By Status:")
    for status, count in sorted(status_count.items()):
        print(f"  {status}: {count} claims")
    
    print("\n" + "═" * 60)
    print("✅ Test data generation complete!")
    print(f"   - {len(claims)} claims in test_fra_claims.json")
    print(f"   - 10 sample text documents in test_documents/")
    print(f"   - Covering 4 states: MP, Odisha, Tripura, Telangana")
    print("═" * 60 + "\n")
