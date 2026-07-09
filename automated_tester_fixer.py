#!/usr/bin/env python3
"""
Automated Testing and Issue Resolution System
Continuously tests the PakWheels project and automatically fixes issues
Uses AI agent API for intelligent issue resolution
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Use D: drive for all operations
D_TEMP = Path("D:/temp")
D_LOGS = Path("D:/pakwheels_test_logs")
D_TEMP.mkdir(exist_ok=True)
D_LOGS.mkdir(exist_ok=True)

class AutomatedTesterAndFixer:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.ai_api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.ai_api_key = os.getenv("OPENROUTER_API_KEY", "")
        
        self.test_iteration = 1
        self.max_iterations = 5
        self.issues_log = []
        self.fixes_applied = []
        self.test_results = []
        
        # Initialize session
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Save to log file
        log_file = D_LOGS / f"automated_test_log_{datetime.now().strftime('%Y%m%d')}.txt"
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception:
            pass  # Continue if logging fails
    
    def call_ai_agent(self, issue_description: str, context: str = "") -> Optional[str]:
        """Call AI agent for issue resolution"""
        if not self.ai_api_key:
            self.log("No AI API key available, skipping AI assistance", "WARNING")
            return None
            
        try:
            headers = {
                "Authorization": f"Bearer {self.ai_api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""
            You are a senior software engineer fixing issues in a PakWheels car prediction API project.
            
            ISSUE: {issue_description}
            
            CONTEXT: {context}
            
            Please provide:
            1. Root cause analysis
            2. Specific fix instructions
            3. Code changes if needed
            4. Prevention measures
            
            Be concise and actionable.
            """
            
            data = {
                "model": "anthropic/claude-3.5-sonnet",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1500
            }
            
            response = requests.post(self.ai_api_url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                self.log(f"AI API error: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Error calling AI agent: {e}", "ERROR")
            return None
    
    def test_api_health(self) -> bool:
        """Test if API is healthy"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def test_api_prediction(self) -> bool:
        """Test API prediction functionality"""
        try:
            test_data = {
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2020,
                "mileage": 50000
            }
            
            response = self.session.post(f"{self.api_url}/predict", json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                price = result.get('predicted_price', 0)
                confidence = result.get('confidence', 0)
                
                # Validate reasonable values
                return 100000 <= price <= 10000000 and 0 <= confidence <= 1
            
            return False
            
        except Exception:
            return False
    
    def test_data_endpoints(self) -> Dict[str, bool]:
        """Test data retrieval endpoints"""
        endpoints = {
            "/cars": False,
            "/brands": False,
            "/stats": False
        }
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.api_url}{endpoint}", timeout=10)
                endpoints[endpoint] = response.status_code == 200
            except Exception:
                endpoints[endpoint] = False
        
        return endpoints
    
    def test_import_system(self) -> Dict[str, bool]:
        """Test critical imports"""
        import_tests = {
            "pandas": False,
            "numpy": False,
            "fastapi": False,
            "requests": False
        }
        
        for module in import_tests:
            try:
                __import__(module)
                import_tests[module] = True
            except ImportError:
                import_tests[module] = False
        
        return import_tests
    
    def test_file_structure(self) -> Dict[str, bool]:
        """Test file structure integrity"""
        structure_tests = {
            "launch.py": Path("launch.py").exists(),
            "src": Path("src").exists(),
            "pakwheels_api": Path("src/pakwheels_api").exists(),
            "pakwheels_ml": Path("src/pakwheels_ml").exists(),
            "pakwheels_scraper": Path("src/pakwheels_scraper").exists()
        }
        
        return structure_tests
    
    def run_comprehensive_test_cycle(self) -> Dict[str, Any]:
        """Run a complete test cycle"""
        self.log(f"=== RUNNING TEST CYCLE {self.test_iteration} ===")
        
        results = {
            "iteration": self.test_iteration,
            "timestamp": datetime.now().isoformat(),
            "api_health": False,
            "api_prediction": False,
            "data_endpoints": {},
            "import_system": {},
            "file_structure": {},
            "issues_found": [],
            "fixes_attempted": []
        }
        
        # Test API health
        self.log("Testing API health...")
        results["api_health"] = self.test_api_health()
        if not results["api_health"]:
            issue = "API server not responding"
            results["issues_found"].append(issue)
            self.issues_log.append(issue)
            fix_attempted = self.attempt_api_fix()
            if fix_attempted:
                results["fixes_attempted"].append(fix_attempted)
        
        # Test API prediction
        if results["api_health"]:
            self.log("Testing API prediction...")
            results["api_prediction"] = self.test_api_prediction()
            if not results["api_prediction"]:
                issue = "API prediction not working properly"
                results["issues_found"].append(issue)
                self.issues_log.append(issue)
        
        # Test data endpoints
        self.log("Testing data endpoints...")
        results["data_endpoints"] = self.test_data_endpoints()
        for endpoint, status in results["data_endpoints"].items():
            if not status:
                issue = f"Data endpoint {endpoint} not working"
                results["issues_found"].append(issue)
                self.issues_log.append(issue)
        
        # Test import system
        self.log("Testing import system...")
        results["import_system"] = self.test_import_system()
        for module, status in results["import_system"].items():
            if not status:
                issue = f"Module {module} not importable"
                results["issues_found"].append(issue)
                self.issues_log.append(issue)
                fix_attempted = self.attempt_import_fix(module)
                if fix_attempted:
                    results["fixes_attempted"].append(fix_attempted)
        
        # Test file structure
        self.log("Testing file structure...")
        results["file_structure"] = self.test_file_structure()
        for item, status in results["file_structure"].items():
            if not status:
                issue = f"Missing file/directory: {item}"
                results["issues_found"].append(issue)
                self.issues_log.append(issue)
        
        # Log results
        total_issues = len(results["issues_found"])
        if total_issues == 0:
            self.log("✅ ALL TESTS PASSED!", "SUCCESS")
        else:
            self.log(f"❌ {total_issues} issues found", "WARNING")
            for issue in results["issues_found"]:
                self.log(f"  - {issue}", "WARNING")
        
        self.test_results.append(results)
        return results
    
    def attempt_api_fix(self) -> Optional[str]:
        """Attempt to fix API issues"""
        self.log("Attempting to fix API issues...")
        
        try:
            # Try to start the API server
            self.log("Trying to start API server...")
            
            # First, check if there's already a process running
            try:
                response = requests.get(f"{self.api_url}/health", timeout=2)
                if response.status_code == 200:
                    self.log("API server is already running")
                    return "API server was already running"
            except:
                pass
            
            # Try to start with our simple working API
            cmd = [sys.executable, "simple_working_api.py"]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Test if it's working now
            if self.test_api_health():
                self.log("✅ API server started successfully")
                fix = "Started API server using simple_working_api.py"
                self.fixes_applied.append(fix)
                return fix
            else:
                self.log("❌ API server still not responding")
                
                # Get AI assistance
                ai_suggestion = self.call_ai_agent(
                    "API server not starting properly",
                    f"Tried to start with: {' '.join(cmd)}"
                )
                
                if ai_suggestion:
                    self.log(f"AI Suggestion: {ai_suggestion}")
                    return f"AI suggested: {ai_suggestion[:100]}..."
                
        except Exception as e:
            self.log(f"Error attempting API fix: {e}", "ERROR")
        
        return None
    
    def attempt_import_fix(self, module_name: str) -> Optional[str]:
        """Attempt to fix import issues"""
        self.log(f"Attempting to fix import issue for {module_name}...")
        
        try:
            # Try to install the module
            cache_dir = D_TEMP / "pip_cache"
            target_dir = D_TEMP / "packages"
            cache_dir.mkdir(exist_ok=True)
            target_dir.mkdir(exist_ok=True)
            
            cmd = [
                sys.executable, "-m", "pip", "install", module_name,
                "--cache-dir", str(cache_dir),
                "--target", str(target_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                # Add to Python path
                sys.path.insert(0, str(target_dir))
                
                # Test import again
                try:
                    __import__(module_name)
                    fix = f"Installed {module_name} to D: drive"
                    self.log(f"✅ {fix}")
                    self.fixes_applied.append(fix)
                    return fix
                except ImportError:
                    self.log(f"❌ {module_name} still not importable after installation")
            else:
                self.log(f"❌ Failed to install {module_name}: {result.stderr}")
                
                # Get AI assistance
                ai_suggestion = self.call_ai_agent(
                    f"Cannot import module {module_name}",
                    f"Installation error: {result.stderr}"
                )
                
                if ai_suggestion:
                    self.log(f"AI Suggestion: {ai_suggestion}")
                    return f"AI suggested: {ai_suggestion[:100]}..."
                
        except Exception as e:
            self.log(f"Error attempting import fix for {module_name}: {e}", "ERROR")
        
        return None
    
    def run_automated_testing(self):
        """Run automated testing with issue resolution"""
        self.log("🚀 STARTING AUTOMATED TESTING AND ISSUE RESOLUTION")
        self.log("=" * 60)
        
        start_time = time.time()
        
        while self.test_iteration <= self.max_iterations:
            # Run test cycle
            cycle_results = self.run_comprehensive_test_cycle()
            
            # Check if all tests passed
            if not cycle_results["issues_found"]:
                self.log("🎉 ALL TESTS PASSED! No more issues to fix.")
                break
            
            # If this is the last iteration, don't try to fix
            if self.test_iteration >= self.max_iterations:
                self.log("⚠️ Maximum iterations reached")
                break
            
            # Wait before next iteration
            self.log(f"Waiting 5 seconds before next iteration...")
            time.sleep(5)
            
            self.test_iteration += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate final report
        self.generate_final_report(total_time)
    
    def generate_final_report(self, total_time: float):
        """Generate final testing report"""
        self.log("\n" + "=" * 60)
        self.log("AUTOMATED TESTING FINAL REPORT")
        self.log("=" * 60)
        
        self.log(f"Total testing time: {total_time:.2f} seconds")
        self.log(f"Test iterations completed: {self.test_iteration}")
        self.log(f"Total issues found: {len(self.issues_log)}")
        self.log(f"Total fixes applied: {len(self.fixes_applied)}")
        
        # Get final test status
        if self.test_results:
            final_results = self.test_results[-1]
            
            self.log("\nFINAL TEST STATUS:")
            self.log(f"  API Health: {'✅' if final_results['api_health'] else '❌'}")
            self.log(f"  API Prediction: {'✅' if final_results['api_prediction'] else '❌'}")
            
            # Data endpoints status
            data_status = all(final_results["data_endpoints"].values())
            self.log(f"  Data Endpoints: {'✅' if data_status else '❌'}")
            
            # Import system status
            import_status = all(final_results["import_system"].values())
            self.log(f"  Import System: {'✅' if import_status else '❌'}")
            
            # File structure status
            structure_status = all(final_results["file_structure"].values())
            self.log(f"  File Structure: {'✅' if structure_status else '❌'}")
        
        # Issues summary
        if self.issues_log:
            self.log(f"\nISSUES ENCOUNTERED:")
            unique_issues = list(set(self.issues_log))
            for i, issue in enumerate(unique_issues, 1):
                count = self.issues_log.count(issue)
                self.log(f"{i}. {issue} (occurred {count} times)")
        
        # Fixes summary
        if self.fixes_applied:
            self.log(f"\nFIXES APPLIED:")
            for i, fix in enumerate(self.fixes_applied, 1):
                self.log(f"{i}. {fix}")
        
        # Save detailed report
        try:
            report_file = D_LOGS / f"automated_test_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "total_time_seconds": total_time,
                "iterations_completed": self.test_iteration,
                "total_issues": len(self.issues_log),
                "total_fixes": len(self.fixes_applied),
                "issues_log": self.issues_log,
                "fixes_applied": self.fixes_applied,
                "test_results": self.test_results,
                "final_status": {
                    "all_tests_passed": not self.test_results[-1]["issues_found"] if self.test_results else False,
                    "api_functional": self.test_results[-1]["api_health"] if self.test_results else False
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.log(f"\nDetailed report saved to: {report_file}")
            
        except Exception as e:
            self.log(f"Could not save detailed report: {e}", "ERROR")
        
        # Final verdict
        if self.test_results and not self.test_results[-1]["issues_found"]:
            self.log("\n🎉 SUCCESS: All issues resolved!")
            self.log("✅ PakWheels project is fully functional!")
        elif len(self.fixes_applied) > 0:
            self.log(f"\n✅ PARTIAL SUCCESS: Applied {len(self.fixes_applied)} fixes")
            self.log("⚠️ Some issues may remain")
        else:
            self.log("\n❌ ATTENTION NEEDED: Issues found but no fixes applied")
            self.log("🔧 Manual intervention may be required")

def main():
    """Main function"""
    print("🤖 Automated PakWheels Testing and Issue Resolution System")
    print("Using D: drive for all operations")
    print("This will continuously test and fix issues until everything works\n")
    
    tester = AutomatedTesterAndFixer()
    tester.run_automated_testing()

if __name__ == "__main__":
    main()
