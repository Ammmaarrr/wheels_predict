"""
Test Car Variants Mapping
"""

import sys
import os

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

from pakistani_car_variants import get_car_variants, get_car_info, is_valid_variant

def test_car_variants():
    """Test the car variants mapping."""
    print("=" * 60)
    print("TESTING CAR VARIANTS MAPPING")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        ('Toyota', 'Corolla'),
        ('Honda', 'Civic'),
        ('Suzuki', 'Alto'),
        ('Toyota', 'Grande'),  # This should use Corolla variants
        ('Honda', 'City'),
        ('Unknown', 'Car')     # This should use generic variants
    ]
    
    for make, model in test_cases:
        print(f"\n🚗 Testing {make} {model}:")
        
        # Get variants
        variants = get_car_variants(make, model)
        print(f"   Variants: {variants}")
        
        # Get car info
        car_info = get_car_info(make, model)
        print(f"   Description: {car_info['description']}")
        print(f"   Engines: {car_info['engines']}")
        print(f"   Transmissions: {car_info['transmissions']}")
        
        # Test variant validation
        if variants:
            test_variant = variants[0]
            is_valid = is_valid_variant(make, model, test_variant)
            print(f"   Is '{test_variant}' valid?: {is_valid}")
    
    print("\n" + "=" * 60)
    print("✅ CAR VARIANTS MAPPING TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_car_variants()
