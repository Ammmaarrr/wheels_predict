#!/usr/bin/env python3
"""
PakWheels Platform Launcher
==========================

Modern launcher for the reorganized PakWheels platform.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def launch_api():
    """Launch the FastAPI server."""
    try:
        # Try the enhanced server first
        from pakwheels_api.api.enhanced_fastapi_server_updated import app
        import uvicorn
        
        print("🚀 Starting PakWheels API Server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except ImportError as e:
        print(f"❌ Enhanced API import error: {e}")
        print("🔄 Falling back to simple working API...")
        
        try:
            from simple_working_api import app
            import uvicorn
            
            print("🚀 Starting Simple PakWheels API Server...")
            uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
            
        except Exception as e2:
            print(f"❌ Fallback API error: {e2}")
            print("Make sure all dependencies are installed:")
            print("pip install -r config/requirements.txt")

def launch_mvp():
    """Launch the MVP server."""
    try:
        from pakwheels_api.api.mvp_fastapi_server import app
        import uvicorn
        
        print("🚀 Starting PakWheels MVP Server...")
        uvicorn.run(app, host="0.0.0.0", port=5000, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r config/requirements.txt")

def run_tests():
    """Run the test suite."""
    import subprocess
    
    print("🧪 Running test suite...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])

def run_comprehensive_tests():
    """Run comprehensive testing with AI integration."""
    import subprocess
    
    print("🧪 Starting comprehensive testing with AI integration...")
    subprocess.run([sys.executable, "run_tests.py"], cwd=Path(__file__).parent)

def run_master_testing():
    """Run master test orchestrator."""
    import subprocess
    
    print("🎯 Starting Master Test Orchestrator...")
    subprocess.run([sys.executable, "tests/master_test_orchestrator.py"], cwd=Path(__file__).parent)

def run_api_tests():
    """Run API endpoint tests."""
    import subprocess
    
    print("🌐 Starting API endpoint tests...")
    subprocess.run([sys.executable, "tests/api_tester.py"], cwd=Path(__file__).parent)

def show_structure():
    """Show the project structure."""
    
    print("📁 PakWheels Platform Structure:")
    print("=" * 40)
    
    structure = {
        "src/": "📦 Source Code",
        "├── pakwheels_api/": "🌐 REST API",
        "├── pakwheels_ml/": "🤖 Machine Learning",
        "└── pakwheels_scraper/": "🕷️ Web Scraping",
        "tests/": "🧪 Test Suite",
        "docs/": "📚 Documentation", 
        "config/": "⚙️ Configuration",
        "deployment/": "🚀 Deployment",
        "examples/": "💡 Examples & Demos"
    }
    
    for path, desc in structure.items():
        print(f"{desc:<20} {path}")

def main():
    """Main launcher function."""
    
    if len(sys.argv) < 2:
        print("🏗️ PakWheels Platform Launcher")
        print("=" * 30)
        print("Usage: python launch.py [command]")
        print()
        print("Commands:")
        print("  api         - Launch FastAPI server")
        print("  mvp         - Launch MVP server")
        print("  test        - Run basic test suite") 
        print("  test-all    - Run comprehensive testing")
        print("  test-master - Run master test orchestrator with AI")
        print("  test-api    - Run API endpoint tests")
        print("  structure   - Show project structure")
        return
    
    command = sys.argv[1].lower()
    
    if command == "api":
        launch_api()
    elif command == "mvp":
        launch_mvp()
    elif command == "test":
        run_tests()
    elif command == "test-all":
        run_comprehensive_tests()
    elif command == "test-master":
        run_master_testing()
    elif command == "test-api":
        run_api_tests()
    elif command == "structure":
        show_structure()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
