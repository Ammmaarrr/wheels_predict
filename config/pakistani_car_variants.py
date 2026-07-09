"""
Pakistani Car Variants Mapping
Complete mapping of car models to their available variants in the Pakistani market
"""

# Pakistani automotive market variants mapping
PAKISTANI_CAR_VARIANTS = {
    'toyota': {
        'corolla': {
            'variants': ['xli', 'gli', 'altis', 'grande', 'se'],
            'description': 'Popular sedan with multiple trim levels',
            'engines': [1300, 1600, 1800],
            'transmissions': ['manual', 'automatic', 'cvt']
        },
        'vitz': {
            'variants': ['f', 'u', 'jewela'],
            'description': 'Compact hatchback',
            'engines': [1000, 1300],
            'transmissions': ['manual', 'automatic']
        },
        'prius': {
            'variants': ['standard', 'alpha', 'g'],
            'description': 'Hybrid sedan',
            'engines': [1800],
            'transmissions': ['automatic']
        },
        'camry': {
            'variants': ['up-spec', 'hybrid', 'grande'],
            'description': 'Executive sedan',
            'engines': [2000, 2500],
            'transmissions': ['automatic']
        },
        'hilux': {
            'variants': ['single cabin', 'double cabin', 'extra cabin'],
            'description': 'Pickup truck',
            'engines': [2400, 2800],
            'transmissions': ['manual', 'automatic']
        },
        'fortuner': {
            'variants': ['2.7 vvt-i', '2.8 sigma 4'],
            'description': 'SUV',
            'engines': [2700, 2800],
            'transmissions': ['manual', 'automatic']
        },
        'land cruiser': {
            'variants': ['gx', 'gxr', 'vx'],
            'description': 'Premium SUV',
            'engines': [4000, 4600],
            'transmissions': ['automatic']
        }
    },
    'honda': {
        'civic': {
            'variants': ['vti', 'vti oriel', 'rs', 'type r'],
            'description': 'Sporty sedan',
            'engines': [1500, 1800, 2000],
            'transmissions': ['manual', 'automatic', 'cvt']
        },
        'city': {
            'variants': ['aspire', 'aspire prosmatec', 'ivtec', 'cvt'],
            'description': 'Compact sedan',
            'engines': [1300, 1500],
            'transmissions': ['manual', 'automatic', 'cvt']
        },
        'accord': {
            'variants': ['cp2', 'cp3', 'executive'],
            'description': 'Executive sedan',
            'engines': [2000, 2400],
            'transmissions': ['automatic']
        },
        'crv': {
            'variants': ['i-vtec', 'exec'],
            'description': 'Compact SUV',
            'engines': [2000, 2400],
            'transmissions': ['automatic']
        },
        'brv': {
            'variants': ['i-vtec', 'cvt'],
            'description': 'Compact SUV',
            'engines': [1500],
            'transmissions': ['manual', 'cvt']
        },
        'fit': {
            'variants': ['hybrid', 'standard'],
            'description': 'Hatchback',
            'engines': [1300, 1500],
            'transmissions': ['automatic', 'cvt']
        }
    },
    'suzuki': {
        'alto': {
            'variants': ['vx', 'vxr', 'vxl'],
            'description': 'Entry-level hatchback',
            'engines': [660, 800],
            'transmissions': ['manual', 'automatic']
        },
        'wagon r': {
            'variants': ['vx', 'vxr', 'vxl'],
            'description': 'Compact hatchback',
            'engines': [1000],
            'transmissions': ['manual', 'automatic']
        },
        'swift': {
            'variants': ['dxg', 'dlx', 'automatic'],
            'description': 'Sporty hatchback',
            'engines': [1300],
            'transmissions': ['manual', 'automatic']
        },
        'cultus': {
            'variants': ['vx', 'vxr', 'vxl', 'ags'],
            'description': 'Compact sedan',
            'engines': [1000],
            'transmissions': ['manual', 'automatic']
        },
        'vitara': {
            'variants': ['glx', 'glx+'],
            'description': 'Compact SUV',
            'engines': [1600],
            'transmissions': ['manual', 'automatic']
        },
        'jimny': {
            'variants': ['standard'],
            'description': 'Compact SUV',
            'engines': [1300],
            'transmissions': ['manual', 'automatic']
        }
    },
    'hyundai': {
        'elantra': {
            'variants': ['gls', 'active'],
            'description': 'Compact sedan',
            'engines': [1800, 2000],
            'transmissions': ['manual', 'automatic']
        },
        'tucson': {
            'variants': ['gls', 'ultimate'],
            'description': 'Compact SUV',
            'engines': [2000],
            'transmissions': ['automatic']
        },
        'sonata': {
            'variants': ['gls', 'limited'],
            'description': 'Executive sedan',
            'engines': [2000, 2400],
            'transmissions': ['automatic']
        },
        'santa fe': {
            'variants': ['gls', 'limited'],
            'description': 'SUV',
            'engines': [2400],
            'transmissions': ['automatic']
        }
    },
    'kia': {
        'sportage': {
            'variants': ['alpha', 'awd'],
            'description': 'Compact SUV',
            'engines': [2000],
            'transmissions': ['automatic']
        },
        'picanto': {
            'variants': ['automatic', 'manual'],
            'description': 'City car',
            'engines': [1000],
            'transmissions': ['manual', 'automatic']
        },
        'stonic': {
            'variants': ['base', 'ex'],
            'description': 'Crossover',
            'engines': [1400],
            'transmissions': ['manual', 'automatic']
        }
    },
    'nissan': {
        'sunny': {
            'variants': ['base', 'ex'],
            'description': 'Compact sedan',
            'engines': [1500],
            'transmissions': ['manual', 'automatic']
        },
        'x-trail': {
            'variants': ['base', 'hybrid'],
            'description': 'SUV',
            'engines': [2000, 2500],
            'transmissions': ['automatic']
        },
        'dayz': {
            'variants': ['base', 'highway star'],
            'description': 'Kei car',
            'engines': [660],
            'transmissions': ['automatic']
        }
    },
    'mitsubishi': {
        'lancer': {
            'variants': ['glx', 'gls'],
            'description': 'Compact sedan',
            'engines': [1300, 1600],
            'transmissions': ['manual', 'automatic']
        },
        'pajero': {
            'variants': ['glx', 'exceed'],
            'description': 'SUV',
            'engines': [3000, 3800],
            'transmissions': ['manual', 'automatic']
        },
        'outlander': {
            'variants': ['base', 'phev'],
            'description': 'SUV',
            'engines': [2000, 2400],
            'transmissions': ['automatic']
        }
    },
    'daihatsu': {
        'mira': {
            'variants': ['e:s', 'x'],
            'description': 'Kei car',
            'engines': [660],
            'transmissions': ['manual', 'automatic']
        },
        'move': {
            'variants': ['l', 'x'],
            'description': 'Kei car',
            'engines': [660],
            'transmissions': ['automatic']
        },
        'hijet': {
            'variants': ['standard', 'cruise'],
            'description': 'Mini truck',
            'engines': [660],
            'transmissions': ['manual', 'automatic']
        }
    }
}

