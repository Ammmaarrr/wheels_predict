"""
Project Reorganization Implementation
====================================

This script actually performs the reorganization of the pakwheels project.
"""

import os
import shutil
from pathlib import Path
import glob

def create_directory_structure():
    """Create the new directory structure."""
    
    directories = [
        # Source code
        'src/pakwheels_api/api',
        'src/pakwheels_api/models', 
        'src/pakwheels_api/services',
        'src/pakwheels_api/utils',
        'src/pakwheels_api/config',
        
        # ML components
        'src/pakwheels_ml/models',
        'src/pakwheels_ml/training',
        'src/pakwheels_ml/preprocessing',
        'src/pakwheels_ml/evaluation',
        
        # Scraper components  
        'src/pakwheels_scraper/spiders',
        'src/pakwheels_scraper/pipelines',
        'src/pakwheels_scraper/items',
        'src/pakwheels_scraper/settings',
        
        # Tests
        'tests/unit',
        'tests/integration',
        'tests/api',
        'tests/fixtures',
        
        # Documentation
        'docs/api',
        'docs/setup',
        'docs/examples',
        'docs/architecture',
        
        # Configuration
        'config/development',
        'config/production', 
        'config/testing',
        
        # Deployment
        'deployment/docker',
        'deployment/kubernetes',
        'deployment/scripts',
        
        # Data
        'data/raw',
        'data/processed',
        'data/models',
        'data/exports',
        'data/logs',
        
        # Scripts
        'scripts/setup',
        'scripts/maintenance', 
        'scripts/migration',
        
        # Examples
        'examples/basic_usage',
        'examples/advanced',
        'examples/notebooks'
    ]
    
    print("📁 Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")

def move_files():
    """Move files to their new locations."""
    
    # File mappings with glob patterns
    file_moves = [
        # API files
        ('enhanced_fastapi_server*.py', 'src/pakwheels_api/api/'),
        ('mvp_fastapi_server.py', 'src/pakwheels_api/api/'),
        ('simple_fastapi*.py', 'src/pakwheels_api/api/'),
        ('simple_api.py', 'src/pakwheels_api/api/'),
        ('api.py', 'src/pakwheels_api/api/'),
        
        # ML files
        ('enhanced_api_wrapper*.py', 'src/pakwheels_ml/models/'),
        ('enhanced_model_updater.py', 'src/pakwheels_ml/training/'),
        ('run_enhanced_processing.py', 'src/pakwheels_ml/training/'),
        
        # Test files
        ('test_*.py', 'tests/unit/'),
        ('step_*_test*.py', 'tests/integration/'),
        ('individual_tests.py', 'tests/integration/'),
        ('debug_test.py', 'tests/unit/'),
        
        # Demo files
        ('demo_*.py', 'examples/basic_usage/'),
        ('*_demo*.py', 'examples/basic_usage/'),
        ('demonstrate_*.py', 'examples/advanced/'),
        ('analyze_*.py', 'examples/advanced/'),
        ('show_*.py', 'examples/advanced/'),
        
        # Configuration
        ('reviewer_config.py', 'config/development/'),
        ('requirements*.txt', 'config/'),
        
        # Documentation (except README.md at root)
        ('*.md', 'docs/'),
        
        # Deployment
        ('Dockerfile*', 'deployment/docker/'),
        ('docker-compose*.yml', 'deployment/docker/'),
        ('docker-entrypoint.sh', 'deployment/docker/'),
        
        # Scripts
        ('*.bat', 'scripts/setup/'),
        ('launch_*.sh', 'scripts/setup/'),
        
        # Logs
        ('*.log', 'data/logs/'),
        
        # Project summary files
        ('project_*.py', 'examples/advanced/'),
    ]
    
    print("\n📦 Moving files...")
    moved_files = []
    
    for pattern, destination in file_moves:
        matches = glob.glob(pattern)
        for file_path in matches:
            if os.path.isfile(file_path):
                filename = os.path.basename(file_path)
                dest_path = os.path.join(destination, filename)
                
                # Special handling for README.md - keep at root
                if filename == 'README.md' and destination == 'docs/':
                    continue
                    
                try:
                    shutil.copy2(file_path, dest_path)
                    moved_files.append((file_path, dest_path))
                    print(f"   Moved: {file_path} → {dest_path}")
                except Exception as e:
                    print(f"   ❌ Error moving {file_path}: {e}")
    
    return moved_files

def handle_scrapy_project():
    """Handle the scrapy project directory."""
    
    print("\n🕷️  Handling Scrapy project...")
    if os.path.exists('scrapers'):
        try:
            # Copy scrapy project to new location
            if os.path.exists('scrapers/pakwheels'):
                shutil.copytree('scrapers/pakwheels', 'src/pakwheels_scraper/scrapy_project', dirs_exist_ok=True)
                print("   Copied: scrapers/pakwheels → src/pakwheels_scraper/scrapy_project")
        except Exception as e:
            print(f"   ❌ Error handling scrapy project: {e}")

def create_init_files():
    """Create __init__.py files."""
    
    init_files = {
        'src/__init__.py': '"""PakWheels Data Analysis Platform"""',
        
        'src/pakwheels_api/__init__.py': '''"""
PakWheels API Package
====================

FastAPI-based REST API for car price predictions and market insights.
"""

__version__ = "1.0.0"
__author__ = "PakWheels Team"
''',
        
        'src/pakwheels_ml/__init__.py': '''"""
PakWheels ML Package
===================

Machine learning models and training pipelines for car price prediction.
"""

__version__ = "1.0.0"
''',
        
        'src/pakwheels_scraper/__init__.py': '''"""
PakWheels Scraper Package
========================

Scrapy-based web scraping components for PakWheels data collection.
"""

__version__ = "1.0.0"
''',
        
        'tests/__init__.py': '"""Test suite for PakWheels platform"""',
        'tests/unit/__init__.py': '"""Unit tests"""',
        'tests/integration/__init__.py': '"""Integration tests"""',
        'tests/api/__init__.py': '"""API tests"""',
    }
    
    print("\n📄 Creating __init__.py files...")
    for file_path, content in init_files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   Created: {file_path}")

