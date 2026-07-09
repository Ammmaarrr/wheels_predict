"""
Interactive Enhanced Features Demo
Allows interactive testing of enhanced features
"""

import sys
import os
from enhanced_api_wrapper import enhanced_api

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from pakistani_car_variants import get_car_variants, get_car_info, is_valid_variant
    HAS_VARIANT_MAPPING = True
except ImportError:
    HAS_VARIANT_MAPPING = False

class InteractiveDemo:
    """Interactive demo for enhanced features."""
    
    def __init__(self):
        self.running = True
        
    def print_menu(self):
        """Print the main menu."""
        print("\n" + "="*60)
        print("ENHANCED FEATURES INTERACTIVE DEMO")
        print("="*60)
        print("1. Test Price Prediction")
        print("2. Test Recommendations")
        print("3. Compare Variants")
        print("4. Market Analysis")
        print("5. Quick Test (Popular Cars)")
        print("6. Performance Test")
        print("7. Exit")
        print("="*60)
    
    def test_price_prediction(self):
        """Interactive price prediction test."""
        print("\n🚗 PRICE PREDICTION TEST")
        print("-" * 30)
        
        try:
            # Get user input
            make = input("Enter car make (e.g., Toyota, Honda, Suzuki): ").strip()
            model = input("Enter car model (e.g., Corolla, Civic, Alto): ").strip()
            year = int(input("Enter year (e.g., 2020): "))
            engine_capacity = float(input("Enter engine capacity in cc (e.g., 1300): "))
            transmission = input("Enter transmission (manual/automatic): ").strip().lower()
            variant = input("Enter variant (e.g., GLI, VTi, VXR) or 'unknown': ").strip().lower()
            
            # Get prediction
            print("\n⏳ Getting prediction...")
            result = enhanced_api.predict_price_enhanced(
                make=make,
                model=model,
                year=year,
                engine_capacity=engine_capacity,
                transmission=transmission,
                variant=variant
            )
            
            # Display results
            print(f"\n✅ PREDICTION RESULTS:")
            print(f"   💰 Predicted Price: {result['predicted_price']:,} PKR")
            print(f"   📊 Confidence: {result['confidence']:.2f}")
            print(f"   📈 Price Range: {result['price_range']['min']:,.0f} - {result['price_range']['max']:,.0f}")
            print(f"   🔧 Model Type: {result['model_info']['type']}")
            
            # Show enhanced features
            features = result['features_used']
            print(f"\n🎯 ENHANCED FEATURES ANALYSIS:")
            print(f"   🏭 Japanese Brand: {features.get('is_japanese', 'N/A')}")
            print(f"   ⭐ Popular Variant: {features.get('is_popular_variant', 'N/A')}")
            print(f"   ⚙️ Automatic: {features.get('is_automatic', 'N/A')}")
            print(f"   🌟 Recent Model: {features.get('is_recent', 'N/A')}")
            print(f"   🔧 Engine Category: {features.get('engine_category', 'N/A')}")
            print(f"   📅 Car Age: {features.get('car_age', 'N/A')} years")
            
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def test_recommendations(self):
        """Interactive recommendations test."""
        print("\n🎯 RECOMMENDATIONS TEST")
        print("-" * 30)
        
        try:
            # Get user input
            budget = float(input("Enter your budget in PKR (e.g., 3000000): "))
            
            print("\nOptional preferences (press Enter to skip):")
            transmission = input("Preferred transmission (manual/automatic): ").strip().lower()
            min_year = input("Minimum year (e.g., 2018): ").strip()
            make = input("Preferred make (e.g., Toyota, Honda): ").strip()
            
            # Build preferences
            preferences = {}
            if transmission:
                preferences['transmission'] = transmission
            if min_year:
                preferences['min_year'] = int(min_year)
            if make:
                preferences['make'] = make
            
            # Get recommendations
            print("\n⏳ Getting recommendations...")
            recommendations = enhanced_api.get_enhanced_recommendations(
                budget=budget,
                preferences=preferences
            )
            
            # Display results
            print(f"\n✅ FOUND {len(recommendations)} RECOMMENDATIONS:")
            print("-" * 50)
            
            for i, rec in enumerate(recommendations[:10], 1):
                print(f"{i:2d}. {rec['make']} {rec['model']} {rec['year']} ({rec['variant']})")
                print(f"    💰 {rec['price']:,} PKR | 🔧 {rec['engine_capacity']}cc | ⚙️ {rec['transmission']}")
                print(f"    📈 Match Score: {rec['match_score']:.2f}")
                print()
                
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def compare_variants(self):
        """Compare different variants of the same car."""
        print("\n🔧 VARIANT COMPARISON TEST")
        print("-" * 30)
        
        try:
            # Get base car info
            make = input("Enter car make (e.g., Toyota): ").strip()
            model = input("Enter car model (e.g., Corolla): ").strip()
            year = int(input("Enter year (e.g., 2020): "))
            engine_capacity = float(input("Enter engine capacity in cc (e.g., 1300): "))
            transmission = input("Enter transmission (manual/automatic): ").strip().lower()
            
            # Get variants for the specific car
            if HAS_VARIANT_MAPPING:
                variants = get_car_variants(make, model)
                car_info = get_car_info(make, model)
                print(f"\n✅ Found {len(variants)} variants for {make} {model}")
                print(f"📋 Description: {car_info['description']}")
                print(f"🔧 Available variants: {', '.join(variants)}")
            else:
                # Fallback to predefined mappings
                car_variants = {
                    'toyota': {
                        'corolla': ['xli', 'gli', 'altis', 'grande', 'se'],
                        'vitz': ['f', 'u', 'jewela'],
                        'prius': ['standard', 'alpha', 'g'],
                        'camry': ['up-spec', 'hybrid', 'grande'],
                        'hilux': ['single cabin', 'double cabin', 'extra cabin']
                    },
                    'honda': {
                        'civic': ['vti', 'vti oriel', 'rs', 'type r'],
                        'city': ['aspire', 'aspire prosmatec', 'ivtec', 'cvt'],
                        'accord': ['cp2', 'cp3', 'executive'],
                        'crv': ['i-vtec', 'exec'],
                        'brv': ['i-vtec', 'cvt']
                    },
                    'suzuki': {
                        'alto': ['vx', 'vxr', 'vxl'],
                        'wagon r': ['vx', 'vxr', 'vxl'],
                        'swift': ['dxg', 'dlx', 'automatic'],
                        'cultus': ['vx', 'vxr', 'vxl', 'ags']
                    },
                    'hyundai': {
                        'elantra': ['gls', 'active'],
                        'tucson': ['gls', 'ultimate'],
                        'sonata': ['gls', 'limited']
                    },
                    'kia': {
                        'sportage': ['alpha', 'awd'],
                        'picanto': ['automatic', 'manual']
                    }
                }
                
                make_lower = make.lower()
                model_lower = model.lower()
                
                if make_lower in car_variants and model_lower in car_variants[make_lower]:
                    variants = car_variants[make_lower][model_lower]
                    print(f"\n✅ Found {len(variants)} variants for {make} {model}")
                    print(f"🔧 Available variants: {', '.join(variants)}")
                else:
                    # Generic fallback
                    variants = ['gli', 'xli', 'vti', 'vxr', 'aspire', 'unknown']
                    print(f"\n⚠️  Using generic variants for {make} {model}")
                    print(f"🔧 Note: Car-specific variants not available, using: {', '.join(variants)}")
            
            print(f"\n⏳ Comparing variants for {make} {model} {year}...")
            print("-" * 50)
            
            variant_results = {}
            
            for variant in variants:
                try:
                    result = enhanced_api.predict_price_enhanced(
                        make=make,
                        model=model,
                        year=year,
                        engine_capacity=engine_capacity,
                        transmission=transmission,
                        variant=variant
                    )
                    variant_results[variant] = result
                except:
                    continue
            
            # Display comparison
            print(f"{'Variant':<10} {'Price':<12} {'Confidence':<12} {'Popular':<8}")
            print("-" * 45)
            
            for variant, result in variant_results.items():
                features = result['features_used']
                popular = "Yes" if features.get('is_popular_variant', False) else "No"
                
                print(f"{variant.upper():<10} {result['predicted_price']:,<12} {result['confidence']:<12.2f} {popular:<8}")
            
            # Show price differences
            if len(variant_results) > 1:
                prices = [r['predicted_price'] for r in variant_results.values()]
                min_price = min(prices)
                max_price = max(prices)
                
                print(f"\n📊 PRICE ANALYSIS:")
                print(f"   Lowest Price: {min_price:,} PKR")
                print(f"   Highest Price: {max_price:,} PKR")
                print(f"   Price Difference: {max_price - min_price:,} PKR ({((max_price/min_price)-1)*100:.1f}%)")
                
        except ValueError as e:
            print(f"❌ Invalid input: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def market_analysis(self):
        """Show market analysis."""
        print("\n📊 MARKET ANALYSIS")
        print("-" * 30)
        
        # Test popular Pakistani cars
        popular_cars = [
            ('Toyota', 'Corolla', 2020, 1300, 'manual', 'gli'),
            ('Honda', 'Civic', 2020, 1800, 'automatic', 'vti'),
            ('Suzuki', 'Alto', 2021, 660, 'manual', 'vxr'),
            ('Honda', 'City', 2020, 1500, 'automatic', 'aspire'),
            ('Toyota', 'Vitz', 2019, 1000, 'manual', 'f'),
            ('Suzuki', 'Cultus', 2020, 1000, 'manual', 'vxr'),
            ('Toyota', 'Prius', 2018, 1800, 'automatic', 'hybrid'),
            ('Honda', 'Vezel', 2019, 1500, 'automatic', 'hybrid')
        ]
        
        print("🚗 POPULAR PAKISTANI CARS ANALYSIS:")
        print("-" * 50)
        
        results = []
        
        for make, model, year, engine, transmission, variant in popular_cars:
            try:
                result = enhanced_api.predict_price_enhanced(
                    make=make,
                    model=model,
                    year=year,
                    engine_capacity=engine,
                    transmission=transmission,
                    variant=variant
                )
                results.append((f"{make} {model} {variant.upper()}", result['predicted_price']))
            except:
                continue
        
        # Sort by price
        results.sort(key=lambda x: x[1])
        
        print(f"{'Car':<25} {'Price':<15}")
        print("-" * 40)
        
        for car, price in results:
            print(f"{car:<25} {price:,<15}")
        
        # Show price categories
        if results:
            prices = [r[1] for r in results]
            avg_price = sum(prices) / len(prices)
            
            print(f"\n📈 MARKET INSIGHTS:")
            print(f"   Average Price: {avg_price:,.0f} PKR")
            print(f"   Price Range: {min(prices):,} - {max(prices):,} PKR")
            print(f"   Most Affordable: {results[0][0]}")
            print(f"   Most Expensive: {results[-1][0]}")
    
    def quick_test(self):
        """Quick test with predefined popular cars."""
        print("\n⚡ QUICK TEST - POPULAR CARS")
        print("-" * 30)
        
        quick_tests = [
            ("Toyota Corolla GLI 2020", 'Toyota', 'Corolla', 2020, 1300, 'manual', 'gli'),
            ("Honda Civic VTi 2020", 'Honda', 'Civic', 2020, 1800, 'automatic', 'vti'),
            ("Suzuki Alto VXR 2021", 'Suzuki', 'Alto', 2021, 660, 'manual', 'vxr'),
            ("Honda City Aspire 2020", 'Honda', 'City', 2020, 1500, 'automatic', 'aspire'),
            ("Toyota Prius 2018", 'Toyota', 'Prius', 2018, 1800, 'automatic', 'hybrid')
        ]
        
        print("🚗 Running quick tests...")
        print()
        
        for name, make, model, year, engine, transmission, variant in quick_tests:
            try:
                result = enhanced_api.predict_price_enhanced(
                    make=make,
                    model=model,
                    year=year,
                    engine_capacity=engine,
                    transmission=transmission,
                    variant=variant
                )
                
                print(f"✅ {name}")
                print(f"   Price: {result['predicted_price']:,} PKR")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Features: Japanese={result['features_used'].get('is_japanese', False)}, "
                      f"Popular={result['features_used'].get('is_popular_variant', False)}")
                print()
                
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
                print()
    
    def performance_test(self):
        """Test API performance."""
        print("\n⚡ PERFORMANCE TEST")
        print("-" * 30)
        
        import time
        
        # Test multiple predictions
        test_runs = 10
        total_time = 0
        
        print(f"Running {test_runs} predictions...")
        
        for i in range(test_runs):
            start_time = time.time()
            
            try:
                result = enhanced_api.predict_price_enhanced(
                    make='Toyota',
                    model='Corolla',
                    year=2020,
                    engine_capacity=1300,
                    transmission='manual',
                    variant='gli'
                )
                
                end_time = time.time()
                run_time = end_time - start_time
                total_time += run_time
                
                print(f"  Run {i+1}: {run_time:.3f}s")
                
            except Exception as e:
                print(f"  Run {i+1}: Error - {e}")
        
        if total_time > 0:
            avg_time = total_time / test_runs
            print(f"\n📊 PERFORMANCE RESULTS:")
            print(f"   Average Time: {avg_time:.3f}s")
            print(f"   Total Time: {total_time:.3f}s")
            print(f"   Requests/Second: {test_runs/total_time:.1f}")
    
    def run(self):
        """Run the interactive demo."""
        print("🎉 Welcome to Enhanced Features Interactive Demo!")
        
        while self.running:
            self.print_menu()
            
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                
                if choice == '1':
                    self.test_price_prediction()
                elif choice == '2':
                    self.test_recommendations()
                elif choice == '3':
                    self.compare_variants()
                elif choice == '4':
                    self.market_analysis()
                elif choice == '5':
                    self.quick_test()
                elif choice == '6':
                    self.performance_test()
                elif choice == '7':
                    print("\n👋 Thank you for testing Enhanced Features!")
                    self.running = False
                else:
                    print("❌ Invalid choice. Please select 1-7.")
                    
                if self.running:
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.running = False
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")

def main():
    """Main function."""
    demo = InteractiveDemo()
    demo.run()

if __name__ == "__main__":
    main()
