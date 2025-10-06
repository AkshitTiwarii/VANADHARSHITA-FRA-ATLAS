#!/usr/bin/env python3
"""Test satellite analysis endpoint"""

import requests
import json

# Test satellite analysis endpoint
url = "http://127.0.0.1:3001/api/satellite/analyze"

payload = {
    "latitude": 21.1458,
    "longitude": 79.0882,
    "radius_km": 5.0,
    "analysis_type": "vegetation"
}

print("🧪 Testing Satellite Analysis Endpoint")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\n" + "="*50 + "\n")

try:
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"\n📊 Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✨ Satellite analysis endpoint is working!")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to backend service")
    print("   Make sure the backend is running on http://127.0.0.1:3001")
except Exception as e:
    print(f"❌ Error: {e}")
