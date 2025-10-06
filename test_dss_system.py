"""
Test script for Enhanced Decision Support System (DSS)

Tests all DSS endpoints:
1. Village analysis
2. Scheme listing
3. Budget optimization
4. Impact prediction
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_dss_schemes():
    """Test 1: Get all available schemes"""
    print("\n" + "="*80)
    print("TEST 1: Get Available Government Schemes")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/dss/schemes")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Found {data['total_schemes']} schemes")
            print(f"Ministries: {', '.join(data['ministries'])}")
            print(f"\nTop 3 Schemes:")
            for scheme in data['schemes'][:3]:
                print(f"  - {scheme['name']} ({scheme['code']})")
                print(f"    Ministry: {scheme['ministry']}")
                print(f"    Budget: ₹{scheme['budget_per_beneficiary']:,} per beneficiary")
            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def test_village_analysis():
    """Test 2: Analyze a village for recommendations"""
    print("\n" + "="*80)
    print("TEST 2: Village DSS Analysis")
    print("="*80)
    
    # Sample village data
    village_data = {
        "village_id": "VIL_TEST_001",
        "village_name": "Sitapur",
        "area_hectares": 500,
        "forest_cover_percent": 40,
        "agricultural_land_percent": 45,
        "water_bodies_count": 2,
        "population": 2500,
        "households": 500,
        "tribal_population_percent": 65,
        "average_income": 45000,
        "unemployment_rate": 18,
        "poverty_rate": 28,
        "roads_km": 3,
        "schools_count": 2,
        "health_centers_count": 1,
        "forest_rights_claims": 50,
        "approved_claims": 35,
        "pending_claims": 10,
        "disputed_claims": 5,
        "ndvi_score": 0.65,
        "water_stress_index": 0.6,
        "deforestation_risk": 0.4,
        "available_budget": 5000000,  # 50 lakhs
        "max_schemes": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dss/analyze-village",
            json=village_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Analysis completed for {data['village_id']}")
            print(f"\nPriority Category: {data['priority_category'].upper()}")
            print(f"Overall Score: {data['overall_score']:.2f}")
            print(f"Success Probability: {data['success_probability']:.1%}")
            print(f"Total Budget Required: ₹{data['total_budget_required']:,.0f}")
            
            print(f"\n{len(data['recommendations'])} Schemes Recommended:")
            for i, rec in enumerate(data['recommendations'], 1):
                print(f"\n{i}. {rec['scheme_name']}")
                print(f"   Priority: {rec['priority_score']:.2f} | Confidence: {rec['confidence']:.2f}")
                print(f"   Budget: ₹{rec['estimated_budget']:,.0f} | Beneficiaries: {rec['estimated_beneficiaries']}")
                print(f"   Expected Impact: {rec['expected_impact_score']:.2f}")
                if rec['reasoning'].get('key_factors'):
                    print(f"   Key Factors: {', '.join(rec['reasoning']['key_factors'][:2])}")
            
            print(f"\nOptimization Strategy: {data['optimization_strategy']}")
            
            if data['risk_factors']:
                print(f"\nRisk Factors ({len(data['risk_factors'])}):")
                for risk in data['risk_factors'][:3]:
                    print(f"  - {risk}")
            
            print(f"\nMulti-Criteria Analysis:")
            mcda = data['multi_criteria_analysis']
            for criterion, score in list(mcda.items())[:4]:
                print(f"  {criterion.replace('_', ' ').title()}: {score:.2f}")
            
            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def test_budget_optimization():
    """Test 3: Multi-village budget optimization"""
    print("\n" + "="*80)
    print("TEST 3: Multi-Village Budget Optimization")
    print("="*80)
    
    # Three villages with different priorities
    villages = [
        {
            "village_id": "VIL001",
            "village_name": "High Priority Village",
            "population": 3000,
            "households": 600,
            "tribal_population_percent": 75,
            "poverty_rate": 35,
            "unemployment_rate": 20,
            "water_stress_index": 0.8,
            "forest_cover_percent": 30,
            "agricultural_land_percent": 40,
            "forest_rights_claims": 60,
            "deforestation_risk": 0.5
        },
        {
            "village_id": "VIL002",
            "village_name": "Medium Priority Village",
            "population": 2000,
            "households": 400,
            "tribal_population_percent": 50,
            "poverty_rate": 20,
            "unemployment_rate": 12,
            "water_stress_index": 0.5,
            "forest_cover_percent": 40,
            "agricultural_land_percent": 45,
            "forest_rights_claims": 30,
            "deforestation_risk": 0.3
        },
        {
            "village_id": "VIL003",
            "village_name": "Low Priority Village",
            "population": 1500,
            "households": 300,
            "tribal_population_percent": 30,
            "poverty_rate": 15,
            "unemployment_rate": 8,
            "water_stress_index": 0.3,
            "forest_cover_percent": 50,
            "agricultural_land_percent": 35,
            "forest_rights_claims": 15,
            "deforestation_risk": 0.2
        }
    ]
    
    request_data = {
        "villages": villages,
        "total_budget": 10000000,  # 1 crore
        "constraints": {"allow_partial": False}
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dss/optimize-budget",
            json=request_data
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Budget optimization completed")
            print(f"\nBudget Summary:")
            print(f"  Total Budget: ₹{data['total_budget']:,.0f}")
            print(f"  Allocated: ₹{data['allocated_budget']:,.0f}")
            print(f"  Remaining: ₹{data['remaining_budget']:,.0f}")
            
            print(f"\nVillage Coverage:")
            print(f"  Fully Funded: {data['fully_funded']}")
            print(f"  Partially Funded: {data['partially_funded']}")
            print(f"  Unfunded: {data['unfunded']}")
            
            print(f"\nAllocation Details:")
            for alloc in data['allocations']:
                print(f"  {alloc['village_name']}:")
                print(f"    Priority: {alloc['priority_category']}, Score: {alloc['overall_score']:.2f}")
                print(f"    Allocation: ₹{alloc['allocation']:,.0f} ({alloc['status']})")
            
            print(f"\nOptimization Summary:")
            summary = data['optimization_summary']
            print(f"  Strategy: {summary['strategy']}")
            print(f"  Coverage: {summary['coverage']}")
            print(f"  High Priority Villages: {summary['high_priority_villages']}")
            
            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def test_impact_prediction():
    """Test 4: Predict impact of a specific scheme"""
    print("\n" + "="*80)
    print("TEST 4: Scheme Impact Prediction")
    print("="*80)
    
    village_data = {
        "village_id": "VIL_IMPACT_TEST",
        "village_name": "Impact Test Village",
        "population": 2500,
        "households": 500,
        "agricultural_land_percent": 60,
        "tribal_population_percent": 55,
        "unemployment_rate": 15,
        "poverty_rate": 25,
        "water_stress_index": 0.7,
        "forest_cover_percent": 35,
        "deforestation_risk": 0.4
    }
    
    schemes_to_test = ["PM_KISAN", "JAL_JEEVAN_MISSION", "DAJGUA"]
    
    try:
        print(f"Testing impact prediction for {len(schemes_to_test)} schemes...")
        
        all_passed = True
        for scheme_code in schemes_to_test:
            request_data = {
                "village_data": village_data,
                "scheme_code": scheme_code
            }
            
            response = requests.post(
                f"{BASE_URL}/api/dss/predict-impact",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n  {data['scheme_name']}:")
                print(f"    Impact Score: {data['predicted_impact_score']:.2f}")
                print(f"    Impact Level: {data['impact_level'].upper()}")
                print(f"    Confidence: {data['confidence']}")
            else:
                print(f"\n  [FAIL] {scheme_code}: Status {response.status_code}")
                all_passed = False
        
        if all_passed:
            print(f"\n[PASS] All impact predictions completed")
            return True
        else:
            print(f"\n[FAIL] Some impact predictions failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def test_scheme_details():
    """Test 5: Get details of a specific scheme"""
    print("\n" + "="*80)
    print("TEST 5: Get Scheme Details")
    print("="*80)
    
    try:
        scheme_code = "DAJGUA"
        response = requests.get(f"{BASE_URL}/api/dss/scheme/{scheme_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] Retrieved details for {scheme_code}")
            print(f"\nScheme: {data['name']}")
            print(f"Ministry: {data['ministry']}")
            print(f"Budget per Beneficiary: ₹{data['budget_per_beneficiary']:,}")
            print(f"Impact Areas: {', '.join(data['impact_areas'])}")
            print(f"Implementation Time: {data['implementation_time_days']} days")
            print(f"\nEligibility Criteria:")
            for criterion, value in data['criteria'].items():
                print(f"  - {criterion}: {value}")
            return True
        else:
            print(f"[FAIL] Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Exception: {e}")
        return False


def main():
    """Run all DSS tests"""
    print("\n" + "="*80)
    print("ENHANCED DSS ENGINE - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Testing AI Service at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Get Schemes", test_dss_schemes),
        ("Village Analysis", test_village_analysis),
        ("Budget Optimization", test_budget_optimization),
        ("Impact Prediction", test_impact_prediction),
        ("Scheme Details", test_scheme_details)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n✅ ALL DSS TESTS PASSED!")
    elif passed > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: {total - passed} test(s) failed")
    else:
        print("\n❌ ALL TESTS FAILED - Check if AI service is running")
    
    return passed == total


if __name__ == "__main__":
    main()
