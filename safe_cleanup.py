"""
Selective Project Cleanup Script
===============================

Safely removes unnecessary files while preserving important project structure.
This script only removes temporary, cache, and duplicate files.

Author: Senior DevOps Engineer Agent
Version: 1.0.0
"""

import os
import shutil
import glob
from pathlib import Path

def safe_cleanup():
    """Perform safe cleanup of unnecessary files."""
    print("🧹 STARTING SAFE PROJECT CLEANUP")
    print("=" * 50)
    
    # Safe to remove - temporary and cache files
    safe_to_remove = [
        # Log files in root
        "*.log",
        
        # Cache directories (but not .git)
        "__pycache__",
        ".pytest_cache",
        
        # Temporary files
        "*.tmp",
        "*.temp",
        "*.bak",
        "*.backup",
        
        # Python compiled files
        "*.pyc",
        "*.pyo",
        "*.pyd",
        
        # OS specific files
        ".DS_Store",
        "Thumbs.db",
        "*.swp",
        "*.swo",
        
        # Obviously duplicate files in root
        "*_refactored.py",  # Only in root, keep organized ones
    ]
    
    removed_count = 0
    preserved_count = 0
    
    print("🗑️  Removing safe temporary files...")
    
    for pattern in safe_to_remove:
        if pattern == "*_refactored.py":
            # Only remove refactored files in root, not in organized structure
            root_refactored = glob.glob(pattern)
            for file_path in root_refactored:
                if os.path.isfile(file_path) and not file_path.startswith('src/') and not file_path.startswith('examples/'):
                    try:
                        os.remove(file_path)
                        print(f"   🗑️  Removed: {file_path}")
                        removed_count += 1
                    except Exception as e:
                        print(f"   ❌ Could not remove {file_path}: {e}")
        else:
            matches = glob.glob(pattern, recursive=True)
            for item in matches:
                # Skip .git and virtual environment
                if '.git' in item or '.venv' in item or 'node_modules' in item:
                    preserved_count += 1
                    continue
                    
                try:
                    if os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"   🗑️  Removed directory: {item}")
                    else:
                        os.remove(item)
                        print(f"   🗑️  Removed file: {item}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Could not remove {item}: {e}")
    
    print(f"\n✅ Safe cleanup complete!")
    print(f"   🗑️  Removed: {removed_count} items")
    print(f"   💾 Preserved: {preserved_count} important items")
    
    # Show current project structure
    print(f"\n📁 Current organized structure:")
    important_dirs = ['src', 'tests', 'docs', 'config', 'deployment', 'examples']
    for directory in important_dirs:
        if os.path.exists(directory):
            file_count = len(list(Path(directory).rglob('*')))
            print(f"   ✅ {directory:<12} ({file_count} files)")

def create_gitignore():
    """Create comprehensive .gitignore file."""
    print(f"\n📋 Creating comprehensive .gitignore...")
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/
spider*.log

# Models (large files)
*.pkl
*.joblib
models/*.pkl
models/*.joblib

# Data (sensitive/large)
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Node.js (if using frontend)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Temporary files
*.tmp
*.temp
*.bak
*.backup
*.orig

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Documentation builds
docs/_build/

# Jupyter Notebook
.ipynb_checkpoints

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Package files
*.deb
*.rpm
*.msi
*.exe
*.dmg

# Compressed files
*.zip
*.tar.gz
*.rar

# Project specific
# Add your project specific ignores here
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print("   ✅ Created comprehensive .gitignore")

def main():
    """Main cleanup function."""
    safe_cleanup()
    create_gitignore()
    
    print(f"\n🎉 PROJECT CLEANUP COMPLETE!")
    print("=" * 50)
    print("✅ Temporary files removed")
    print("✅ Cache directories cleaned")
    print("✅ Duplicate files in root removed")
    print("✅ Organized structure preserved")
    print("✅ Comprehensive .gitignore created")
    
    print(f"\n🎯 NEXT STEPS:")
    print("   1. Review the cleaned project structure")
    print("   2. Test functionality: python launch.py api")
    print("   3. Run tests: python launch.py test")
    print("   4. Deploy using: cd deployment/docker && docker-compose up")

if __name__ == "__main__":
    main()