def get_car_variants(make: str, model: str) -> list:
    """Get variants for a specific car make and model."""
    make_lower = make.lower()
    model_lower = model.lower()
    
    if make_lower in PAKISTANI_CAR_VARIANTS:
        if model_lower in PAKISTANI_CAR_VARIANTS[make_lower]:
            return PAKISTANI_CAR_VARIANTS[make_lower][model_lower]['variants']
    
    # Return generic variants if specific car not found
    return ['gli', 'xli', 'vti', 'vxr', 'aspire', 'unknown']

def get_car_info(make: str, model: str) -> dict:
    """Get complete information about a car including variants, engines, etc."""
    make_lower = make.lower()
    model_lower = model.lower()
    
    if make_lower in PAKISTANI_CAR_VARIANTS:
        if model_lower in PAKISTANI_CAR_VARIANTS[make_lower]:
            return PAKISTANI_CAR_VARIANTS[make_lower][model_lower]
    
    # Return default info if specific car not found
    return {
        'variants': ['gli', 'xli', 'vti', 'vxr', 'aspire', 'unknown'],
        'description': 'Generic car',
        'engines': [1300, 1600, 1800],
        'transmissions': ['manual', 'automatic']
    }

def is_valid_variant(make: str, model: str, variant: str) -> bool:
    """Check if a variant is valid for a specific car."""
    variants = get_car_variants(make, model)
    return variant.lower() in [v.lower() for v in variants]

def get_popular_variants(make: str, model: str) -> list:
    """Get popular variants for a specific car (typically the first few)."""
    variants = get_car_variants(make, model)
    # Return first 3 variants as popular ones
    return variants[:3] if len(variants) >= 3 else variants

if __name__ == "__main__":
    # Test the mapping
    print("Pakistani Car Variants Mapping")
    print("=" * 50)
    
    # Test Toyota Corolla
    print("\nToyota Corolla variants:")
    corolla_variants = get_car_variants('Toyota', 'Corolla')
    print(f"  {corolla_variants}")
    
    # Test Honda Civic
    print("\nHonda Civic variants:")
    civic_variants = get_car_variants('Honda', 'Civic')
    print(f"  {civic_variants}")
    
    # Test Suzuki Alto
    print("\nSuzuki Alto variants:")
    alto_variants = get_car_variants('Suzuki', 'Alto')
    print(f"  {alto_variants}")
    
    # Test unknown car
    print("\nUnknown car variants:")
    unknown_variants = get_car_variants('Unknown', 'Car')
    print(f"  {unknown_variants}")
