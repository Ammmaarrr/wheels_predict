#!/usr/bin/env python3
"""
PakWheels Testing Suite Launcher
Comprehensive testing tools for the PakWheels project
"""

import sys
import subprocess
from pathlib import Path

def show_menu():
    """Display testing options menu"""
    print("=" * 60)
    print("🧪 PAKWHEELS TESTING SUITE")
    print("=" * 60)
    print("Choose a testing option:")
    print()
    print("1. ⚡ Quick Test - Basic functionality check")
    print("2. 🔍 Comprehensive Test - All APIs and features")
    print("3. 🚀 Advanced API Test - Detailed API testing")
    print("4. 🤖 Automated Test & Fix - Continuous testing with auto-fixes")
    print("5. 📊 Project Status Report - Current project state")
    print("6. 🌐 Start API Server - Launch the API server")
    print("7. 📖 View Test Logs - Show recent test logs")
    print("0. ❌ Exit")
    print()

def run_quick_test():
    """Run quick basic test"""
    print("\n🚀 Running Quick Test...")
    subprocess.run([sys.executable, "simple_comprehensive_tester.py"])

def run_comprehensive_test():
    """Run comprehensive test suite"""
    print("\n🔍 Running Comprehensive Test...")
    # Try the main comprehensive tester if it exists, fallback to simple
    if Path("comprehensive_tester.py").exists():
        subprocess.run([sys.executable, "comprehensive_tester.py"])
    else:
        subprocess.run([sys.executable, "simple_comprehensive_tester.py"])

def run_advanced_api_test():
    """Run advanced API testing"""
    print("\n🚀 Running Advanced API Test...")
    subprocess.run([sys.executable, "advanced_api_tester.py"])

def run_automated_test_fix():
    """Run automated testing with fixes"""
    print("\n🤖 Running Automated Test & Fix...")
    subprocess.run([sys.executable, "automated_tester_fixer.py"])

def show_project_status():
    """Show current project status"""
    print("\n📊 Showing Project Status...")
    subprocess.run([sys.executable, "final_project_status.py"])

def start_api_server():
    """Start the API server"""
    print("\n🌐 Starting API Server...")
    print("The server will start in the background.")
    print("Visit http://localhost:8000/docs to see the API documentation.")
    print("Press Ctrl+C to stop the server.")
    subprocess.run([sys.executable, "simple_working_api.py"])

def view_test_logs():
    """View recent test logs"""
    print("\n📖 Recent Test Logs:")
    
    log_dir = Path("D:/pakwheels_test_logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("*.txt"))
        if log_files:
            # Get the most recent log file
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"\nShowing latest log: {latest_log.name}")
            print("-" * 60)
            
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Show last 20 lines
                    for line in lines[-20:]:
                        print(line.rstrip())
            except Exception as e:
                print(f"Error reading log file: {e}")
        else:
            print("No log files found.")
    else:
        print("Log directory not found.")
    
    # Also check for JSON reports
    temp_dir = Path("D:/temp")
    if temp_dir.exists():
        json_files = list(temp_dir.glob("*test_report*.json"))
        if json_files:
            latest_report = max(json_files, key=lambda x: x.stat().st_mtime)
            print(f"\nLatest test report: {latest_report.name}")

def main():
    """Main menu loop"""
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (0-7): ").strip()
            
            if choice == "0":
                print("\n👋 Goodbye!")
                break
            elif choice == "1":
                run_quick_test()
            elif choice == "2":
                run_comprehensive_test()
            elif choice == "3":
                run_advanced_api_test()
            elif choice == "4":
                run_automated_test_fix()
            elif choice == "5":
                show_project_status()
            elif choice == "6":
                start_api_server()
            elif choice == "7":
                view_test_logs()
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            if choice != "0":
                input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
