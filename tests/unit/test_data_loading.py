"""
Test script to verify enhanced data loading
"""
import pandas as pd
import os

def test_data_loading():
    """Test loading enhanced data."""
    print("Testing enhanced data loading...")
    
    # Find latest enhanced data
    data_dir = "data/cleaned"
    files = [f for f in os.listdir(data_dir) if f.startswith("cleaned_enhanced") and f.endswith(".csv")]
    
    if not files:
        print("No enhanced data files found!")
        return
    
    latest_file = sorted(files)[-1]
    full_path = os.path.join(data_dir, latest_file)
    
    print(f"Loading: {full_path}")
    
    try:
        df = pd.read_csv(full_path, low_memory=False)
        print(f"✅ Successfully loaded data: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:")
        print(df.head(2))
        
        # Check for enhanced features
        enhanced_features = [col for col in df.columns if col.startswith('extracted_')]
        print(f"\\nEnhanced features found: {enhanced_features}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None

if __name__ == "__main__":
    test_data_loading()
