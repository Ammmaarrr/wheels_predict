@echo off
REM CI/CD Setup Script for Windows
REM This script helps set up the local development environment for CI/CD

echo 🚀 Setting up CI/CD environment...

REM Create necessary directories
echo 📁 Creating directories...
if not exist ".github\workflows" mkdir ".github\workflows"
if not exist "logs" mkdir "logs"
if not exist "data\raw" mkdir "data\raw"
if not exist "data\cleaned" mkdir "data\cleaned"
if not exist "models" mkdir "models"

REM Install development dependencies
echo 📦 Installing development dependencies...
pip install --upgrade pip
pip install -r config\requirements.txt
pip install -r tests\requirements_test.txt

REM Create .env from template if it doesn't exist
if not exist ".env" (
    echo 📄 Creating .env file from template...
    copy ".env.example" ".env"
    echo ✅ Created .env file (please configure it)
) else (
    echo ✅ .env file already exists
)

REM Run initial code quality checks
echo 🔍 Running initial code quality checks...
echo   - Formatting check...
black --check . || echo ⚠️  Code formatting issues found. Run 'black .' to fix.

echo   - Import sorting check...
isort --check-only . || echo ⚠️  Import sorting issues found. Run 'isort .' to fix.

echo   - Linting check...
flake8 . || echo ⚠️  Linting issues found.

REM Run tests
echo 🧪 Running tests...
pytest tests\ -v --tb=short || echo ⚠️  Some tests failed.

echo.
echo ✅ CI/CD setup complete!
echo.
echo 📋 Next steps:
echo    1. Configure your .env file
echo    2. Set up GitHub repository secrets
echo    3. Push to GitHub to trigger CI/CD pipeline
echo    4. Review and customize workflows in .github\workflows\
echo.
echo 🔧 Useful commands:
echo    - Format code: black .
echo    - Sort imports: isort .
echo    - Run linting: flake8 .
echo    - Run tests: pytest tests\ -v
echo    - Run security scan: bandit -r .
echo.
pause
