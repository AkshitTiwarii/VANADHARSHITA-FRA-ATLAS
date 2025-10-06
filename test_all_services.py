"""
Comprehensive Service Test Suite for FRA Atlas
Tests: AI Service, Blockchain Integration, GIS Features, Satellite Analysis
"""

import requests
import json
import time
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

def print_test(name, status, details=""):
    if status == "PASS":
        symbol = "✅"
        color = Colors.GREEN
    elif status == "WARN":
        symbol = "⚠️"
        color = Colors.YELLOW
    elif status == "FAIL":
        symbol = "❌"
        color = Colors.RED
    else:
        symbol = "ℹ️"
        color = Colors.BLUE
    
    print(f"{color}{symbol} {name}{Colors.RESET}")
    if details:
        print(f"   {Colors.BLUE}{details}{Colors.RESET}")

def test_ai_service_health():
    """Test AI service basic health"""
    print_header("AI SERVICE HEALTH CHECK")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("AI Service Running", "PASS", f"Status: {data.get('status')}")
            
            components = data.get('components', {})
            for component, status in components.items():
                status_text = "PASS" if status == "healthy" else "WARN"
                print_test(f"  Component: {component}", status_text, f"Status: {status}")
            
            return True
        else:
            print_test("AI Service Health Check", "FAIL", f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test("AI Service Connection", "FAIL", "Service not running on port 8000")
        print(f"{Colors.YELLOW}   Start with: cd ai-service && python main_v2.py{Colors.RESET}")
        return False
    except Exception as e:
        print_test("AI Service Health Check", "FAIL", str(e))
        return False

def test_blockchain_connection():
    """Test blockchain service connection"""
    print_header("BLOCKCHAIN SERVICE CONNECTION")
    
    # Test direct blockchain service
    try:
        response = requests.get('http://localhost:8001/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("Blockchain Service Direct", "PASS", f"Port 8001 - Blocks: {data.get('blocks', 0)}")
        else:
            print_test("Blockchain Service Direct", "FAIL", f"Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print_test("Blockchain Service Direct", "WARN", "Not running on port 8001")
        print(f"{Colors.YELLOW}   Start with: cd blockchain-main && npm start{Colors.RESET}")
    except Exception as e:
        print_test("Blockchain Service Direct", "FAIL", str(e))
    
    # Test AI service blockchain proxy
    try:
        response = requests.get('http://localhost:8000/api/blockchain/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            if status == 'connected':
                print_test("AI Service → Blockchain Proxy", "PASS", "Connected successfully")
                return True
            else:
                print_test("AI Service → Blockchain Proxy", "WARN", f"Status: {status}")
                print(f"{Colors.YELLOW}   {data.get('message')}{Colors.RESET}")
                return False
        else:
            print_test("AI Service → Blockchain Proxy", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("AI Service → Blockchain Proxy", "FAIL", str(e))
        return False

def test_gis_features():
    """Test GIS/Shapefile features"""
    print_header("GIS FEATURES TEST")
    
    # Check dependencies
    try:
        response = requests.get('http://localhost:8000/api/gis/check-dependencies', timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ready':
                print_test("GIS Dependencies", "PASS", "geopandas, shapely, fiona installed")
            else:
                print_test("GIS Dependencies", "WARN", data.get('message'))
        else:
            print_test("GIS Dependencies Check", "FAIL")
    except Exception as e:
        print_test("GIS Dependencies Check", "FAIL", str(e))
    
    # Get external layers catalog
    try:
        response = requests.get('http://localhost:8000/api/gis/external-layers', timeout=5)
        if response.status_code == 200:
            data = response.json()
            catalog = data.get('catalog', {})
            recommended = data.get('recommended', [])
            
            total_layers = sum(len(layers) for layers in catalog.values())
            print_test("External Layer Catalog", "PASS", 
                      f"{total_layers} layers across {len(catalog)} categories")
            print_test("  Recommended Layers", "INFO", f"{len(recommended)} layers for FRA")
            
            for category, layers in catalog.items():
                print(f"   {Colors.BLUE}• {category}: {len(layers)} layers{Colors.RESET}")
            
            return True
        else:
            print_test("External Layer Catalog", "FAIL", f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("External Layer Catalog", "FAIL", str(e))
        return False

def test_satellite_analysis():
    """Test satellite analysis"""
    print_header("SATELLITE ANALYSIS TEST")
    
    # Test coordinates (Delhi area)
    test_location = {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "radius": 500
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/analyze-satellite',
            json=test_location,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print_test("Satellite Analysis", "PASS", "Analysis completed successfully")
                
                # Check NDVI data
                ndvi = data.get('ndvi', {})
                if ndvi:
                    print_test("  NDVI Analysis", "PASS", 
                              f"Value: {ndvi.get('value', 'N/A')}, Health: {ndvi.get('health', 'N/A')}")
                
                # Check land cover
                land_cover = data.get('land_cover', {})
                if land_cover:
                    forest_pct = land_cover.get('forest_cover_percentage', 0)
                    print_test("  Land Cover Analysis", "PASS", 
                              f"Forest: {forest_pct}%, Primary: {land_cover.get('primary_type', 'N/A')}")
                
                # Check change detection
                change_detection = data.get('change_detection', {})
                if change_detection:
                    print_test("  Change Detection", "PASS", 
                              f"Status: {change_detection.get('status', 'N/A')}")
                
                return True
            else:
                print_test("Satellite Analysis", "WARN", data.get('message', 'Analysis incomplete'))
                return False
        else:
            print_test("Satellite Analysis", "FAIL", f"Status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print_test("Satellite Analysis", "WARN", "Request timed out (takes 20-30 seconds)")
        return False
    except Exception as e:
        print_test("Satellite Analysis", "FAIL", str(e))
        return False

def test_blockchain_submission():
    """Test blockchain verification submission"""
    print_header("BLOCKCHAIN VERIFICATION TEST")
    
    test_verification = {
        "documentId": f"TEST-{int(time.time())}",
        "documentHash": "a1b2c3d4e5f6789012345678901234567890abcdefabcdef1234567890abcd",
        "documentType": "test_claim",
        "metadata": {
            "village": "Test Village",
            "applicant": "Test User",
            "area_hectares": 10.5,
            "test": True,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/blockchain/submit-verification',
            json=test_verification,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            tx_id = data.get('transactionId')
            print_test("Blockchain Submission", "PASS", f"Transaction ID: {tx_id}")
            
            # Try to verify the transaction
            if tx_id:
                time.sleep(1)  # Brief pause
                verify_response = requests.get(
                    f'http://localhost:8000/api/blockchain/verify/{tx_id}',
                    timeout=5
                )
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    if verify_data.get('verified'):
                        print_test("  Blockchain Verification", "PASS", "Transaction verified successfully")
                        return True
                    else:
                        print_test("  Blockchain Verification", "WARN", "Not yet verified")
                else:
                    print_test("  Blockchain Verification", "WARN", f"Status: {verify_response.status_code}")
            
            return True
            
        elif response.status_code == 503:
            print_test("Blockchain Submission", "WARN", "Blockchain service unavailable")
            print(f"{Colors.YELLOW}   Start blockchain: cd blockchain-main && npm start{Colors.RESET}")
            return False
        else:
            print_test("Blockchain Submission", "FAIL", f"Status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_test("Blockchain Submission", "FAIL", "Cannot connect to blockchain service")
        return False
    except Exception as e:
        print_test("Blockchain Submission", "FAIL", str(e))
        return False

def test_stats_endpoint():
    """Test stats endpoint"""
    print_header("SERVICE STATISTICS")
    
    try:
        response = requests.get('http://localhost:8000/api/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print_test("Statistics Endpoint", "PASS")
            print(f"   {Colors.BLUE}Total Jobs: {data.get('total_jobs', 0)}{Colors.RESET}")
            print(f"   {Colors.BLUE}Documents Processed: {data.get('total_documents_processed', 0)}{Colors.RESET}")
            print(f"   {Colors.BLUE}Version: {data.get('version', 'N/A')}{Colors.RESET}")
            
            ml_models = data.get('ml_models', {})
            for model, status in ml_models.items():
                print(f"   {Colors.BLUE}• {model}: {status}{Colors.RESET}")
            
            return True
        else:
            print_test("Statistics Endpoint", "FAIL")
            return False
    except Exception as e:
        print_test("Statistics Endpoint", "FAIL", str(e))
        return False

def generate_summary(results):
    """Generate test summary"""
    print_header("TEST SUMMARY")
    
    passed = sum(1 for r in results if r)
    total = len(results)
    failed = total - passed
    
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"{Colors.BOLD}Total Tests: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print(f"{Colors.BLUE}Success Rate: {percentage:.1f}%{Colors.RESET}")
    
    if percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! FRA ATLAS IS READY! 🎉{Colors.RESET}")
    elif percentage >= 80:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ MOST TESTS PASSED - SOME SERVICES MAY NEED ATTENTION{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ MULTIPLE SERVICES NEED ATTENTION{Colors.RESET}")

def main():
    """Run all tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("FRA ATLAS COMPREHENSIVE SERVICE TEST SUITE".center(70))
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(70))
    print("=" * 70)
    print(f"{Colors.RESET}\n")
    
    results = []
    
    # Test each service
    results.append(test_ai_service_health())
    results.append(test_blockchain_connection())
    results.append(test_gis_features())
    results.append(test_satellite_analysis())
    results.append(test_blockchain_submission())
    results.append(test_stats_endpoint())
    
    # Generate summary
    generate_summary(results)
    
    print(f"\n{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.CYAN}Test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
