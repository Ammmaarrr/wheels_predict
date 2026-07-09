#!/usr/bin/env python3
"""
Test Launcher - Quick access to all testing functionality
"""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def print_banner():
    """Print banner"""
    print("=" * 80)
    print("🧪 PAKWHEELS COMPREHENSIVE TESTING SUITE")
    print("🤖 With AI Agent Integration for Automatic Issue Resolution")
    print("=" * 80)

def print_menu():
    """Print testing menu"""
    print("\n📋 Available Testing Options:")
    print("1. 🎯 Master Test Orchestrator (Full AI-powered testing)")
    print("2. 📋 Comprehensive System Tests")
    print("3. 🌐 API Endpoint Testing")
    print("4. 📊 Database & ML Testing")
    print("5. 🔍 Quick Health Check")
    print("0. ❌ Exit")

def run_master_orchestrator():
    """Run the master test orchestrator"""
    print("\n🎯 Starting Master Test Orchestrator...")
    print("This will run comprehensive testing with AI-powered issue resolution.")
    print("Expected duration: 10-20 minutes")
    
    confirm = input("\nContinue? (y/N): ").lower().strip()
    if confirm == 'y':
        subprocess.run([sys.executable, "tests/master_test_orchestrator.py"], cwd=PROJECT_ROOT)
    else:
        print("❌ Cancelled.")

def run_comprehensive_tests():
    """Run comprehensive system tests"""
    print("\n📋 Starting Comprehensive System Tests...")
    subprocess.run([sys.executable, "tests/comprehensive_tester.py"], cwd=PROJECT_ROOT)

def run_api_tests():
    """Run API tests"""
    print("\n🌐 Starting API Endpoint Tests...")
    subprocess.run([sys.executable, "tests/api_tester.py"], cwd=PROJECT_ROOT)

def run_database_ml_tests():
    """Run database and ML tests"""
    print("\n📊 Starting Database & ML Tests...")
    subprocess.run([sys.executable, "tests/database_ml_tester.py"], cwd=PROJECT_ROOT)

def run_quick_health_check():
    """Run quick health check"""
    print("\n🔍 Running Quick Health Check...")
    
    try:
        # Test basic imports
        print("🔄 Testing imports...")
        import launch
        print("✅ Launch module: OK")
        
        try:
            import src.pakwheels_api
            print("✅ API package: OK")
        except ImportError as e:
            print(f"❌ API package: {e}")
        
        try:
            import src.pakwheels_ml
            print("✅ ML package: OK")
        except ImportError as e:
            print(f"❌ ML package: {e}")
        
        try:
            import src.pakwheels_scraper
            print("✅ Scraper package: OK")
        except ImportError as e:
            print(f"❌ Scraper package: {e}")
        
        # Test file structure
        print("\n🔄 Testing file structure...")
        required_dirs = ["src", "tests", "config", "docs"]
        for dir_name in required_dirs:
            dir_path = PROJECT_ROOT / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name}/: OK")
            else:
                print(f"❌ {dir_name}/: Missing")
        
        # Test launcher
        print("\n🔄 Testing launcher...")
        result = subprocess.run([sys.executable, "launch.py", "structure"], 
                              capture_output=True, text=True, cwd=PROJECT_ROOT)
        if result.returncode == 0:
            print("✅ Launcher: OK")
        else:
            print(f"❌ Launcher: {result.stderr}")
        
        print("\n✅ Quick health check complete!")
        
    except Exception as e:
        print(f"\n❌ Health check failed: {str(e)}")

def main():
    """Main menu function"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("\n🎯 Select option (0-5): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                run_master_orchestrator()
            elif choice == "2":
                run_comprehensive_tests()
            elif choice == "3":
                run_api_tests()
            elif choice == "4":
                run_database_ml_tests()
            elif choice == "5":
                run_quick_health_check()
            else:
                print("❌ Invalid choice. Please select 0-5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Testing cancelled. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        # Pause before showing menu again
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
