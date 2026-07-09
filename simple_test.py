#!/usr/bin/env python3
"""Simple test without imports"""

print("Starting simple test...")
print("Python is working normally")

# Try to read some data files
import os
import pandas as pd

try:
    # Check if enhanced data exists
    data_dir = "data/cleaned"
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.startswith("cleaned_enhanced") and f.endswith(".csv")]
        if files:
            latest_file = sorted(files)[-1]
            data_path = os.path.join(data_dir, latest_file)
            print(f"Enhanced data file found: {latest_file}")
            
            # Load and check data
            df = pd.read_csv(data_path, low_memory=False)
            print(f"Data shape: {df.shape}")
            print(f"Columns: {list(df.columns)[:10]}")
            print("✅ Enhanced data loaded successfully")
        else:
            print("No enhanced data files found")
    else:
        print("Data directory not found")
        
    # Test complete
    print("✅ Simple test completed successfully")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
