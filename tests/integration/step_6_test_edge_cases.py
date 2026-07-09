"""
Step by Step Testing - Edge Cases
"""

print("=" * 60)
print("STEP 6: TESTING EDGE CASES")
print("=" * 60)

try:
    from src.pakwheels_ml.models.enhanced_api_wrapper import enhanced_api
    
    # Test edge cases
    print("🧪 Testing edge cases...")
    
    edge_cases = [
        {
            'name': 'Very Old Car (2005)',
            'params': {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2005,
                'engine_capacity': 1300,
                'transmission': 'manual',
                'variant': 'xli'
            },
            'expected': 'Lower price due to age'
        },
        {
            'name': 'Very New Car (2024)',
            'params': {
                'make': 'Honda',
                'model': 'Civic',
                'year': 2024,
                'engine_capacity': 1800,
                'transmission': 'automatic',
                'variant': 'vti'
            },
            'expected': 'Higher price for new model'
        },
        {
            'name': 'Large Engine (2500cc)',
            'params': {
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2020,
                'engine_capacity': 2500,
                'transmission': 'automatic',
                'variant': 'hybrid'
            },
            'expected': 'Premium pricing for large engine'
        },
        {
            'name': 'Unknown Variant',
            'params': {
                'make': 'Suzuki',
                'model': 'Swift',
                'year': 2020,
                'engine_capacity': 1200,
                'transmission': 'manual',
                'variant': 'unknown'
            },
            'expected': 'Standard pricing for unknown variant'
        },
        {
            'name': 'Invalid Year (Future)',
            'params': {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2030,
                'engine_capacity': 1300,
                'transmission': 'manual',
                'variant': 'gli'
            },
            'expected': 'Should handle future year gracefully'
        }
    ]
    
    successful_tests = 0
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        try:
            result = enhanced_api.predict_price_enhanced(**test_case['params'])
            
            print(f"✅ Price: {result['predicted_price']:,} PKR")
            print(f"   Expected: {test_case['expected']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Market Position: {result.get('market_position', 'N/A')}")
            
            successful_tests += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Edge Case Testing Summary:")
    print(f"   Successful: {successful_tests}/{len(edge_cases)} tests")
    print(f"   Success Rate: {(successful_tests/len(edge_cases))*100:.1f}%")
    
    # Test invalid inputs
    print(f"\n🔧 Testing invalid inputs...")
    
    invalid_tests = [
        {
            'name': 'Empty Make',
            'params': {
                'make': '',
                'model': 'Corolla',
                'year': 2020,
                'engine_capacity': 1300,
                'transmission': 'manual',
                'variant': 'gli'
            }
        },
        {
            'name': 'Negative Engine Capacity',
            'params': {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2020,
                'engine_capacity': -1300,
                'transmission': 'manual',
                'variant': 'gli'
            }
        },
        {
            'name': 'Invalid Transmission',
            'params': {
                'make': 'Toyota',
                'model': 'Corolla',
                'year': 2020,
                'engine_capacity': 1300,
                'transmission': 'invalid',
                'variant': 'gli'
            }
        }
    ]
    
    for i, test_case in enumerate(invalid_tests, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        try:
            result = enhanced_api.predict_price_enhanced(**test_case['params'])
            print(f"✅ Handled gracefully: {result['predicted_price']:,} PKR")
            
        except Exception as e:
            print(f"❌ Error (Expected): {e}")

except Exception as e:
    print(f"❌ Error testing edge cases: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 6 COMPLETED!")
print("=" * 60)
