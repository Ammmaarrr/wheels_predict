#!/usr/bin/env python3
"""
Simple but Comprehensive PakWheels Tester
Uses D: drive for all operations to avoid space issues
Focuses on critical functionality testing
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime

# Configure to use D: drive for all temporary operations
os.environ['TMPDIR'] = 'D:/temp'
os.environ['TEMP'] = 'D:/temp'
os.environ['TMP'] = 'D:/temp'

# Create temp directories on D: drive
D_TEMP = Path("D:/temp")
D_TEMP.mkdir(exist_ok=True)

class SimpleTester:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.issues = []
        self.fixes = []
        
    def log(self, message):
        """Simple logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_basic_imports(self):
        """Test basic imports"""
        self.log("Testing basic imports...")
        
        basic_imports = [
            "sys", "os", "json", "time", "requests", 
            "pathlib", "subprocess"
        ]
        
        for module in basic_imports:
            try:
                __import__(module)
                self.log(f"✓ {module} - OK")
            except ImportError as e:
                self.log(f"✗ {module} - FAILED: {e}")
                self.issues.append(f"Import {module}: {e}")
    
    def test_project_structure(self):
        """Test project structure"""
        self.log("Testing project structure...")
        
        required_paths = [
            "launch.py",
            "src",
            "src/pakwheels_api", 
            "src/pakwheels_ml",
            "src/pakwheels_scraper"
        ]
        
        for path in required_paths:
            if Path(path).exists():
                self.log(f"✓ {path} - EXISTS")
            else:
                self.log(f"✗ {path} - MISSING")
                self.issues.append(f"Missing: {path}")
    
    def test_python_environment(self):
        """Test Python environment"""
        self.log("Testing Python environment...")
        
        # Check Python version
        version = sys.version_info
        self.log(f"Python version: {version.major}.{version.minor}")
        
        if version.major >= 3 and version.minor >= 8:
            self.log("✓ Python version - OK")
        else:
            self.log("✗ Python version - TOO OLD")
            self.issues.append("Python version too old")
    
    def test_disk_space(self):
        """Test disk space on D: drive"""
        self.log("Testing disk space...")
        
        try:
            import shutil
            total, used, free = shutil.disk_usage("D:")
            free_gb = free // (1024**3)
            self.log(f"Free space on D: drive: {free_gb} GB")
            
            if free_gb > 2:
                self.log("✓ Disk space - OK")
            else:
                self.log("✗ Disk space - LOW")
                self.issues.append(f"Low disk space: {free_gb} GB")
                
        except Exception as e:
            self.log(f"✗ Could not check disk space: {e}")
    
    def test_api_server(self):
        """Test if API server is running"""
        self.log("Testing API server...")
        
        try:
            response = requests.get(f"{self.api_url}/", timeout=5)
            if response.status_code < 400:
                self.log("✓ API server - RUNNING")
            else:
                self.log(f"✗ API server - ERROR {response.status_code}")
                self.issues.append(f"API server error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log("✗ API server - NOT RUNNING")
            self.issues.append("API server not running")
            self.try_start_api_server()
            
        except Exception as e:
            self.log(f"✗ API server - ERROR: {e}")
            self.issues.append(f"API server error: {e}")
    
    def try_start_api_server(self):
        """Try to start the API server"""
        self.log("Attempting to start API server...")
        
        try:
            # Try to start with launch.py
            cmd = [sys.executable, "launch.py", "api"]
            self.log(f"Running: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # Wait a bit for server to start
            time.sleep(3)
            
            # Check if it's running now
            try:
                response = requests.get(f"{self.api_url}/", timeout=5)
                if response.status_code < 400:
                    self.log("✓ API server started successfully")
                    self.fixes.append("Started API server")
                else:
                    self.log("✗ API server still not responding")
            except:
                self.log("✗ API server still not running")
                
        except Exception as e:
            self.log(f"✗ Could not start API server: {e}")
    
    def test_simple_prediction(self):
        """Test simple prediction functionality"""
        self.log("Testing prediction functionality...")
        
        sample_data = {
            "brand": "Toyota",
            "model": "Corolla",
            "year": 2020,
            "mileage": 50000
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/predict",
                json=sample_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✓ Prediction - SUCCESS: {result}")
            else:
                self.log(f"✗ Prediction - FAILED: {response.status_code}")
                self.issues.append(f"Prediction failed: {response.status_code}")
                
        except Exception as e:
            self.log(f"✗ Prediction - ERROR: {e}")
            self.issues.append(f"Prediction error: {e}")
    
    def test_file_permissions(self):
        """Test file permissions and write access"""
        self.log("Testing file permissions...")
        
        test_file = D_TEMP / "test_write.txt"
        
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            
            test_file.unlink()
            self.log("✓ File permissions - OK")
            
        except Exception as e:
            self.log(f"✗ File permissions - ERROR: {e}")
            self.issues.append(f"File permission error: {e}")
    
    def test_package_imports(self):
        """Test importing key packages"""
        self.log("Testing package imports...")
        
        packages = [
            "pandas",
            "numpy", 
            "fastapi",
            "uvicorn",
            "requests",
            "pathlib"
        ]
        
        for package in packages:
            try:
                __import__(package)
                self.log(f"✓ {package} - OK")
            except ImportError:
                self.log(f"✗ {package} - MISSING")
                self.issues.append(f"Missing package: {package}")
                self.try_install_package(package)
    
    def try_install_package(self, package):
        """Try to install missing package to D: drive"""
        self.log(f"Trying to install {package}...")
        
        try:
            # Install to D: drive
            target_dir = D_TEMP / "packages"
            target_dir.mkdir(exist_ok=True)
            
            cmd = [
                sys.executable, "-m", "pip", "install", package,
                "--target", str(target_dir),
                "--cache-dir", str(D_TEMP / "pip_cache")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log(f"✓ Installed {package} to D: drive")
                self.fixes.append(f"Installed {package}")
                
                # Add to Python path
                sys.path.insert(0, str(target_dir))
                
            else:
                self.log(f"✗ Failed to install {package}: {result.stderr}")
                
        except Exception as e:
            self.log(f"✗ Install error for {package}: {e}")
    
    def run_comprehensive_test(self):
        """Run all tests"""
        self.log("=" * 50)
        self.log("STARTING COMPREHENSIVE PAKWHEELS TESTING")
        self.log(f"Using D: drive for temporary operations")
        self.log("=" * 50)
        
        # Run all test categories
        test_methods = [
            self.test_python_environment,
            self.test_disk_space,
            self.test_file_permissions,
            self.test_basic_imports,
            self.test_package_imports,
            self.test_project_structure,
            self.test_api_server,
            self.test_simple_prediction
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log(f"✗ Test failed: {test_method.__name__} - {e}")
                self.issues.append(f"Test {test_method.__name__}: {e}")
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        self.log("\n" + "=" * 50)
        self.log("TEST SUMMARY")
        self.log("=" * 50)
        
        self.log(f"Issues found: {len(self.issues)}")
        self.log(f"Fixes applied: {len(self.fixes)}")
        
        if self.issues:
            self.log("\nISSUES:")
            for i, issue in enumerate(self.issues, 1):
                self.log(f"{i}. {issue}")
        
        if self.fixes:
            self.log("\nFIXES APPLIED:")
            for i, fix in enumerate(self.fixes, 1):
                self.log(f"{i}. {fix}")
        
        # Save report to D: drive
        try:
            report_file = D_TEMP / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "issues": self.issues,
                "fixes": self.fixes,
                "summary": {
                    "total_issues": len(self.issues),
                    "total_fixes": len(self.fixes),
                    "status": "PASSED" if not self.issues else "NEEDS_ATTENTION"
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"\nReport saved to: {report_file}")
            
        except Exception as e:
            self.log(f"Could not save report: {e}")
        
        if not self.issues:
            self.log("\n🎉 ALL TESTS PASSED!")
        else:
            self.log(f"\n⚠️  {len(self.issues)} issues need attention")

def main():
    """Main function"""
    tester = SimpleTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
