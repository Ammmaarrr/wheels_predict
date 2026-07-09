"""
Step by Step Testing - Enhanced Recommendations
"""

print("=" * 60)
print("STEP 4: TESTING ENHANCED RECOMMENDATIONS")
print("=" * 60)

try:
    from src.pakwheels_ml.models.enhanced_api_wrapper import enhanced_api
    
    # Test budget-based recommendations
    print("💰 Testing budget-based recommendations...")
    
    budget_scenarios = [
        {
            'name': 'Budget Cars (20 Lakh)',
            'budget': 2000000,
            'preferences': {'transmission': 'manual'}
        },
        {
            'name': 'Mid-Range (35 Lakh)',
            'budget': 3500000,
            'preferences': {'transmission': 'automatic'}
        },
        {
            'name': 'Premium (50 Lakh)',
            'budget': 5000000,
            'preferences': {'min_year': 2019}
        }
    ]
    
    for i, scenario in enumerate(budget_scenarios, 1):
        print(f"\n{i}. Testing: {scenario['name']}")
        
        try:
            recommendations = enhanced_api.get_enhanced_recommendations(
                budget=scenario['budget'],
                preferences=scenario['preferences']
            )
            
            print(f"✅ Found {len(recommendations)} recommendations")
            
            # Show top 3 recommendations
            for j, rec in enumerate(recommendations[:3], 1):
                print(f"   {j}. {rec['make']} {rec['model']} {rec['year']}")
                print(f"      💰 {rec['price']:,} PKR | 🔧 {rec.get('engine_capacity', 'N/A')}cc")
                print(f"      📈 Score: {rec.get('match_score', 'N/A')}")
                
        except Exception as e:
            print(f"❌ Error in {scenario['name']}: {e}")
    
    # Test specific car recommendations
    print(f"\n🔧 Testing specific car recommendations...")
    
    try:
        specific_recs = enhanced_api.get_recommendations_enhanced(
            make="Toyota",
            model="Corolla",
            year=2020,
            budget_range=(1500000, 2500000),
            limit=5
        )
        
        print(f"✅ Found {len(specific_recs)} Toyota Corolla recommendations")
        for i, rec in enumerate(specific_recs[:3], 1):
            print(f"   {i}. {rec['make']} {rec['model']} {rec['year']}")
            print(f"      💰 {rec['price']:,} PKR | 🎯 Similarity: {rec.get('similarity_score', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error in specific recommendations: {e}")
    
except Exception as e:
    print(f"❌ Error testing recommendations: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("STEP 4 COMPLETED!")
print("=" * 60)
