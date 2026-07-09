import pandas as pd
import numpy as np

def compare_cleaning_approaches():
    """Compare the old vs new data cleaning approaches."""
    
    print("="*80)
    print("DATA CLEANING COMPARISON ANALYSIS")
    print("="*80)
    
    # Load old cleaned data
    try:
        old_df = pd.read_csv('data/pakwheels_listings_cleaned.csv')
        print(f"\n📊 OLD CLEANED DATA:")
        print(f"   Shape: {old_df.shape}")
        print(f"   Columns: {list(old_df.columns)}")
        print(f"   Data Size: {old_df.shape[0]:,} rows, {old_df.shape[1]} columns")
    except FileNotFoundError:
        print("\n❌ Old cleaned data not found")
        old_df = None
    
    # Load new enhanced data
    try:
        new_df = pd.read_csv('data/cleaned/cleaned_enhanced_2025-07-11_05-12-45.csv')
        print(f"\n📊 NEW ENHANCED DATA:")
        print(f"   Shape: {new_df.shape}")
        print(f"   Columns: {len(new_df.columns)} total")
        print(f"   Data Size: {new_df.shape[0]:,} rows, {new_df.shape[1]} columns")
    except FileNotFoundError:
        print("\n❌ New enhanced data not found")
        new_df = None
    
    if old_df is not None and new_df is not None:
        print(f"\n🔄 COMPARISON SUMMARY:")
        print(f"   Data Volume Increase: {new_df.shape[0] - old_df.shape[0]:,} rows ({((new_df.shape[0]/old_df.shape[0])-1)*100:.1f}% increase)")
        print(f"   Feature Richness: {new_df.shape[1] - old_df.shape[1]} additional columns")
        print(f"   Data Completeness: From {old_df.shape[1]} to {new_df.shape[1]} features")
    
    # Feature extraction improvements
    print(f"\n🎯 FEATURE EXTRACTION IMPROVEMENTS:")
    print(f"   ✅ Enhanced Variant Detection: Improved from basic to advanced regex patterns")
    print(f"   ✅ Engine Capacity Extraction: Now supports both CC and Liter formats")
    print(f"   ✅ Transmission Type Recognition: Better AT/MT detection")
    print(f"   ✅ Make/Model Extraction: Covers 20+ car brands popular in Pakistan")
    print(f"   ✅ Year Extraction: Robust 4-digit year detection (1980-2025)")
    print(f"   ✅ Price Extraction: Handles Lakh/Crore Pakistani currency formats")
    print(f"   ✅ Location Extraction: Identifies major Pakistani cities")
    print(f"   ✅ Body Type Classification: Sedan, SUV, Hatchback, etc.")
    
    # Data quality improvements
    if new_df is not None:
        print(f"\n📈 DATA QUALITY METRICS:")
        total_rows = len(new_df)
        
        # Variant extraction quality
        unknown_variants = (new_df['extracted_variant'] == 'unknown').sum()
        variant_success = ((total_rows - unknown_variants) / total_rows) * 100
        print(f"   🚗 Variant Detection Success: {variant_success:.1f}% ({total_rows - unknown_variants:,} out of {total_rows:,})")
        
        # Engine capacity extraction quality
        missing_engine = new_df['extracted_engine_capacity_cc'].isnull().sum()
        engine_success = ((total_rows - missing_engine) / total_rows) * 100
        print(f"   🔧 Engine Capacity Success: {engine_success:.1f}% ({total_rows - missing_engine:,} out of {total_rows:,})")
        
        # Transmission type extraction quality
        unknown_transmission = (new_df['extracted_transmission_type'] == 'unknown').sum()
        transmission_success = ((total_rows - unknown_transmission) / total_rows) * 100
        print(f"   ⚙️  Transmission Type Success: {transmission_success:.1f}% ({total_rows - unknown_transmission:,} out of {total_rows:,})")
        
        # Location extraction quality (if exists)
        if 'extracted_location' in new_df.columns:
            unknown_location = (new_df['extracted_location'] == 'unknown').sum()
            location_success = ((total_rows - unknown_location) / total_rows) * 100
            print(f"   📍 Location Detection Success: {location_success:.1f}% ({total_rows - unknown_location:,} out of {total_rows:,})")
        
        # Body type extraction quality (if exists)
        if 'extracted_body_type' in new_df.columns:
            unknown_body_type = (new_df['extracted_body_type'] == 'unknown').sum()
            body_type_success = ((total_rows - unknown_body_type) / total_rows) * 100
            print(f"   🚙 Body Type Success: {body_type_success:.1f}% ({total_rows - unknown_body_type:,} out of {total_rows:,})")
    
    # Algorithm improvements
    print(f"\n🔬 ALGORITHM IMPROVEMENTS:")
    print(f"   🎯 Multi-Pass Extraction: Tries description first, then name field")
    print(f"   🎯 Fallback Mechanisms: Multiple regex patterns for better coverage")
    print(f"   🎯 Pakistani Market Focus: Tailored for local car variants and brands")
    print(f"   🎯 Context-Aware Parsing: Uses make/model context for better accuracy")
    print(f"   🎯 Data Validation: Filters out noise and invalid entries")
    
    # Processing improvements
    print(f"\n⚡ PROCESSING IMPROVEMENTS:")
    print(f"   📊 Comprehensive Reporting: Detailed summary with statistics")
    print(f"   📁 Organized Output: Timestamped files with structured naming")
    print(f"   🔍 Quality Metrics: Success rates and coverage percentages")
    print(f"   📈 Progress Tracking: Real-time feedback during processing")
    
    print("="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    compare_cleaning_approaches()
