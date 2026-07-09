"""
Comprehensive Test Suite for Enhanced API Features
"""

from src.pakwheels_ml.models.enhanced_api_wrapper import enhanced_api
import time
import json

def test_enhanced_api():
    """Test the enhanced API with comprehensive scenarios."""
    print("="*70)
    print("COMPREHENSIVE ENHANCED API TESTING")
    print("="*70)
    
    # Test 1: Enhanced Price Prediction
    test_price_predictions()
    
    # Test 2: Enhanced Recommendations
    test_enhanced_recommendations()
    
    # Test 3: Pakistani Market Specific Features
    test_pakistani_market_features()
    
    # Test 4: Variant-Specific Testing
    test_variant_specific_features()
    
    # Test 5: Performance Testing
    test_performance_metrics()
    
    # Test 6: Edge Cases
    test_edge_cases()
    
    print("\n" + "="*70)
    print("ALL ENHANCED API TESTS COMPLETED SUCCESSFULLY! 🎉")
    print("="*70)

def test_price_predictions():
    """Test enhanced price prediction with various scenarios."""
    print("\n1. ENHANCED PRICE PREDICTION TESTING")
    print("-" * 50)
    
    # Test cases covering different Pakistani market scenarios
    test_cases = [
        {
            'name': 'Toyota Corolla GLI 2020 (Popular Variant)',
            'make': 'Toyota',
            'model': 'Corolla',
            'year': 2020,
            'engine_capacity': 1300,
            'transmission': 'manual',
            'variant': 'gli'
        },
        {
            'name': 'Honda Civic VTi 2019 (Automatic Premium)',
            'make': 'Honda',
            'model': 'Civic',
            'year': 2019,
            'engine_capacity': 1800,
            'transmission': 'automatic',
            'variant': 'vti'
        },
        {
            'name': 'Suzuki Alto VXR 2021 (Compact Popular)',
            'make': 'Suzuki',
            'model': 'Alto',
            'year': 2021,
            'engine_capacity': 660,
            'transmission': 'manual',
            'variant': 'vxr'
        },
        {
            'name': 'Toyota Prius 2018 (Hybrid Premium)',
            'make': 'Toyota',
            'model': 'Prius',
            'year': 2018,
            'engine_capacity': 1800,
            'transmission': 'automatic',
            'variant': 'hybrid'
        },
        {
            'name': 'Honda City 2020 (Mid-Range)',
            'make': 'Honda',
            'model': 'City',
            'year': 2020,
            'engine_capacity': 1500,
            'transmission': 'cvt',
            'variant': 'aspire'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        start_time = time.time()
        result = enhanced_api.predict_price_enhanced(
            make=test_case['make'],
            model=test_case['model'],
            year=test_case['year'],
            engine_capacity=test_case['engine_capacity'],
            transmission=test_case['transmission'],
            variant=test_case['variant']
        )
        prediction_time = time.time() - start_time
        
        print(f"   💰 Predicted Price: {result['predicted_price']:,} PKR")
        print(f"   📊 Confidence: {result['confidence']:.2f}")
        print(f"   📈 Price Range: {result['price_range']['min']:,.0f} - {result['price_range']['max']:,.0f}")
        print(f"   ⚡ Response Time: {prediction_time:.3f}s")
        print(f"   🎯 Model: {result['model_info']['type']}")
        
        # Show enhanced features used
        features_used = result['features_used']
        print(f"   🚗 Enhanced Features: Pakistani={features_used.get('is_japanese', False)}, "
              f"Popular={features_used.get('is_popular_variant', False)}, "
              f"Auto={features_used.get('is_automatic', False)}")

def test_enhanced_recommendations():
    """Test enhanced recommendation engine."""
    print("\n2. ENHANCED RECOMMENDATION TESTING")
    print("-" * 50)
    
    # Test different budget scenarios
    budget_scenarios = [
        {
            'name': 'Budget Cars (20 Lakh)',
            'budget': 2000000,
            'preferences': {'transmission': 'manual'},
            'description': 'Affordable manual cars'
        },
        {
            'name': 'Mid-Range (35 Lakh)',
            'budget': 3500000,
            'preferences': {'transmission': 'automatic'},
            'description': 'Automatic mid-range cars'
        },
        {
            'name': 'Premium (50 Lakh)',
            'budget': 5000000,
            'preferences': {'transmission': 'automatic', 'min_year': 2019},
            'description': 'Premium recent automatic cars'
        },
        {
            'name': 'Luxury (75 Lakh)',
            'budget': 7500000,
            'preferences': {'min_year': 2020},
            'description': 'Luxury recent cars'
        }
    ]
    
    for i, scenario in enumerate(budget_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']} - {scenario['description']}")
        
        start_time = time.time()
        recommendations = enhanced_api.get_enhanced_recommendations(
            budget=scenario['budget'],
            preferences=scenario['preferences']
        )
        rec_time = time.time() - start_time
        
        print(f"   📊 Found {len(recommendations)} recommendations in {rec_time:.3f}s")
        
        # Show top 3 recommendations
        for j, rec in enumerate(recommendations[:3], 1):
            print(f"   {j}. {rec['make']} {rec['model']} {rec['year']} {rec['variant']}")
            print(f"      💰 {rec['price']:,} PKR | 🔧 {rec['engine_capacity']}cc | ⚙️ {rec['transmission']}")
            print(f"      📈 Match Score: {rec['match_score']:.2f}")

def test_pakistani_market_features():
    """Test Pakistani market specific features."""
    print("\n3. PAKISTANI MARKET SPECIFIC FEATURES")
    print("-" * 50)
    
    # Test popular Pakistani variants
    pakistani_variants = [
        ('Toyota', 'Corolla', 'GLI', 'Popular sedan variant'),
        ('Honda', 'Civic', 'VTi', 'Performance variant'),
        ('Suzuki', 'Alto', 'VXR', 'Top variant of compact car'),
        ('Toyota', 'Vitz', 'F', 'Hatchback variant'),
        ('Honda', 'City', 'Aspire', 'Premium city car')
    ]
    
    print("\n🇵🇰 Testing Popular Pakistani Variants:")
    for i, (make, model, variant, description) in enumerate(pakistani_variants, 1):
        result = enhanced_api.predict_price_enhanced(
            make=make,
            model=model,
            year=2020,
            engine_capacity=1300,
            transmission='manual',
            variant=variant.lower()
        )
        
        features = result['features_used']
        print(f"   {i}. {make} {model} {variant}: {result['predicted_price']:,} PKR")
        print(f"      📋 {description}")
        print(f"      🏭 Japanese Brand: {features.get('is_japanese', 'N/A')}")
        print(f"      ⭐ Popular Variant: {features.get('is_popular_variant', 'N/A')}")

def test_variant_specific_features():
    """Test variant-specific feature extraction."""
    print("\n4. VARIANT-SPECIFIC FEATURE TESTING")
    print("-" * 50)
    
    # Test same car with different variants - using car-specific variants
    base_car = {
        'make': 'Toyota',
        'model': 'Corolla',
        'year': 2020,
        'engine_capacity': 1300,
        'transmission': 'manual'
    }
    
    # Toyota Corolla specific variants
    variants = ['xli', 'gli', 'altis', 'grande', 'se']
    
    print("\n🔧 Testing Toyota Corolla Variant Price Differences (2020):")
    variant_prices = {}
    
    for variant in variants:
        result = enhanced_api.predict_price_enhanced(
            variant=variant,
            **base_car
        )
        
        variant_prices[variant] = result['predicted_price']
        features = result['features_used']
        
        print(f"   • {variant.upper()}: {result['predicted_price']:,} PKR")
        print(f"     Confidence: {result['confidence']:.2f} | Popular: {features.get('is_popular_variant', False)}")
    
    # Show price differences
    print(f"\n📊 Toyota Corolla Variant Price Analysis:")
    base_price = variant_prices['gli']  # GLI as base variant
    for variant, price in variant_prices.items():
        diff = price - base_price
        diff_pct = (diff / base_price) * 100
        print(f"   {variant.upper()}: {diff:+,} PKR ({diff_pct:+.1f}% vs GLI)")
    
    # Test Honda Civic variants
    print("\n🔧 Testing Honda Civic Variant Price Differences (2020):")
    honda_base_car = {
        'make': 'Honda',
        'model': 'Civic',
        'year': 2020,
        'engine_capacity': 1800,
        'transmission': 'automatic'
    }
    
    # Honda Civic specific variants
    honda_variants = ['vti', 'vti oriel', 'rs']
    honda_variant_prices = {}
    
    for variant in honda_variants:
        result = enhanced_api.predict_price_enhanced(
            variant=variant,
            **honda_base_car
        )
        
        honda_variant_prices[variant] = result['predicted_price']
        features = result['features_used']
        
        print(f"   • {variant.upper()}: {result['predicted_price']:,} PKR")
        print(f"     Confidence: {result['confidence']:.2f} | Popular: {features.get('is_popular_variant', False)}")
    
    # Show Honda price differences
    print(f"\n📊 Honda Civic Variant Price Analysis:")
    honda_base_price = honda_variant_prices['vti']  # VTi as base variant
    for variant, price in honda_variant_prices.items():
        diff = price - honda_base_price
        diff_pct = (diff / honda_base_price) * 100
        print(f"   {variant.upper()}: {diff:+,} PKR ({diff_pct:+.1f}% vs VTi)")
    
    # Test Suzuki Alto variants
    print("\n🔧 Testing Suzuki Alto Variant Price Differences (2021):")
    suzuki_base_car = {
        'make': 'Suzuki',
        'model': 'Alto',
        'year': 2021,
        'engine_capacity': 660,
        'transmission': 'manual'
    }
    
    # Suzuki Alto specific variants
    suzuki_variants = ['vx', 'vxr', 'vxl']
    suzuki_variant_prices = {}
    
    for variant in suzuki_variants:
        result = enhanced_api.predict_price_enhanced(
            variant=variant,
            **suzuki_base_car
        )
        
        suzuki_variant_prices[variant] = result['predicted_price']
        features = result['features_used']
        
        print(f"   • {variant.upper()}: {result['predicted_price']:,} PKR")
        print(f"     Confidence: {result['confidence']:.2f} | Popular: {features.get('is_popular_variant', False)}")
    
    # Show Suzuki price differences
    print(f"\n📊 Suzuki Alto Variant Price Analysis:")
    suzuki_base_price = suzuki_variant_prices['vx']  # VX as base variant
    for variant, price in suzuki_variant_prices.items():
        diff = price - suzuki_base_price
        diff_pct = (diff / suzuki_base_price) * 100
        print(f"   {variant.upper()}: {diff:+,} PKR ({diff_pct:+.1f}% vs VX)")

def test_performance_metrics():
    """Test performance and response times."""
    print("\n5. PERFORMANCE METRICS TESTING")
    print("-" * 50)
    
    # Test response times
    test_runs = 5
    total_time = 0
    
    print(f"\n⚡ Testing Response Times ({test_runs} runs):")
    
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

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n6. EDGE CASES & ERROR HANDLING")
    print("-" * 50)
    
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
            'name': 'Large Engine (2500cc)',
            'params': {'make': 'Toyota', 'model': 'Camry', 'year': 2020, 'engine_capacity': 2500, 'transmission': 'automatic', 'variant': 'hybrid'},
            'expected': 'Premium pricing for large engine'
        },
        {
            'name': 'Unknown Variant',
            'params': {'make': 'Suzuki', 'model': 'Swift', 'year': 2020, 'engine_capacity': 1200, 'transmission': 'manual', 'variant': 'unknown'},
            'expected': 'Standard pricing for unknown variant'
        }
    ]
    
    print("\n🧪 Testing Edge Cases:")
    for i, test_case in enumerate(edge_cases, 1):
        try:
            result = enhanced_api.predict_price_enhanced(**test_case['params'])
            print(f"   {i}. {test_case['name']}: {result['predicted_price']:,} PKR")
            print(f"      Expected: {test_case['expected']}")
            print(f"      Confidence: {result['confidence']:.2f}")
        except Exception as e:
            print(f"   {i}. {test_case['name']}: ERROR - {e}")

if __name__ == "__main__":
    test_enhanced_api()
