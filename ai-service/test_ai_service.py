#!/usr/bin/env python3
"""
Test script for FRA Atlas AI Service
"""

import requests
import os
from pathlib import Path

def test_ai_service():
    """Test the AI service endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing FRA Atlas AI Service")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Health check: FAILED")
            return False
    except Exception as e:
        print(f"❌ Health check: FAILED - {e}")
        return False
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint: PASSED")
            stats = response.json()
            print(f"   OCR Engine: {stats.get('ocr_engine', 'Unknown')}")
            print(f"   Supported formats: {', '.join(stats.get('supported_formats', []))}")
        else:
            print("❌ Stats endpoint: FAILED")
    except Exception as e:
        print(f"❌ Stats endpoint: FAILED - {e}")
    
    # Test satellite analysis
    try:
        test_coords = {"latitude": 21.2514, "longitude": 81.6296}
        response = requests.post(f"{base_url}/api/analyze-satellite", json=test_coords)
        if response.status_code == 200:
            print("✅ Satellite analysis: PASSED")
            analysis = response.json()
            print(f"   Forest cover: {analysis.get('forest_cover', 'Unknown')}%")
        else:
            print("❌ Satellite analysis: FAILED")
    except Exception as e:
        print(f"❌ Satellite analysis: FAILED - {e}")
    
    print("\n🎯 AI Service Test Complete")
    print("\n📝 To test document processing:")
    print("   1. Start the AI service: python main.py")
    print("   2. Open the frontend and upload a document image")
    print("   3. Click 'Process with AI' button")
    
    return True

if __name__ == "__main__":
    test_ai_service()