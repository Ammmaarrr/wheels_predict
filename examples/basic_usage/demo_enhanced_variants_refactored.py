"""
Enhanced Car Variants Demo - Refactored
Shows proper car-specific variant testing with improved structure
"""

from typing import Dict, List, Tuple

def get_car_variants_mapping() -> Dict[str, Dict[str, List[str]]]:
    """Get the car variants mapping data."""
    return {
        'toyota': {
            'corolla': ['xli', 'gli', 'altis', 'grande', 'se'],
            'vitz': ['f', 'u', 'jewela'],
            'prius': ['standard', 'alpha', 'g'],
            'camry': ['up-spec', 'hybrid', 'grande'],
        },
        'honda': {
            'civic': ['vti', 'vti oriel', 'rs', 'type r'],
            'city': ['aspire', 'aspire prosmatec', 'ivtec', 'cvt'],
            'accord': ['cp2', 'cp3', 'executive'],
            'crv': ['i-vtec', 'exec'],
        },
        'suzuki': {
            'alto': ['vx', 'vxr', 'vxl'],
            'wagon r': ['vx', 'vxr', 'vxl'],
            'swift': ['dxg', 'dlx', 'automatic'],
            'cultus': ['vx', 'vxr', 'vxl', 'ags']
        },
        'hyundai': {
            'elantra': ['gls', 'value edition'],
            'tucson': ['gls', 'ultimate'],
            'santafe': ['gls', 'limited']
        }
    }

def display_variants_for_make(make: str, models_variants: Dict[str, List[str]]) -> None:
    """Display variants for a specific car make."""
    print(f"\n🏭 {make.upper()} VARIANTS:")
    print("-" * 40)
    
    for model, variants in models_variants.items():
        print(f"\n  📱 {model.title()}:")
        for variant in variants:
            print(f"    • {variant.upper()}")
        print(f"    Total variants: {len(variants)}")

def get_test_scenarios() -> List[Tuple[str, str, str, str]]:
    """Get test scenarios for variant testing."""
    return [
        ("Toyota", "Corolla", "GLI", "✅ Valid - Popular Pakistan variant"),
        ("Honda", "Civic", "VTi Oriel", "✅ Valid - Premium variant"),
        ("Suzuki", "Alto", "VXR", "✅ Valid - High-end variant"),
        ("Toyota", "Corolla", "Invalid", "❌ Invalid - Not a real variant"),
        ("Honda", "City", "ASPIRE", "✅ Valid - Entry level variant"),
    ]

def test_variant_validation(car_variants: Dict) -> None:
    """Test variant validation logic."""
    print(f"\n🧪 VARIANT VALIDATION TESTING:")
    print("-" * 50)
    
    test_scenarios = get_test_scenarios()
    
    for make, model, variant, expected in test_scenarios:
        # Simple validation logic
        make_lower = make.lower()
        model_lower = model.lower()
        variant_lower = variant.lower()
        
        is_valid = False
        if make_lower in car_variants:
            if model_lower in car_variants[make_lower]:
                is_valid = variant_lower in car_variants[make_lower][model_lower]
        
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"\nTest: {make} {model} {variant}")
        print(f"Result: {status}")
        print(f"Expected: {expected}")

def show_market_insights(car_variants: Dict) -> None:
    """Show market insights from variants data."""
    print(f"\n📊 MARKET INSIGHTS:")
    print("-" * 50)
    
    total_makes = len(car_variants)
    total_models = sum(len(models) for models in car_variants.values())
    total_variants = sum(
        len(variants) 
        for models in car_variants.values() 
        for variants in models.values()
    )
    
    print(f"✅ Total Car Makes: {total_makes}")
    print(f"✅ Total Models: {total_models}")
    print(f"✅ Total Variants: {total_variants}")
    print(f"✅ Average Variants per Model: {total_variants/total_models:.1f}")

def demonstrate_business_value() -> None:
    """Demonstrate business value of variant mapping."""
    print(f"\n💰 BUSINESS VALUE:")
    print("-" * 50)
    
    benefits = [
        "🎯 Accurate price differentiation by variant",
        "🔍 Better search filtering and categorization", 
        "📊 Market analysis by specific variants",
        "🚗 Improved recommendation accuracy",
        "📈 Enhanced user experience with valid options",
        "🔧 Reduced data entry errors"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

def demo_enhanced_variants():
    """Main demonstration function - refactored for clarity."""
    print("=" * 70)
    print("ENHANCED CAR VARIANTS DEMONSTRATION")
    print("=" * 70)
    
    # Get variants data
    car_variants = get_car_variants_mapping()
    
    # Display variants by make
    for make, models_variants in car_variants.items():
        display_variants_for_make(make, models_variants)
    
    # Test validation
    test_variant_validation(car_variants)
    
    # Show insights
    show_market_insights(car_variants)
    
    # Show business value
    demonstrate_business_value()
    
    print(f"\n{'=' * 70}")
    print("🎉 Enhanced variants system provides structured,")
    print("validated car variant data for the Pakistani market!")
    print("=" * 70)

if __name__ == "__main__":
    demo_enhanced_variants()
