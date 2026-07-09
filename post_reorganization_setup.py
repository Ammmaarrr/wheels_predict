"""
Import Path Update Script
========================

Updates import paths in moved files to match the new project structure.
"""

import os
import re
from pathlib import Path

def update_imports_in_file(file_path: str):
    """Update import statements in a single file."""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update common import patterns
        updates = [
            # Config imports
            (r'from config\.secure_config import', 'from src.pakwheels_api.config.secure_config import'),
            (r'import config\.secure_config', 'import src.pakwheels_api.config.secure_config'),
            
            # API imports
            (r'from enhanced_api_wrapper import', 'from src.pakwheels_ml.models.enhanced_api_wrapper import'),
            (r'import enhanced_api_wrapper', 'import src.pakwheels_ml.models.enhanced_api_wrapper'),
            
            # Reviewer config
            (r'from reviewer_config import', 'from config.development.reviewer_config import'),
            (r'import reviewer_config', 'import config.development.reviewer_config'),
        ]
        
        for old_pattern, new_pattern in updates:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
    
    return False

def update_all_imports():
    """Update imports in all relevant files."""
    
    print("🔧 Updating import statements...")
    
    # Files to update
    update_patterns = [
        'src/**/*.py',
        'tests/**/*.py',
        'examples/**/*.py'
    ]
    
    updated_files = []
    
    for pattern in update_patterns:
        for file_path in Path('.').glob(pattern):
            if file_path.is_file():
                if update_imports_in_file(str(file_path)):
                    updated_files.append(str(file_path))
                    print(f"   Updated: {file_path}")
    
    print(f"\n✅ Updated imports in {len(updated_files)} files")
    return updated_files

def create_modern_launcher():
    """Create a modern launcher script for the reorganized project."""
    
    launcher_content = '''#!/usr/bin/env python3
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
        from pakwheels_api.api.enhanced_fastapi_server_updated import app
        import uvicorn
        
        print("🚀 Starting PakWheels API Server...")
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
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
        print("  api      - Launch FastAPI server")
        print("  mvp      - Launch MVP server")
        print("  test     - Run test suite") 
        print("  structure - Show project structure")
        return
    
    command = sys.argv[1].lower()
    
    if command == "api":
        launch_api()
    elif command == "mvp":
        launch_mvp()
    elif command == "test":
        run_tests()
    elif command == "structure":
        show_structure()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
'''
    
    with open('launch.py', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print("🚀 Created modern launcher: launch.py")

def create_development_env():
    """Create development environment template."""
    
    env_content = '''# PakWheels Platform - Development Environment
# =============================================

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pakwheelsdb
DB_USER=postgres
DB_PASSWORD=your_password_here

# Security
SECRET_KEY=your_secret_key_here_min_32_chars

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
'''
    
    env_path = 'config/development/.env.template'
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"📝 Created environment template: {env_path}")

if __name__ == "__main__":
    print("🔧 POST-REORGANIZATION SETUP")
    print("=" * 30)
    
    # Update imports
    updated_files = update_all_imports()
    
    # Create modern launcher
    create_modern_launcher()
    
    # Create environment template
    create_development_env()
    
    print("\n✅ POST-REORGANIZATION COMPLETE!")
    print("=" * 30)
    print("🎯 Quick Start:")
    print("   1. Copy config/development/.env.template to .env")
    print("   2. Fill in your database credentials")
    print("   3. Run: python launch.py api")
    print("   4. Visit: http://localhost:8000/docs")
