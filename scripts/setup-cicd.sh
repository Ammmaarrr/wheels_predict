#!/bin/bash

# CI/CD Setup Script
# This script helps set up the local development environment for CI/CD

set -e

echo "🚀 Setting up CI/CD environment..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p .github/workflows
mkdir -p logs
mkdir -p data/raw
mkdir -p data/cleaned
mkdir -p models

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install --upgrade pip
pip install -r config/requirements.txt
pip install -r tests/requirements_test.txt

# Set up pre-commit hooks (optional)
echo "🔧 Setting up pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  pre-commit not found, skipping hooks setup"
    echo "   Install with: pip install pre-commit"
fi

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file (please configure it)"
else
    echo "✅ .env file already exists"
fi

# Run initial code quality checks
echo "🔍 Running initial code quality checks..."
echo "  - Formatting check..."
black --check . || echo "⚠️  Code formatting issues found. Run 'black .' to fix."

echo "  - Import sorting check..."
isort --check-only . || echo "⚠️  Import sorting issues found. Run 'isort .' to fix."

echo "  - Linting check..."
flake8 . || echo "⚠️  Linting issues found."

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short || echo "⚠️  Some tests failed."

echo ""
echo "✅ CI/CD setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Configure your .env file"
echo "   2. Set up GitHub repository secrets"
echo "   3. Push to GitHub to trigger CI/CD pipeline"
echo "   4. Review and customize workflows in .github/workflows/"
echo ""
echo "🔧 Useful commands:"
echo "   - Format code: black ."
echo "   - Sort imports: isort ."
echo "   - Run linting: flake8 ."
echo "   - Run tests: pytest tests/ -v"
echo "   - Run security scan: bandit -r ."
echo ""
