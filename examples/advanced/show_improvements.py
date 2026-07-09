#!/usr/bin/env python3
"""
Simple script to show the key improvements in feature extraction
"""

import pandas as pd

def show_key_improvements():
    print("PAKWHEELS ML PLATFORM - FEATURE EXTRACTION IMPROVEMENTS")
    print("="*60)
    
    # Load enhanced data
    enhanced_data = pd.read_csv('data/cleaned/cleaned_enhanced_2025-07-11_04-30-36.csv')
    
    print(f"Enhanced data shape: {enhanced_data.shape}")
    print(f"Total records: {len(enhanced_data):,}")
    
    # Show extracted features
    print("\nNEW EXTRACTED FEATURES:")
    print("-" * 30)
    
    features = {
        'extracted_variant': 'Car Variant',
        'extracted_engine_capacity_cc': 'Engine Capacity (CC)',
        'extracted_transmission_type': 'Transmission Type',
        'extracted_make': 'Car Make',
        'extracted_model': 'Car Model',
        'extracted_year': 'Year'
    }
    
    for col, desc in features.items():
        if col in enhanced_data.columns:
            non_null = enhanced_data[col].notna().sum()
            rate = non_null / len(enhanced_data) * 100
            print(f"{desc}: {non_null:,} / {len(enhanced_data):,} ({rate:.1f}%)")
    
    # Show sample extractions
    print("\nSAMPLE EXTRACTIONS:")
    print("-" * 30)
    
    sample = enhanced_data.head(3)
    for idx, row in sample.iterrows():
        print(f"\nExample {idx + 1}:")
        print(f"  Name: {str(row.get('name', 'N/A'))[:60]}...")
        print(f"  Make: {row.get('extracted_make', 'N/A')}")
        print(f"  Model: {row.get('extracted_model', 'N/A')}")
        print(f"  Engine: {row.get('extracted_engine_capacity_cc', 'N/A')} CC")
        print(f"  Transmission: {row.get('extracted_transmission_type', 'N/A')}")
    
    print("\n" + "="*60)
    print("SUCCESS: Structured features extracted from unstructured text!")
    print("="*60)

if __name__ == "__main__":
    show_key_improvements()
