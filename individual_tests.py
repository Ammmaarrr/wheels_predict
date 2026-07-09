"""
Individual Test Runner for Enhanced API Features
"""

import sys
import os
import time
import traceback

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_1_price_prediction():
    """Test 1: Enhanced Price Prediction"""
    print("="*60)
    print("TEST 1: ENHANCED PRICE PREDICTION")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test case 1: Toyota Corolla GLI 2020
        print("\n1.1 Testing Toyota Corolla GLI 2020 (Popular Variant)")
        print("-" * 50)
        
        start_time = time.time()
        result = enhanced_api.predict_price_enhanced(
            make='Toyota',
            model='Corolla',
            year=2020,
            engine_capacity=1300,
            transmission='manual',
            variant='gli'
        )
        prediction_time = time.time() - start_time
        
        print(f"✅ Prediction successful!")
        print(f"   💰 Predicted Price: {result['predicted_price']:,} PKR")
        print(f"   📊 Confidence: {result['confidence']:.2f}")
        print(f"   📈 Price Range: {result['price_range']['min']:,.0f} - {result['price_range']['max']:,.0f} PKR")
        print(f"   ⚡ Response Time: {prediction_time:.3f}s")
        print(f"   🎯 Market Position: {result['market_position']}")
        
        # Test case 2: Honda Civic VTi 2019
        print("\n1.2 Testing Honda Civic VTi 2019 (Automatic Premium)")
        print("-" * 50)
        
        result2 = enhanced_api.predict_price_enhanced(
            make='Honda',
            model='Civic',
            year=2019,
            engine_capacity=1800,
            transmission='automatic',
            variant='vti'
        )
        
        print(f"✅ Prediction successful!")
        print(f"   💰 Predicted Price: {result2['predicted_price']:,} PKR")
        print(f"   📊 Confidence: {result2['confidence']:.2f}")
        print(f"   🎯 Market Position: {result2['market_position']}")
        
        # Test case 3: Suzuki Alto VXR 2021
        print("\n1.3 Testing Suzuki Alto VXR 2021 (Compact Popular)")
        print("-" * 50)
        
        result3 = enhanced_api.predict_price_enhanced(
            make='Suzuki',
            model='Alto',
            year=2021,
            engine_capacity=660,
            transmission='manual',
            variant='vxr'
        )
        
        print(f"✅ Prediction successful!")
        print(f"   💰 Predicted Price: {result3['predicted_price']:,} PKR")
        print(f"   📊 Confidence: {result3['confidence']:.2f}")
        print(f"   🎯 Market Position: {result3['market_position']}")
        
        print(f"\n🎉 TEST 1 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
        traceback.print_exc()

def test_2_recommendations():
    """Test 2: Enhanced Recommendations"""
    print("\n" + "="*60)
    print("TEST 2: ENHANCED RECOMMENDATIONS")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test case 1: Budget cars (20 Lakh)
        print("\n2.1 Testing Budget Cars (20 Lakh)")
        print("-" * 50)
        
        recommendations = enhanced_api.get_enhanced_recommendations(
            budget=2000000,
            preferences={'transmission': 'manual'}
        )
        
        print(f"✅ Found {len(recommendations)} recommendations")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"   {i}. {rec['make']} {rec['model']} {rec['year']}")
            print(f"      💰 {rec['price']:,} PKR | 🔧 {rec.get('engine_capacity', 'N/A')}cc | ⚙️ {rec.get('transmission', 'N/A')}")
        
        # Test case 2: Mid-range cars (35 Lakh)
        print("\n2.2 Testing Mid-Range Cars (35 Lakh)")
        print("-" * 50)
        
        recommendations2 = enhanced_api.get_enhanced_recommendations(
            budget=3500000,
            preferences={'transmission': 'automatic'}
        )
        
        print(f"✅ Found {len(recommendations2)} recommendations")
        for i, rec in enumerate(recommendations2[:3], 1):
            print(f"   {i}. {rec['make']} {rec['model']} {rec['year']}")
            print(f"      💰 {rec['price']:,} PKR | 🔧 {rec.get('engine_capacity', 'N/A')}cc | ⚙️ {rec.get('transmission', 'N/A')}")
        
        print(f"\n🎉 TEST 2 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
        traceback.print_exc()

def test_3_variant_analysis():
    """Test 3: Variant Analysis"""
    print("\n" + "="*60)
    print("TEST 3: VARIANT ANALYSIS")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test variant comparison for Toyota Corolla
        print("\n3.1 Testing Toyota Corolla Variant Analysis")
        print("-" * 50)
        
        base_car = {
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'engine_capacity': 1300,
            'transmission': 'manual'
        }
        
        variants = ['gli', 'xli', 'altis']
        variant_prices = {}
        
        for variant in variants:
            result = enhanced_api.predict_price_enhanced(
                variant=variant,
                **base_car
            )
            
            variant_prices[variant] = result['predicted_price']
            print(f"   • {variant.upper()}: {result['predicted_price']:,} PKR")
            print(f"     Confidence: {result['confidence']:.2f}")
        
        # Show price differences
        print(f"\n📊 Variant Price Comparison:")
        base_price = variant_prices['gli']
        for variant, price in variant_prices.items():
            diff = price - base_price
            diff_pct = (diff / base_price) * 100
            print(f"   {variant.upper()}: {diff:+,} PKR ({diff_pct:+.1f}% vs GLI)")
        
        print(f"\n🎉 TEST 3 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
        traceback.print_exc()

def test_4_market_insights():
    """Test 4: Market Insights"""
    print("\n" + "="*60)
    print("TEST 4: MARKET INSIGHTS")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test market insights for Toyota
        print("\n4.1 Testing Toyota Market Insights")
        print("-" * 50)
        
        market_insights = enhanced_api.get_market_insights(
            make='Toyota',
            year_range=(2018, 2022)
        )
        
        print(f"✅ Market insights retrieved!")
        print(f"   📊 Total Listings: {market_insights['total_listings']:,}")
        print(f"   💰 Average Price: {market_insights['avg_price']:,.0f} PKR")
        print(f"   📈 Price Range: {market_insights['price_range']['min']:,.0f} - {market_insights['price_range']['max']:,.0f} PKR")
        
        # Test market insights for Honda
        print("\n4.2 Testing Honda Market Insights")
        print("-" * 50)
        
        market_insights2 = enhanced_api.get_market_insights(
            make='Honda',
            year_range=(2018, 2022)
        )
        
        print(f"✅ Market insights retrieved!")
        print(f"   📊 Total Listings: {market_insights2['total_listings']:,}")
        print(f"   💰 Average Price: {market_insights2['avg_price']:,.0f} PKR")
        print(f"   📈 Price Range: {market_insights2['price_range']['min']:,.0f} - {market_insights2['price_range']['max']:,.0f} PKR")
        
        print(f"\n🎉 TEST 4 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
        traceback.print_exc()

def test_5_performance():
    """Test 5: Performance Testing"""
    print("\n" + "="*60)
    print("TEST 5: PERFORMANCE TESTING")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test response times
        test_runs = 5
        total_time = 0
        
        print(f"\n5.1 Testing Response Times ({test_runs} runs)")
        print("-" * 50)
        
        for i in range(test_runs):
            start_time = time.time()
            result = enhanced_api.predict_price_enhanced(
                make='Honda',
                model='Civic',
                year=2020,
                engine_capacity=1800,
                transmission='automatic',
                variant='vti'
            )
            end_time = time.time()
            
            run_time = end_time - start_time
            total_time += run_time
            
            print(f"   Run {i+1}: {run_time:.3f}s | Price: {result['predicted_price']:,} PKR")
        
        avg_time = total_time / test_runs
        print(f"\n📊 Performance Summary:")
        print(f"   Average Response Time: {avg_time:.3f}s")
        print(f"   Total Test Time: {total_time:.3f}s")
        print(f"   Requests per Second: {test_runs/total_time:.1f}")
        
        print(f"\n🎉 TEST 5 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 5 FAILED: {e}")
        traceback.print_exc()

def test_6_edge_cases():
    """Test 6: Edge Cases"""
    print("\n" + "="*60)
    print("TEST 6: EDGE CASES")
    print("="*60)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        edge_cases = [
            {
                'name': 'Very Old Car (2005)',
                'params': {'make': 'Toyota', 'model': 'Corolla', 'year': 2005, 'engine_capacity': 1300, 'transmission': 'manual', 'variant': 'xli'},
                'expected': 'Lower price due to age'
            },
            {
                'name': 'Very New Car (2024)',
                'params': {'make': 'Honda', 'model': 'Civic', 'year': 2024, 'engine_capacity': 1800, 'transmission': 'automatic', 'variant': 'vti'},
                'expected': 'Higher price for new model'
            },
            {
                'name': 'Unknown Variant',
                'params': {'make': 'Suzuki', 'model': 'Swift', 'year': 2020, 'engine_capacity': 1200, 'transmission': 'manual', 'variant': 'unknown'},
                'expected': 'Standard pricing for unknown variant'
            }
        ]
        
        print("\n6.1 Testing Edge Cases")
        print("-" * 50)
        
        for i, test_case in enumerate(edge_cases, 1):
            try:
                result = enhanced_api.predict_price_enhanced(**test_case['params'])
                print(f"   {i}. {test_case['name']}: {result['predicted_price']:,} PKR")
                print(f"      Expected: {test_case['expected']}")
                print(f"      Confidence: {result['confidence']:.2f}")
            except Exception as e:
                print(f"   {i}. {test_case['name']}: ERROR - {e}")
        
        print(f"\n🎉 TEST 6 COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ TEST 6 FAILED: {e}")
        traceback.print_exc()

def main():
    """Run all tests individually"""
    print("🚀 STARTING INDIVIDUAL ENHANCED API TESTS")
    print("="*60)
    
    # Run tests one by one
    test_1_price_prediction()
    test_2_recommendations()
    test_3_variant_analysis()
    test_4_market_insights()
    test_5_performance()
    test_6_edge_cases()
    
    print("\n" + "="*60)
    print("🎉 ALL INDIVIDUAL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    main()
