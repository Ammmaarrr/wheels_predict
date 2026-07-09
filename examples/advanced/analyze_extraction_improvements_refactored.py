#!/usr/bin/env python3
"""
Script to analyze and demonstrate the feature extraction improvements
in the enhanced data processing pipeline.
"""

import pandas as pd
import numpy as np

def load_datasets():
    """Load raw and enhanced datasets."""
    print("\n1. Loading raw data...")
    raw_data = pd.read_csv('data/pakwheels_listings.csv')
    print(f"Raw data shape: {raw_data.shape}")
    print(f"Raw data columns: {list(raw_data.columns)}")
    
    print("\n2. Loading enhanced data...")
    enhanced_data = pd.read_csv('data/cleaned/cleaned_enhanced_2025-07-11_04-30-36.csv')
    print(f"Enhanced data shape: {enhanced_data.shape}")
    print(f"Enhanced data columns: {list(enhanced_data.columns)}")
    
    return raw_data, enhanced_data

def analyze_extracted_features(enhanced_data):
    """Analyze and display extracted features."""
    print("\n3. NEW EXTRACTED FEATURES:")
    print("="*50)
    
    new_features = ['extracted_variant', 'extracted_engine_capacity_cc', 
                   'extracted_transmission_type', 'extracted_make', 
                   'extracted_model', 'extracted_year']
    
    for feature in new_features:
        if feature in enhanced_data.columns:
            print(f"\n✓ {feature.upper().replace('_', ' ')}")
            print(f"  Non-null values: {enhanced_data[feature].notna().sum():,} / {len(enhanced_data):,}")
            print(f"  Extraction rate: {enhanced_data[feature].notna().sum() / len(enhanced_data) * 100:.1f}%")
            
            # Show top values
            if enhanced_data[feature].dtype == 'object':
                top_values = enhanced_data[feature].value_counts().head(5)
                print(f"  Top 5 values: {dict(top_values)}")
            else:
                print(f"  Sample values: {enhanced_data[feature].dropna().head(5).tolist()}")

def compare_data_quality(raw_data, enhanced_data):
    """Compare data quality improvements between raw and enhanced data."""
    print("\n4. DATA QUALITY IMPROVEMENTS:")
    print("="*50)
    
    # Check original columns that might have been sparse
    original_columns = ['make', 'model', 'year', 'transmission', 'engine_capacity']
    
    for col in original_columns:
        if col in raw_data.columns:
            raw_non_null = raw_data[col].notna().sum()
            raw_rate = raw_non_null / len(raw_data) * 100
            
            # Find corresponding extracted column
            extracted_col = f'extracted_{col}'
            if col == 'engine_capacity':
                extracted_col = 'extracted_engine_capacity_cc'
            elif col == 'transmission':
                extracted_col = 'extracted_transmission_type'
            
            if extracted_col in enhanced_data.columns:
                enhanced_non_null = enhanced_data[extracted_col].notna().sum()
                enhanced_rate = enhanced_non_null / len(enhanced_data) * 100
                
                print(f"\n{col.upper()}:")
                print(f"  Raw data: {raw_non_null:,} / {len(raw_data):,} ({raw_rate:.1f}%)")
                print(f"  Enhanced: {enhanced_non_null:,} / {len(enhanced_data):,} ({enhanced_rate:.1f}%)")
                print(f"  Improvement: +{enhanced_rate - raw_rate:.1f} percentage points")

def show_extraction_examples(enhanced_data):
    """Show example extractions from enhanced data."""
    print("\n5. EXAMPLE EXTRACTIONS:")
    print("="*50)
    
    # Get sample rows to show extraction
    sample_rows = enhanced_data.head(10)
    
    for idx, row in sample_rows.iterrows():
        print(f"\nExample {idx + 1}:")
        print(f"  Original Name: {row.get('name', 'N/A')[:80]}...")
        print(f"  Extracted Make: {row.get('extracted_make', 'N/A')}")
        print(f"  Extracted Model: {row.get('extracted_model', 'N/A')}")
        print(f"  Extracted Variant: {row.get('extracted_variant', 'N/A')}")
        print(f"  Extracted Engine: {row.get('extracted_engine_capacity_cc', 'N/A')} CC")
        print(f"  Extracted Transmission: {row.get('extracted_transmission_type', 'N/A')}")
        print(f"  Extracted Year: {row.get('extracted_year', 'N/A')}")
        
        if idx >= 4:  # Show first 5 examples
            break

def assess_ml_readiness(enhanced_data):
    """Assess ML readiness of the enhanced dataset."""
    print("\n6. ML READINESS ASSESSMENT:")
    print("="*50)
    
    # Calculate how many rows have complete feature sets
    core_features = ['extracted_make', 'extracted_model', 'extracted_engine_capacity_cc', 
                    'extracted_transmission_type', 'extracted_year']
    
    complete_rows = enhanced_data[core_features].notna().all(axis=1).sum()
    completeness_rate = complete_rows / len(enhanced_data) * 100
    
    print(f"Rows with complete core features: {complete_rows:,} / {len(enhanced_data):,}")
    print(f"ML readiness rate: {completeness_rate:.1f}%")

def analyze_feature_distributions(enhanced_data):
    """Analyze the distribution of extracted features."""
    print("\n7. FEATURE DISTRIBUTION ANALYSIS:")
    print("="*50)
    
    # Engine capacity distribution
    if 'extracted_engine_capacity_cc' in enhanced_data.columns:
        engine_stats = enhanced_data['extracted_engine_capacity_cc'].describe()
        print(f"\nEngine Capacity (CC) Statistics:")
        print(f"  Count: {engine_stats['count']:.0f}")
        print(f"  Mean: {engine_stats['mean']:.0f} CC")
        print(f"  Std: {engine_stats['std']:.0f} CC")
        print(f"  Min: {engine_stats['min']:.0f} CC")
        print(f"  Max: {engine_stats['max']:.0f} CC")
    
    # Transmission distribution
    if 'extracted_transmission_type' in enhanced_data.columns:
        trans_dist = enhanced_data['extracted_transmission_type'].value_counts()
        print(f"\nTransmission Type Distribution:")
        for trans_type, count in trans_dist.items():
            print(f"  {trans_type.title()}: {count:,} ({count/len(enhanced_data)*100:.1f}%)")
    
    # Make distribution
    if 'extracted_make' in enhanced_data.columns:
        make_dist = enhanced_data['extracted_make'].value_counts().head(10)
        print(f"\nTop 10 Car Makes:")
        for make, count in make_dist.items():
            print(f"  {make}: {count:,} ({count/len(enhanced_data)*100:.1f}%)")

def analyze_extraction_improvements():
    """Main function to analyze extraction improvements."""
    
    print("="*80)
    print("PAKWHEELS ML PLATFORM - FEATURE EXTRACTION IMPROVEMENTS")
    print("="*80)
    
    # Load datasets
    raw_data, enhanced_data = load_datasets()
    
    # Analyze extracted features
    analyze_extracted_features(enhanced_data)
    
    # Compare data quality
    compare_data_quality(raw_data, enhanced_data)
    
    # Show examples
    show_extraction_examples(enhanced_data)
    
    # Assess ML readiness
    assess_ml_readiness(enhanced_data)
    
    # Analyze feature distributions
    analyze_feature_distributions(enhanced_data)
    
    print("\n" + "="*80)
    print("SUMMARY: Enhanced data processing successfully extracted structured")
    print("features from unstructured text, significantly improving ML readiness!")
    print("="*80)

if __name__ == "__main__":
    analyze_extraction_improvements()
