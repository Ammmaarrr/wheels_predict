"""
Step by Step Testing - Performance Metrics
"""

import time

print("=" * 60)
print("STEP 5: TESTING PERFORMANCE METRICS")
print("=" * 60)

try:
    from enhanced_api_wrapper import enhanced_api
    
    # Test response times
    print("⚡ Testing response times...")
    
    test_runs = 5
    total_time = 0
    successful_runs = 0
    
    test_car = {
        'make': 'Honda',
        'model': 'Civic',
        'year': 2020,
        'engine_capacity': 1800,
        'transmission': 'automatic',
        'variant': 'vti'
    }
    
    print(f"Running {test_runs} performance tests...")
    
    for i in range(test_runs):
        try:
            start_time = time.time()
            result = enhanced_api.predict_price_enhanced(**test_car)
            end_time = time.time()
            
            run_time = end_time - start_time
            total_time += run_time
            successful_runs += 1
            
            print(f"✅ Run {i+1}: {run_time:.3f}s | Price: {result['predicted_price']:,} PKR")
            
        except Exception as e:
            print(f"❌ Run {i+1}: Error - {e}")
    
    if successful_runs > 0:
        avg_time = total_time / successful_runs
        print(f"\n📊 Performance Summary:")
        print(f"   Successful runs: {successful_runs}/{test_runs}")
        print(f"   Average Response Time: {avg_time:.3f}s")
        print(f"   Total Test Time: {total_time:.3f}s")
        print(f"   Requests per Second: {successful_runs/total_time:.1f}")
        
        # Performance thresholds
        if avg_time < 0.5:
            print(f"✅ Performance: EXCELLENT (< 0.5s)")
        elif avg_time < 1.0:
            print(f"✅ Performance: GOOD (< 1.0s)")
        elif avg_time < 2.0:
            print(f"⚠️  Performance: ACCEPTABLE (< 2.0s)")
        else:
            print(f"❌ Performance: NEEDS IMPROVEMENT (> 2.0s)")
    
    # Test data loading performance
    print(f"\n📊 Testing data access performance...")
    
    try:
        start_time = time.time()
        data_shape = enhanced_api.enhanced_data.shape if enhanced_api.enhanced_data is not None else (0, 0)
        data_time = time.time() - start_time
        
        print(f"✅ Data access: {data_time:.3f}s | Shape: {data_shape}")
        
    except Exception as e:
        print(f"❌ Data access error: {e}")
    
    # Test memory usage (simplified)
    print(f"\n💾 Testing memory usage...")
    
    try:
        import sys
        if enhanced_api.enhanced_data is not None:
            memory_usage = sys.getsizeof(enhanced_api.enhanced_data) / (1024 * 1024)  # MB
            print(f"✅ Data memory usage: {memory_usage:.2f} MB")
        else:
            print(f"❌ No data loaded for memory test")
            
    except Exception as e:
        print(f"❌ Memory test error: {e}")

except Exception as e:
    print(f"❌ Error testing performance: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 5 COMPLETED!")
print("=" * 60)
