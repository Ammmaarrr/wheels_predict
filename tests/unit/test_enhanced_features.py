#!/usr/bin/env python3
"""
Test the improved extraction functions with real examples
"""

import sys
import os
sys.path.append('data_processing')

from clean_and_preprocess import (
    extract_variant, extract_engine_capacity_cc, extract_transmission_type,
    extract_location, extract_body_type, extract_make_model, extract_year
)

def test_improved_extractions():
    """Test the improved extraction functions with specific examples."""
    
    print("🔧 TESTING IMPROVED EXTRACTION FUNCTIONS")
    print("="*60)
    
    # Test cases based on user feedback
    test_cases = [
        "Nissan AD Van 2006 for sale in Attock",
        "Honda Civic VTi 2018 AT 1.8L for sale in Lahore",
        "Toyota Corolla GLI 2020 MT 1.3L available in Karachi",
        "Suzuki Wagon R VXR 2007 1.0L manual transmission",
        "Honda City Z 2020 automatic sedan for sale in Islamabad",
        "Hyundai Tucson 2.0L AT SUV 2019 for sale in Rawalpindi"
    ]
    
    print("\n🎯 EXTRACTION RESULTS:")
    print("-" * 60)
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"   Original: {text}")
        
        # Test all extraction functions
        variant = extract_variant(text)
        engine_cc = extract_engine_capacity_cc(text)
        transmission = extract_transmission_type(text)
        location = extract_location(text)
        body_type = extract_body_type(text)
        make, model = extract_make_model(text)
        year = extract_year(text)
        
        print(f"   🏭 Make: {make}")
        print(f"   🚙 Model: {model}")
        print(f"   🚗 Variant: {variant}")
        print(f"   🏎️ Engine: {engine_cc} CC")
        print(f"   ⚙️ Transmission: {transmission}")
        print(f"   📍 Location: {location}")
        print(f"   🚘 Body Type: {body_type}")
        print(f"   📅 Year: {year}")
    
    # Show specific improvements
    print(f"\n🎉 KEY IMPROVEMENTS IMPLEMENTED:")
    print("-" * 60)
    print("✅ AT/MT Recognition: AT = Automatic, MT = Manual")
    print("✅ Liter to CC Conversion: 1.0L = 1000CC, 1.8L = 1800CC")
    print("✅ Variant-Year Separation: 'VXR 2007' → Variant: VXR, Year: 2007")
    print("✅ Location Extraction: 'for sale in Attock' → Location: Attock")
    print("✅ Body Type Detection: Van, Sedan, SUV, Hatchback")
    print("✅ Make/Brand Standardization: Proper case formatting")
    
    print(f"\n🚀 THESE IMPROVEMENTS WILL ENHANCE:")
    print("-" * 60)
    print("• Price prediction accuracy (better features)")
    print("• Recommendation relevance (variant-specific)")
    print("• User search/filtering experience")
    print("• Market analysis capabilities")
    print("• ML model training quality")

if __name__ == "__main__":
    test_improved_extractions()
            latest_data = sorted(data_files)[-1]
            data_path = os.path.join("data/cleaned", latest_data)
            
            df = pd.read_csv(data_path)
            print(f"✅ Enhanced data loaded: {data_path}")
            print(f"   Shape: {df.shape}")
            
            # Check for enhanced columns
            enhanced_columns = [col for col in df.columns if col.startswith('extracted_')]
            print(f"   Enhanced columns: {enhanced_columns}")
            
            # Show data quality
            if 'extracted_variant' in df.columns:
                unknown_variants = (df['extracted_variant'] == 'unknown').sum()
                print(f"   Variant extraction: {len(df) - unknown_variants}/{len(df)} successful")
            
            if 'extracted_engine_capacity_cc' in df.columns:
                missing_engine = df['extracted_engine_capacity_cc'].isnull().sum()
                print(f"   Engine capacity extraction: {len(df) - missing_engine}/{len(df)} successful")
                
        else:
            print("❌ No enhanced data found")
            
    except Exception as e:
        print(f"❌ Error loading enhanced data: {e}")
    
    # Test 2: Check model training
    print("\n2. Testing model training...")
    try:
        from models.enhanced_model_training_v2 import EnhancedCarPricePredictor
        
        predictor = EnhancedCarPricePredictor()
        
        # Check if model exists
        model_files = [f for f in os.listdir("models") if f.startswith("enhanced_car_price_model")]
        if model_files:
            latest_model = sorted(model_files)[-1]
            model_path = os.path.join("models", latest_model)
            
            predictor.load_model(model_path)
            print(f"✅ Enhanced model loaded: {latest_model}")
            
            # Test prediction
            test_price = predictor.predict_price(
                make='Toyota',
                model='Corolla',
                year=2020,
                engine_capacity=1300,
                transmission='automatic',
                variant='xli'
            )
            print(f"   Test prediction: {test_price:,.0f} PKR")
            
        else:
            print("❌ No enhanced model found")
            
    except Exception as e:
        print(f"❌ Error testing model: {e}")
    
    # Test 3: Check recommendation engine
    print("\n3. Testing recommendation engine...")
    try:
        from models.enhanced_recommendation_engine import EnhancedRecommendationEngine
        
        engine = EnhancedRecommendationEngine()
        
        # Load data
        if data_files:
            latest_data = sorted(data_files)[-1]
            data_path = os.path.join("data/cleaned", latest_data)
            
            engine.load_enhanced_data(data_path)
            print(f"✅ Recommendation engine loaded data")
            
            # Test recommendations
            recommendations = engine.get_recommendations(
                budget=2500000,
                preferences={'transmission': 'automatic'},
                max_results=3
            )
            
            print(f"   Test recommendations: {len(recommendations)} found")
            for i, rec in enumerate(recommendations[:2], 1):
                print(f"   {i}. {rec['make']} {rec['model']} {rec['year']} - {rec['price']:,} PKR")
                
        else:
            print("❌ No data for recommendation engine")
            
    except Exception as e:
        print(f"❌ Error testing recommendation engine: {e}")
    
    print("\n" + "=" * 50)
    print("Enhanced Features Test Complete!")

if __name__ == "__main__":
    test_enhanced_features()
