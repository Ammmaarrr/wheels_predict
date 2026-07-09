import sys
print("Python version:", sys.version)
print("Current working directory:", sys.path[0])
print("Python executable:", sys.executable)

# Try to import the enhanced_api_wrapper
try:
    from enhanced_api_wrapper import enhanced_api
    print("✅ Enhanced API wrapper imported successfully")
    print("✅ Enhanced data loaded:", enhanced_api.enhanced_data is not None)
    if enhanced_api.enhanced_data is not None:
        print("   Data shape:", enhanced_api.enhanced_data.shape)
        print("   Available columns:", list(enhanced_api.enhanced_data.columns)[:10])
except Exception as e:
    print("❌ Error importing enhanced API wrapper:", e)
    import traceback
    traceback.print_exc()
