"""
Project Structure Reorganization Script
======================================

This script reorganizes the pakwheels project into a clean, professional structure
following Python best practices and modern project organization standards.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

def create_new_structure():
    """Create the new project folder structure."""
    
    structure = {
        # Source code
        'src/pakwheels_api': [
            '__init__.py',
            'api/',
            'models/',
            'services/',
            'utils/',
            'config/'
        ],
        
        # Data and ML components
        'src/pakwheels_ml': [
            '__init__.py',
            'models/',
            'training/',
            'preprocessing/',
            'evaluation/'
        ],
        
        # Web scraping components
        'src/pakwheels_scraper': [
            '__init__.py',
            'spiders/',
            'pipelines/',
            'items/',
            'settings/'
        ],
        
        # Tests
        'tests': [
            '__init__.py',
            'unit/',
            'integration/', 
            'api/',
            'fixtures/'
        ],
        
        # Documentation
        'docs': [
            'api/',
            'setup/',
            'examples/',
            'architecture/'
        ],
        
        # Configuration
        'config': [
            'development/',
            'production/',
            'testing/'
        ],
        
        # Deployment
        'deployment': [
            'docker/',
            'kubernetes/',
            'scripts/'
        ],
        
        # Data directories
        'data': [
            'raw/',
            'processed/',
            'models/',
            'exports/'
        ],
        
        # Scripts and utilities
        'scripts': [
            'setup/',
            'maintenance/',
            'migration/'
        ],
        
        # Examples and demos
        'examples': [
            'basic_usage/',
            'advanced/',
            'notebooks/'
        ]
    }
    
    return structure

def get_file_mappings():
    """Define how existing files should be mapped to new structure."""
    
    mappings = {
        # API files
        'enhanced_fastapi_server*.py': 'src/pakwheels_api/api/',
        'mvp_fastapi_server.py': 'src/pakwheels_api/api/',
        'simple_*.py': 'src/pakwheels_api/api/',
        'api.py': 'src/pakwheels_api/api/',
        
        # ML and models
        'enhanced_api_wrapper*.py': 'src/pakwheels_ml/models/',
        'enhanced_model_updater.py': 'src/pakwheels_ml/training/',
        'run_enhanced_processing.py': 'src/pakwheels_ml/training/',
        
        # Configuration
        'config/': 'config/',
        'reviewer_config.py': 'config/development/',
        
        # Tests
        'test_*.py': 'tests/unit/',
        'step_*_test*.py': 'tests/integration/',
        'individual_tests.py': 'tests/integration/',
        'debug_test.py': 'tests/unit/',
        
        # Demo and examples
        'demo_*.py': 'examples/basic_usage/',
        'demonstrate_*.py': 'examples/advanced/',
        'analyze_*.py': 'examples/advanced/',
        'interactive_demo.py': 'examples/basic_usage/',
        
        # Documentation
        '*.md': 'docs/',
        'HOW_TO_RUN.md': 'docs/setup/',
        'README.md': './',  # Keep at root
        
        # Deployment
        'Dockerfile*': 'deployment/docker/',
        'docker-compose*.yml': 'deployment/docker/',
        'docker-entrypoint.sh': 'deployment/docker/',
        '*.bat': 'scripts/setup/',
        '*.sh': 'scripts/setup/',
        
        # Requirements
        'requirements*.txt': 'config/',
        'pyproject.toml': './',  # Keep at root
        
        # Logs
        '*.log': 'data/logs/',
        
        # Scrapy project
        'scrapers/': 'src/pakwheels_scraper/',
    }
    
    return mappings

def create_init_files():
    """Create proper __init__.py files with package information."""
    
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
    }
    
    return init_files

def create_readme_files():
    """Create README files for major directories."""
    
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
'''
    }
    
    return readmes

def print_migration_plan():
    """Print the migration plan for user review."""
    
    print("🏗️  PROJECT REORGANIZATION PLAN")
    print("=" * 50)
    print()
    
    structure = create_new_structure()
    mappings = get_file_mappings()
    
    print("📁 NEW FOLDER STRUCTURE:")
    print("-" * 30)
    for folder, subfolders in structure.items():
        print(f"📂 {folder}/")
        for subfolder in subfolders:
            if subfolder.endswith('/'):
                print(f"   📂 {subfolder}")
            else:
                print(f"   📄 {subfolder}")
        print()
    
    print("📋 FILE MAPPINGS:")
    print("-" * 30)
    for pattern, destination in mappings.items():
        print(f"   {pattern} → {destination}")
    
    print("\n✅ BENEFITS:")
    print("-" * 30)
    benefits = [
        "🎯 Clear separation of concerns",
        "📦 Proper Python package structure", 
        "🧪 Organized test suite",
        "📚 Comprehensive documentation",
        "🚀 Production-ready deployment setup",
        "🔧 Easy maintenance and scaling",
        "👥 Better team collaboration",
        "📈 Professional project appearance"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")

if __name__ == "__main__":
    print_migration_plan()
