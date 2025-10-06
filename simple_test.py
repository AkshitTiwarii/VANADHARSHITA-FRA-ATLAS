"""
Simple Service Test for FRA Atlas
Tests all backend services without frontend
"""

import requests
import json
import time

def test_service(name, url, timeout=5):
    """Test a service endpoint"""
    print(f"\n[Testing] {name}...")
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"[PASS] {name} - Status: {response.status_code}")
            return True, response.json()
        else:
            print(f"[FAIL] {name} - Status: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {name} - Service not running")
        return False, None
    except Exception as e:
        print(f"[FAIL] {name} - Error: {e}")
        return False, None

def test_post_service(name, url, data, timeout=10):
    """Test a POST endpoint"""
    print(f"\n[Testing] {name}...")
    try:
        response = requests.post(url, json=data, timeout=timeout)
        if response.status_code == 200:
            print(f"[PASS] {name} - Status: {response.status_code}")
            return True, response.json()
        elif response.status_code == 503:
            print(f"[WARN] {name} - Service unavailable (503)")
            return False, None
        else:
            print(f"[FAIL] {name} - Status: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {name} - Cannot connect")
        return False, None
    except Exception as e:
        print(f"[FAIL] {name} - Error: {e}")
        return False, None

print("="*70)
print("FRA ATLAS SERVICE TEST SUITE")
print("="*70)

results = []

# Test 1: AI Service Health
print("\n" + "="*70)
print("TEST 1: AI SERVICE HEALTH")
print("="*70)
passed, data = test_service("AI Service Health", "http://localhost:8000/health")
results.append(passed)
if data:
    print(f"  Components: {list(data.get('components', {}).keys())}")

# Test 2: AI Service Stats
print("\n" + "="*70)
print("TEST 2: AI SERVICE STATISTICS")
print("="*70)
passed, data = test_service("Service Stats", "http://localhost:8000/api/stats")
results.append(passed)
if data:
    print(f"  Total Jobs: {data.get('total_jobs', 0)}")
    print(f"  Version: {data.get('version', 'N/A')}")
    print(f"  Features: {data.get('features', {})}")

# Test 3: GIS Dependencies
print("\n" + "="*70)
print("TEST 3: GIS FEATURES")
print("="*70)
passed, data = test_service("GIS Dependencies", "http://localhost:8000/api/gis/check-dependencies")
results.append(passed)
if data:
    print(f"  Status: {data.get('status', 'N/A')}")

# Test 4: External GIS Layers
passed, data = test_service("External GIS Layers", "http://localhost:8000/api/gis/external-layers")
results.append(passed)
if data:
    catalog = data.get('catalog', {})
    recommended = data.get('recommended', [])
    total_layers = sum(len(layers) for layers in catalog.values())
    print(f"  Total Layers: {total_layers}")
    print(f"  Categories: {len(catalog)}")
    print(f"  Recommended: {len(recommended)}")

# Test 5: Satellite Analysis
print("\n" + "="*70)
print("TEST 5: SATELLITE ANALYSIS")
print("="*70)
test_coords = {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "radius": 500
}
passed, data = test_post_service("Satellite Analysis", 
                                  "http://localhost:8000/api/analyze-satellite",
                                  test_coords,
                                  timeout=30)
results.append(passed)
if data and data.get('success'):
    ndvi = data.get('ndvi', {})
    land_cover = data.get('land_cover', {})
    print(f"  NDVI: {ndvi.get('value', 'N/A')}")
    print(f"  Health: {ndvi.get('health', 'N/A')}")
    print(f"  Forest Cover: {land_cover.get('forest_cover_percentage', 0)}%")

# Test 6: Blockchain Health
print("\n" + "="*70)
print("TEST 6: BLOCKCHAIN CONNECTION")
print("="*70)
passed, data = test_service("Blockchain Health", "http://localhost:8000/api/blockchain/health")
results.append(passed)
if data:
    print(f"  Status: {data.get('status', 'N/A')}")
    print(f"  Message: {data.get('message', 'N/A')}")

# Test 7: Blockchain Submission
test_verification = {
    "documentId": f"TEST-{int(time.time())}",
    "documentHash": "test_hash_abc123",
    "documentType": "test_claim",
    "metadata": {"test": True}
}
passed, data = test_post_service("Blockchain Submission",
                                  "http://localhost:8000/api/blockchain/submit-verification",
                                  test_verification)
results.append(passed)
if data and data.get('transactionId'):
    print(f"  Transaction ID: {data.get('transactionId')}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
total = len(results)
passed_count = sum(results)
failed_count = total - passed_count
percentage = (passed_count / total * 100) if total > 0 else 0

print(f"\nTotal Tests: {total}")
print(f"Passed: {passed_count}")
print(f"Failed: {failed_count}")
print(f"Success Rate: {percentage:.1f}%")

if percentage == 100:
    print("\n[SUCCESS] ALL TESTS PASSED!")
elif percentage >= 70:
    print("\n[PARTIAL] MOST SERVICES WORKING")
else:
    print("\n[WARNING] MULTIPLE SERVICES NEED ATTENTION")

print("\n" + "="*70)
print("SERVICES STATUS:")
print("="*70)
print("AI Service (Port 8000):", "[RUNNING]" if results[0] else "[STOPPED]")
print("GIS Features:", "[OK]" if len(results) > 2 and results[2] else "[NEEDS ATTENTION]")
print("Satellite Analysis:", "[OK]" if len(results) > 4 and results[4] else "[NEEDS ATTENTION]")
print("Blockchain:", "[OK]" if len(results) > 5 and results[5] else "[NEEDS BLOCKCHAIN SERVICE]")
print("="*70)
