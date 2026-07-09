"""
Simple Enhanced Features Test
Auto-runs without user input
"""

import sys
import os
import pandas as pd
from datetime import datetime

def test_data_improvements():
    """Test the data improvements."""
    
    print("="*60)
    print("ENHANCED DATA FEATURES TEST")
    print("="*60)
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Load and compare data
    print("\n1. DATA COMPARISON")
    print("-" * 30)
    
    # Load enhanced data
    try:
        data_dir = "data/cleaned"
        files = [f for f in os.listdir(data_dir) if f.startswith("cleaned_enhanced") and f.endswith(".csv")]
        if files:
            latest_file = sorted(files)[-1]
            enhanced_path = os.path.join(data_dir, latest_file)
            enhanced_data = pd.read_csv(enhanced_path, low_memory=False)
            print(f"✅ Enhanced data loaded: {enhanced_data.shape}")
            
            # Show new features
            print("\nNew Enhanced Features:")
            enhanced_features = [col for col in enhanced_data.columns if 'extracted' in col.lower()]
            for feature in enhanced_features:
                non_null_count = enhanced_data[feature].notna().sum()
                print(f"  - {feature}: {non_null_count:,} non-null values")
            
            # Sample data
            print("\nSample Enhanced Data:")
            sample_cols = ['make', 'model', 'year', 'price', 'extracted_variant', 'extracted_engine_capacity_cc', 'extracted_transmission_type']
            available_cols = [col for col in sample_cols if col in enhanced_data.columns]
            print(enhanced_data[available_cols].head(3).to_string())
            
        else:
            print("❌ No enhanced data found")
    except Exception as e:
        print(f"❌ Error loading enhanced data: {e}")
    
    # Test 2: Load original data for comparison
    try:
        old_path = "data/pakwheels_listings_cleaned.csv"
        if os.path.exists(old_path):
            old_data = pd.read_csv(old_path)
            print(f"\n✅ Original data loaded: {old_data.shape}")
            
            # Compare sizes
            if 'enhanced_data' in locals():
                print(f"\nData Size Comparison:")
                print(f"  Original: {old_data.shape[0]:,} rows, {old_data.shape[1]} columns")
                print(f"  Enhanced: {enhanced_data.shape[0]:,} rows, {enhanced_data.shape[1]} columns")
                print(f"  Improvement: {((enhanced_data.shape[0] / old_data.shape[0]) - 1) * 100:.1f}% more rows")
                print(f"  Improvement: {((enhanced_data.shape[1] / old_data.shape[1]) - 1) * 100:.1f}% more features")
        else:
            print("❌ No original data found")
    except Exception as e:
        print(f"❌ Error loading original data: {e}")
    
    # Test 3: Test API wrapper if available
    print("\n2. API WRAPPER TEST")
    print("-" * 30)
    
    try:
        from enhanced_api_wrapper import enhanced_api
        
        # Test price prediction
        print("Testing price prediction...")
        result = enhanced_api.predict_price_enhanced(
            make="Toyota",
            model="Corolla",
            year=2020,
            engine_capacity=1300,
            transmission="manual",
            variant="gli"
        )
        print(f"✅ Price prediction: {result['predicted_price']:,.0f} PKR")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Market position: {result['market_position']}")
        
    except Exception as e:
        print(f"❌ API wrapper test failed: {e}")
    
    # Test 4: Data processing functions
    print("\n3. DATA PROCESSING FUNCTIONS TEST")
    print("-" * 30)
    
    try:
        sys.path.append('data_processing')
        from clean_and_preprocess import (
            extract_variant, extract_engine_capacity_cc, extract_transmission_type
        )
        
        test_titles = [
            "Honda Civic VTi 2020 AT 1.8L for sale in Lahore",
            "Toyota Corolla GLI 2019 MT 1.3L available in Karachi",
            "Suzuki Alto VXR 2021 660cc manual transmission"
        ]
        
        print("Testing extraction functions:")
        for title in test_titles:
            variant = extract_variant(title)
            engine = extract_engine_capacity_cc(title)
            transmission = extract_transmission_type(title)
            
            print(f"\nTitle: {title}")
            print(f"  Variant: {variant}")
            print(f"  Engine: {engine} CC")
            print(f"  Transmission: {transmission}")
            
    except Exception as e:
        print(f"❌ Data processing test failed: {e}")
    
    print("\n" + "="*60)
    print("ENHANCED FEATURES TEST COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    test_data_improvements()
