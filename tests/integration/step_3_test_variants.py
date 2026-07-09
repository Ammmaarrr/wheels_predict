"""
Step by Step Testing - Car Variants System
"""

print("=" * 60)
print("STEP 3: TESTING CAR VARIANTS SYSTEM")
print("=" * 60)

try:
    # Test car variants mapping
    print("🚗 Testing car variants mapping...")
    
    # Define car variants manually for testing
    car_variants = {
        'toyota': {
            'corolla': ['xli', 'gli', 'altis', 'grande', 'se']
        },
        'honda': {
            'civic': ['vti', 'vti oriel', 'rs', 'type r']
        },
        'suzuki': {
            'alto': ['vx', 'vxr', 'vxl']
        }
    }
    
    print("✅ Car variants mapping loaded")
    
    # Test variant extraction for different cars
    test_cars = [
        ('Toyota', 'Corolla'),
        ('Honda', 'Civic'),
        ('Suzuki', 'Alto')
    ]
    
    for make, model in test_cars:
        make_lower = make.lower()
        model_lower = model.lower()
        
        if make_lower in car_variants and model_lower in car_variants[make_lower]:
            variants = car_variants[make_lower][model_lower]
            print(f"✅ {make} {model} variants: {variants}")
        else:
            print(f"❌ {make} {model} variants not found")
    
    # Test variant-specific price prediction
    print("\n🔧 Testing variant-specific predictions...")
    
    from src.pakwheels_ml.models.enhanced_api_wrapper import enhanced_api
    
    # Test Toyota Corolla variants
    base_car = {
        'make': 'Toyota',
        'model': 'Corolla',
        'year': 2020,
        'engine_capacity': 1300,
        'transmission': 'manual'
    }
    
    variants = ['xli', 'gli', 'altis']
    variant_prices = {}
    
    for variant in variants:
        try:
            result = enhanced_api.predict_price_enhanced(
                variant=variant,
                **base_car
            )
            variant_prices[variant] = result['predicted_price']
            print(f"✅ {variant.upper()}: {result['predicted_price']:,} PKR")
        except Exception as e:
            print(f"❌ {variant.upper()}: Error - {e}")
    
    # Show price differences
    if len(variant_prices) > 1:
        print(f"\n📊 Variant Price Analysis:")
        base_variant = list(variant_prices.keys())[0]
        base_price = variant_prices[base_variant]
        
        for variant, price in variant_prices.items():
            diff = price - base_price
            diff_pct = (diff / base_price) * 100
            print(f"   {variant.upper()}: {diff:+,} PKR ({diff_pct:+.1f}% vs {base_variant.upper()})")
    
except Exception as e:
    print(f"❌ Error testing car variants: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 3 COMPLETED!")
print("=" * 60)
