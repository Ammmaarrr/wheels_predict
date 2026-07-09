"""
Step by Step Testing - Enhanced API Wrapper
"""

print("=" * 60)
print("STEP 2: TESTING ENHANCED API WRAPPER")
print("=" * 60)

try:
    from enhanced_api_wrapper import enhanced_api
    print("✅ API Wrapper imported successfully")
    
    # Check if data is loaded
    if enhanced_api.enhanced_data is not None:
        print(f"✅ Enhanced data loaded: {enhanced_api.enhanced_data.shape}")
        print(f"✅ Available columns: {len(enhanced_api.enhanced_data.columns)}")
    else:
        print("❌ No enhanced data loaded")
    
    # Test a simple price prediction
    print("\n🔧 Testing price prediction...")
    result = enhanced_api.predict_price_enhanced(
        make='Toyota',
        model='Corolla',
        year=2020,
        engine_capacity=1300,
        transmission='manual',
        variant='gli'
    )
    
    print(f"✅ Price prediction successful!")
    print(f"   Predicted Price: {result['predicted_price']:,} PKR")
    print(f"   Confidence: {result['confidence']:.2f}")
    
except Exception as e:
    print(f"❌ Error testing API wrapper: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 2 COMPLETED!")
print("=" * 60)
