"""
🔗 Blockchain Duplicate Detection Test
Tests the blockchain service's ability to prevent duplicate FRA claims
"""

import requests
import json
import hashlib
from datetime import datetime

# Service URLs
AI_SERVICE = "http://localhost:8000"
BLOCKCHAIN_SERVICE = "http://localhost:8001"

def create_claim_hash(claim_data):
    """Create unique hash for claim"""
    claim_string = f"{claim_data['aadhaar']}{claim_data['gps']}{claim_data['area_hectares']}"
    return hashlib.sha256(claim_string.encode()).hexdigest()

def test_1_submit_new_claim():
    """Test 1: Submit a new claim (should succeed)"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Submit New Claim")
    print("="*60)
    
    claim = {
        "claimId": "FRA/BAL/TEST001/2024",
        "claimant_name": "Ram Singh Maravi",
        "aadhaar": "1234-5678-9012",
        "village": "Kanha Village",
        "district": "Balaghat",
        "state": "Madhya Pradesh",
        "gps": "21.8046, 80.1887",
        "area_hectares": 12.4,
        "claim_type": "IFR",
        "tribal_group": "Gond"
    }
    
    # Create hash
    claim["aadhaar_hash"] = hashlib.sha256(claim["aadhaar"].encode()).hexdigest()
    claim["claim_hash"] = create_claim_hash(claim)
    
    try:
        print(f"\n📝 Submitting claim:")
        print(f"   Claimant: {claim['claimant_name']}")
        print(f"   GPS: {claim['gps']}")
        print(f"   Area: {claim['area_hectares']} hectares")
        
        # Submit to blockchain
        response = requests.post(
            f"{BLOCKCHAIN_SERVICE}/api/blockchain/submit-claim",
            json=claim,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS: Claim submitted")
            print(f"   ClaimID: {result.get('claimId', 'N/A')}")
            print(f"   Blockchain Hash: {result.get('blockHash', 'N/A')[:16]}...")
            print(f"   Timestamp: {result.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"\n❌ FAILED: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️ WARNING: Blockchain service not responding")
        print("   Make sure blockchain service is running on port 8001")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_2_duplicate_same_person():
    """Test 2: Submit duplicate claim (same person, same land)"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Duplicate Claim Detection (Same Person)")
    print("="*60)
    
    # Same claim as Test 1
    claim = {
        "claimId": "FRA/BAL/TEST002/2024",  # Different ID
        "claimant_name": "Ram Singh Maravi",  # SAME PERSON
        "aadhaar": "1234-5678-9012",  # SAME AADHAAR
        "village": "Kanha Village",
        "district": "Balaghat",
        "state": "Madhya Pradesh",
        "gps": "21.8045, 80.1886",  # ALMOST SAME GPS (99% overlap)
        "area_hectares": 12.0,  # Slightly different
        "claim_type": "IFR",
        "tribal_group": "Gond"
    }
    
    claim["aadhaar_hash"] = hashlib.sha256(claim["aadhaar"].encode()).hexdigest()
    claim["claim_hash"] = create_claim_hash(claim)
    
    try:
        print(f"\n📝 Submitting duplicate claim:")
        print(f"   Claimant: {claim['claimant_name']} (SAME AS TEST 1)")
        print(f"   GPS: {claim['gps']} (99% overlap with TEST 1)")
        print(f"   Area: {claim['area_hectares']} hectares")
        
        response = requests.post(
            f"{BLOCKCHAIN_SERVICE}/api/blockchain/submit-claim",
            json=claim,
            timeout=10
        )
        
        if response.status_code == 400 or response.status_code == 409:
            result = response.json()
            print(f"\n✅ DUPLICATE DETECTED! (Expected behavior)")
            print(f"   Reason: {result.get('reason', 'N/A')}")
            print(f"   Existing Claim: {result.get('existingClaimId', 'N/A')}")
            print(f"   Status: {result.get('existingStatus', 'N/A')}")
            return True
        elif response.status_code == 200:
            print(f"\n❌ FAILED: Duplicate was NOT detected!")
            print(f"   This is a security issue - blockchain should reject duplicates")
            return False
        else:
            print(f"\n⚠️ UNEXPECTED RESPONSE: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️ WARNING: Blockchain service not responding")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_3_duplicate_scheme():
    """Test 3: Apply for same scheme twice"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Duplicate Scheme Detection")
    print("="*60)
    
    scheme_application = {
        "claimId": "FRA/BAL/TEST001/2024",
        "schemeId": "PM-KISAN",
        "schemeName": "PM Kisan Samman Nidhi",
        "benefitAmount": "₹6,000/year",
        "applicant_aadhaar_hash": hashlib.sha256("1234-5678-9012".encode()).hexdigest()
    }
    
    try:
        print(f"\n📝 First scheme application:")
        print(f"   ClaimID: {scheme_application['claimId']}")
        print(f"   Scheme: {scheme_application['schemeName']}")
        print(f"   Benefit: {scheme_application['benefitAmount']}")
        
        # First application
        response1 = requests.post(
            f"{BLOCKCHAIN_SERVICE}/api/blockchain/apply-scheme",
            json=scheme_application,
            timeout=10
        )
        
        if response1.status_code == 200:
            print(f"\n✅ First application approved")
        
        # Try to apply again
        print(f"\n📝 Second scheme application (DUPLICATE):")
        response2 = requests.post(
            f"{BLOCKCHAIN_SERVICE}/api/blockchain/apply-scheme",
            json=scheme_application,
            timeout=10
        )
        
        if response2.status_code == 400 or response2.status_code == 409:
            result = response2.json()
            print(f"\n✅ DUPLICATE SCHEME DETECTED! (Expected behavior)")
            print(f"   Reason: {result.get('reason', 'N/A')}")
            print(f"   Claimed Date: {result.get('claimed_date', 'N/A')}")
            print(f"   Benefits Received: {result.get('benefits_received', 'N/A')}")
            return True
        elif response2.status_code == 200:
            print(f"\n❌ FAILED: Duplicate scheme was NOT detected!")
            return False
        else:
            print(f"\n⚠️ UNEXPECTED RESPONSE: {response2.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️ WARNING: Blockchain service not responding")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_4_land_overlap():
    """Test 4: Different person claiming overlapping land"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Land Overlap Detection")
    print("="*60)
    
    claim = {
        "claimId": "FRA/BAL/TEST003/2024",
        "claimant_name": "Lakhan Singh Gond",  # DIFFERENT PERSON
        "aadhaar": "9876-5432-1098",  # Different Aadhaar
        "village": "Kanha Village",
        "district": "Balaghat",
        "state": "Madhya Pradesh",
        "gps": "21.8048, 80.1889",  # Overlapping with TEST001
        "area_hectares": 10.5,
        "claim_type": "CFR",
        "tribal_group": "Gond"
    }
    
    claim["aadhaar_hash"] = hashlib.sha256(claim["aadhaar"].encode()).hexdigest()
    claim["claim_hash"] = create_claim_hash(claim)
    
    try:
        print(f"\n📝 Submitting claim with overlapping land:")
        print(f"   Claimant: {claim['claimant_name']} (Different person)")
        print(f"   GPS: {claim['gps']} (Overlaps with TEST 1)")
        print(f"   Area: {claim['area_hectares']} hectares")
        
        response = requests.post(
            f"{BLOCKCHAIN_SERVICE}/api/blockchain/submit-claim",
            json=claim,
            timeout=10
        )
        
        # Land overlap might be flagged or forwarded for verification
        if response.status_code == 202:  # Accepted but flagged
            result = response.json()
            print(f"\n✅ LAND OVERLAP FLAGGED! (Expected behavior)")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Overlap: {result.get('overlap_percentage', 'N/A')}%")
            print(f"   Action: {result.get('action', 'N/A')}")
            return True
        elif response.status_code == 400 or response.status_code == 409:
            result = response.json()
            print(f"\n✅ LAND OVERLAP REJECTED! (Expected behavior)")
            print(f"   Reason: {result.get('reason', 'N/A')}")
            return True
        elif response.status_code == 200:
            print(f"\n⚠️ WARNING: Overlapping claim accepted without flagging")
            print(f"   Should be flagged for Gram Sabha verification")
            return False
        else:
            print(f"\n⚠️ UNEXPECTED RESPONSE: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n⚠️ WARNING: Blockchain service not responding")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_blockchain_health():
    """Check if blockchain service is online"""
    print("\n" + "="*60)
    print("🔍 Checking Blockchain Service Health")
    print("="*60)
    
    try:
        response = requests.get(f"{BLOCKCHAIN_SERVICE}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Blockchain Service: ONLINE")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Port: 8001")
            return True
        else:
            print(f"\n❌ Blockchain Service: ERROR {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Blockchain Service: OFFLINE")
        print(f"   Cannot connect to {BLOCKCHAIN_SERVICE}")
        print(f"\n💡 To start blockchain service:")
        print(f"   cd blockchain-main")
        print(f"   npm start")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def test_ai_service_health():
    """Check if AI service is online"""
    print("\n" + "="*60)
    print("🔍 Checking AI Service Health")
    print("="*60)
    
    try:
        response = requests.get(f"{AI_SERVICE}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ AI Service: ONLINE")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Port: 8000")
            return True
        else:
            print(f"\n❌ AI Service: ERROR {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ AI Service: OFFLINE")
        print(f"   Cannot connect to {AI_SERVICE}")
        print(f"\n💡 To start AI service:")
        print(f"   cd ai-service")
        print(f"   python main_v2.py")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False

def main():
    """Run all blockchain tests"""
    print("\n" + "="*60)
    print("🔗 BLOCKCHAIN ANTI-FRAUD SYSTEM - TEST SUITE")
    print("="*60)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Health checks
    ai_healthy = test_ai_service_health()
    blockchain_healthy = test_blockchain_health()
    
    if not blockchain_healthy:
        print("\n❌ TESTS ABORTED: Blockchain service must be running")
        print("\n📚 See: BLOCKCHAIN_ANTI_FRAUD_SYSTEM.md for setup instructions")
        return
    
    # Run tests
    results = {
        "Test 1 - New Claim": False,
        "Test 2 - Duplicate Person": False,
        "Test 3 - Duplicate Scheme": False,
        "Test 4 - Land Overlap": False
    }
    
    results["Test 1 - New Claim"] = test_1_submit_new_claim()
    results["Test 2 - Duplicate Person"] = test_2_duplicate_same_person()
    results["Test 3 - Duplicate Scheme"] = test_3_duplicate_scheme()
    results["Test 4 - Land Overlap"] = test_4_land_overlap()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Blockchain anti-fraud system working correctly!")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed. Check blockchain implementation.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
