"""
Direct API Test
Test the enhanced features by calling the API directly
"""

import requests
import json
from datetime import datetime

def test_enhanced_api_direct():
    """Test the enhanced API directly."""
    
    print("="*60)
    print("DIRECT API TEST - ENHANCED FEATURES")
    print("="*60)
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    base_url = "http://localhost:5000"
    
    # Test 1: Health check
    print("\n1. API HEALTH CHECK")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ API health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    # Test 2: Price prediction
    print("\n2. PRICE PREDICTION TEST")
    print("-" * 30)
    
    test_data = {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "engine_capacity": 1300,
        "transmission": "manual",
        "variant": "gli"
    }
    
    try:
        response = requests.post(f"{base_url}/predict", json=test_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Price prediction successful")
            print(f"  Predicted Price: {result.get('predicted_price', 'N/A'):,.0f} PKR")
            print(f"  Confidence: {result.get('confidence', 'N/A')}")
            print(f"  Market Position: {result.get('market_position', 'N/A')}")
        else:
            print(f"❌ Price prediction failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Price prediction error: {e}")
    
    # Test 3: Recommendations
    print("\n3. RECOMMENDATIONS TEST")
    print("-" * 30)
    
    rec_data = {
        "make": "Toyota",
        "model": "Corolla",
        "year": 2020,
        "budget_min": 1500000,
        "budget_max": 2500000,
        "limit": 5
    }
    
    try:
        response = requests.post(f"{base_url}/recommendations", json=rec_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Recommendations successful")
            recommendations = result.get('recommendations', [])
            print(f"  Found {len(recommendations)} recommendations")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec.get('make', 'N/A')} {rec.get('model', 'N/A')} {rec.get('year', 'N/A')}")
                print(f"     Price: {rec.get('price', 0):,.0f} PKR")
        else:
            print(f"❌ Recommendations failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
    
    # Test 4: Market insights
    print("\n4. MARKET INSIGHTS TEST")
    print("-" * 30)
    
    market_data = {
        "make": "Toyota",
        "year_start": 2018,
        "year_end": 2022
    }
    
    try:
        response = requests.post(f"{base_url}/market_insights", json=market_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Market insights successful")
            print(f"  Total Listings: {result.get('total_listings', 'N/A')}")
            print(f"  Average Price: {result.get('avg_price', 0):,.0f} PKR")
            print(f"  Price Range: {result.get('price_range', {}).get('min', 0):,.0f} - {result.get('price_range', {}).get('max', 0):,.0f} PKR")
        else:
            print(f"❌ Market insights failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Market insights error: {e}")
    
    print("\n" + "="*60)
    print("DIRECT API TEST COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    test_enhanced_api_direct()