def create_readme_files():
    """Create README files for directories."""
    
    readmes = {
        'src/README.md': '''# Source Code

This directory contains the main source code for the PakWheels platform.

## Structure

- `pakwheels_api/` - FastAPI REST API
- `pakwheels_ml/` - Machine learning components  
- `pakwheels_scraper/` - Web scraping components
''',
        
        'tests/README.md': '''# Tests

Comprehensive test suite for the PakWheels platform.

## Structure

- `unit/` - Unit tests
- `integration/` - Integration tests
- `api/` - API endpoint tests
- `fixtures/` - Test data and fixtures

## Running Tests

```bash
pytest tests/
```
''',
        
        'docs/README.md': '''# Documentation

Documentation for the PakWheels platform.

## Structure

- `api/` - API documentation
- `setup/` - Setup and installation guides
- `examples/` - Usage examples
- `architecture/` - System architecture documentation
''',
        
        'deployment/README.md': '''# Deployment

Deployment configurations and scripts.

## Structure

- `docker/` - Docker configurations
- `kubernetes/` - Kubernetes manifests (if applicable)
- `scripts/` - Deployment scripts

## Quick Start

```bash
# Build and run with Docker
cd docker/
docker-compose up -d
```
''',
        
        'config/README.md': '''# Configuration

Configuration files for different environments.

## Structure

- `development/` - Development environment config
- `production/` - Production environment config
- `testing/` - Testing environment config

## Environment Files

Create `.env` files in each environment directory with required variables.
''',
        
        'examples/README.md': '''# Examples

Usage examples and demonstrations.

## Structure

- `basic_usage/` - Simple usage examples
- `advanced/` - Advanced features and analysis
- `notebooks/` - Jupyter notebooks (if any)

## Running Examples

```bash
python examples/basic_usage/demo_enhanced_variants.py
```
'''
    }
    
    print("\n📚 Creating README files...")
    for file_path, content in readmes.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   Created: {file_path}")

def create_main_setup_files():
    """Create main setup files at root level."""
    
    # Update pyproject.toml with new structure
    pyproject_content = '''[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[project]
name = "pakwheels-platform"
version = "1.0.0"
description = "PakWheels Car Price Prediction and Market Analysis Platform"
authors = [{name = "PakWheels Team"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

dependencies = [
    "fastapi>=0.68.0",
    "uvicorn>=0.15.0",
    "pandas>=1.3.0",
    "numpy>=1.21.0",
    "scikit-learn>=1.0.0",
    "joblib>=1.0.0",
    "python-dotenv>=0.19.0",
    "psycopg2-binary>=2.9.0",
    "scrapy>=2.5.0",
    "requests>=2.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "pytest-cov>=2.12",
    "black>=21.0",
    "flake8>=3.9",
    "mypy>=0.910",
]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"

[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
    
    print("\n⚙️  Creating setup files...")
    
    # Write pyproject.toml
    with open('pyproject.toml', 'w', encoding='utf-8') as f:
        f.write(pyproject_content)
    print("   Updated: pyproject.toml")
    
    # Create .gitignore if it doesn't exist
    gitignore_content = '''# Python
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

# Data
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep

# Logs
*.log
logs/

# Models
*.pkl
*.joblib
models/*.pkl
models/*.joblib

# OS
.DS_Store
Thumbs.db
'''
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        print("   Created: .gitignore")

def create_gitkeep_files():
    """Create .gitkeep files in empty directories."""
    
    empty_dirs = [
        'data/raw',
        'data/processed', 
        'data/models',
        'data/exports',
        'tests/fixtures',
        'docs/api',
        'docs/architecture',
        'examples/notebooks'
    ]
    
    print("\n📌 Creating .gitkeep files...")
    for directory in empty_dirs:
        gitkeep_path = os.path.join(directory, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('')
        print(f"   Created: {gitkeep_path}")

def reorganize_project():
    """Main function to reorganize the project."""
    
    print("🏗️  STARTING PROJECT REORGANIZATION")
    print("=" * 50)
    
    # Create directory structure
    create_directory_structure()
    
    # Move files
    moved_files = move_files()
    
    # Handle scrapy project
    handle_scrapy_project()
    
    # Create init files
    create_init_files()
    
    # Create README files
    create_readme_files()
    
    # Create setup files
    create_main_setup_files()
    
    # Create gitkeep files
    create_gitkeep_files()
    
    print(f"\n✅ REORGANIZATION COMPLETE!")
    print("=" * 50)
    print(f"📊 Summary:")
    print(f"   📁 Directories created: Multiple")
    print(f"   📦 Files moved: {len(moved_files)}")
    print(f"   📄 Documentation created: Multiple README files")
    print(f"   ⚙️  Configuration updated: pyproject.toml")
    
    print(f"\n🎯 Next Steps:")
    print("   1. Review the new structure")
    print("   2. Update import statements in moved files")
    print("   3. Test the reorganized project") 
    print("   4. Remove old files after verification")

if __name__ == "__main__":
    reorganize_project()
