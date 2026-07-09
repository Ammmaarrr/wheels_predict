#!/usr/bin/env python3
"""
Advanced API Endpoint Tester
Tests all API endpoints with various scenarios and edge cases
"""

import requests
import json
import time
import threading
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import concurrent.futures

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@dataclass
class APITestCase:
    """API test case structure"""
    name: str
    endpoint: str
    method: str
    payload: Optional[Dict] = None
    headers: Optional[Dict] = None
    expected_status: int = 200
    timeout: int = 10
    description: str = ""

class APITester:
    """Comprehensive API testing class"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.server_process = None
        
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def start_api_server(self) -> bool:
        """Start the API server for testing"""
        try:
            self.log("🚀 Starting API server...")
            self.server_process = subprocess.Popen(
                [sys.executable, "launch.py", "api"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=PROJECT_ROOT
            )
            
            # Wait for server to start
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    response = requests.get(f"{self.base_url}/docs", timeout=2)
                    if response.status_code == 200:
                        self.log("✅ API server started successfully")
                        return True
                except requests.RequestException:
                    pass
                
                time.sleep(2)
                self.log(f"⏳ Waiting for server... (attempt {attempt + 1}/{max_attempts})")
            
            self.log("❌ Failed to start API server")
            return False
            
        except Exception as e:
            self.log(f"❌ Error starting server: {str(e)}")
            return False
    
    def stop_api_server(self):
        """Stop the API server"""
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                self.log("🛑 API server stopped")
            except:
                self.server_process.kill()
                self.log("🔪 API server killed")
    
    def discover_endpoints(self) -> List[str]:
        """Discover API endpoints from OpenAPI spec"""
        try:
            response = self.session.get(f"{self.base_url}/openapi.json", timeout=10)
            if response.status_code == 200:
                openapi_spec = response.json()
                endpoints = list(openapi_spec.get("paths", {}).keys())
                self.log(f"📍 Discovered {len(endpoints)} endpoints")
                return endpoints
            else:
                self.log("⚠️ Could not fetch OpenAPI spec, using default endpoints")
                return ["/", "/docs", "/health", "/openapi.json"]
        except Exception as e:
            self.log(f"⚠️ Error discovering endpoints: {str(e)}")
            return ["/", "/docs", "/health", "/openapi.json"]
    
    def create_test_cases(self) -> List[APITestCase]:
        """Create comprehensive test cases"""
        endpoints = self.discover_endpoints()
        test_cases = []
        
        # Basic connectivity tests
        basic_tests = [
            APITestCase("root_endpoint", "/", "GET", description="Root endpoint accessibility"),
            APITestCase("docs_endpoint", "/docs", "GET", description="API documentation"),
            APITestCase("openapi_spec", "/openapi.json", "GET", description="OpenAPI specification"),
            APITestCase("health_check", "/health", "GET", description="Health check endpoint"),
        ]
        test_cases.extend(basic_tests)
        
        # Test each discovered endpoint
        for endpoint in endpoints:
            if endpoint not in ["/", "/docs", "/openapi.json", "/health"]:
                # GET request test
                test_cases.append(APITestCase(
                    f"get_{endpoint.replace('/', '_').strip('_')}", 
                    endpoint, 
                    "GET",
                    description=f"GET request to {endpoint}"
                ))
                
                # POST request test (if it makes sense)
                if any(keyword in endpoint.lower() for keyword in ["predict", "upload", "submit", "create"]):
                    test_cases.append(APITestCase(
                        f"post_{endpoint.replace('/', '_').strip('_')}", 
                        endpoint, 
                        "POST",
                        payload={"test": "data"},
                        headers={"Content-Type": "application/json"},
                        expected_status=200,  # May vary
                        description=f"POST request to {endpoint}"
                    ))
        
        # Edge case tests
        edge_cases = [
            APITestCase("invalid_endpoint", "/nonexistent", "GET", expected_status=404, 
                       description="Invalid endpoint handling"),
            APITestCase("invalid_method", "/docs", "DELETE", expected_status=405, 
                       description="Invalid method handling"),
            APITestCase("malformed_json", "/", "POST", 
                       payload="invalid json", expected_status=400,
                       description="Malformed JSON handling"),
        ]
        test_cases.extend(edge_cases)
        
        # Performance tests
        performance_tests = [
            APITestCase("concurrent_requests", "/", "GET", description="Concurrent request handling"),
            APITestCase("large_payload", "/", "POST", 
                       payload={"large_data": "x" * 10000}, 
                       description="Large payload handling"),
        ]
        test_cases.extend(performance_tests)
        
        return test_cases
    
    def run_single_test(self, test_case: APITestCase) -> Dict[str, Any]:
        """Run a single API test case"""
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{test_case.endpoint}"
            
            # Prepare request
            kwargs = {
                "timeout": test_case.timeout,
                "headers": test_case.headers or {}
            }
            
            if test_case.payload:
                if test_case.headers and test_case.headers.get("Content-Type") == "application/json":
                    kwargs["json"] = test_case.payload
                else:
                    kwargs["data"] = test_case.payload
            
            # Make request
            response = self.session.request(test_case.method, url, **kwargs)
            
            duration = time.time() - start_time
            
            # Analyze response
            success = response.status_code == test_case.expected_status
            
            result = {
                "name": test_case.name,
                "status": "PASS" if success else "FAIL",
                "description": test_case.description,
                "method": test_case.method,
                "endpoint": test_case.endpoint,
                "expected_status": test_case.expected_status,
                "actual_status": response.status_code,
                "duration": duration,
                "response_size": len(response.content),
                "success": success
            }
            
            # Additional checks
            if success:
                result["details"] = {
                    "content_type": response.headers.get("content-type", ""),
                    "has_content": len(response.content) > 0,
                    "response_time_ms": round(duration * 1000, 2)
                }
            else:
                result["error"] = f"Expected {test_case.expected_status}, got {response.status_code}"
                result["response_text"] = response.text[:500]
            
            return result
            
        except requests.RequestException as e:
            duration = time.time() - start_time
            return {
                "name": test_case.name,
                "status": "ERROR",
                "description": test_case.description,
                "method": test_case.method,
                "endpoint": test_case.endpoint,
                "error": str(e),
                "duration": duration,
                "success": False
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                "name": test_case.name,
                "status": "ERROR",
                "description": test_case.description,
                "error": f"Unexpected error: {str(e)}",
                "duration": duration,
                "success": False
            }
    
    def run_concurrent_test(self, test_case: APITestCase, num_concurrent: int = 5) -> Dict[str, Any]:
        """Run concurrent requests to test performance"""
        if test_case.name != "concurrent_requests":
            return self.run_single_test(test_case)
        
        self.log(f"🔀 Running {num_concurrent} concurrent requests...")
        
        start_time = time.time()
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            # Create multiple test cases
            concurrent_cases = [
                APITestCase(f"concurrent_{i}", "/", "GET", description=f"Concurrent request {i}")
                for i in range(num_concurrent)
            ]
            
            # Submit all requests
            futures = [executor.submit(self.run_single_test, case) for case in concurrent_cases]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e), "success": False})
        
        total_duration = time.time() - start_time
        successful = sum(1 for r in results if r.get("success", False))
        
        return {
            "name": "concurrent_requests",
            "status": "PASS" if successful == num_concurrent else "FAIL",
            "description": f"Concurrent request handling ({num_concurrent} requests)",
            "total_duration": total_duration,
            "successful_requests": successful,
            "total_requests": num_concurrent,
            "success_rate": successful / num_concurrent * 100,
            "avg_response_time": sum(r.get("duration", 0) for r in results) / len(results),
            "success": successful == num_concurrent
        }
    
    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all API tests"""
        self.log("🧪 Creating test cases...")
        test_cases = self.create_test_cases()
        self.log(f"📋 Created {len(test_cases)} test cases")
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            self.log(f"🔍 Running test {i}/{len(test_cases)}: {test_case.name}")
            
            if test_case.name == "concurrent_requests":
                result = self.run_concurrent_test(test_case)
            else:
                result = self.run_single_test(test_case)
            
            results.append(result)
            
            # Log result
            emoji = "✅" if result["success"] else "❌"
            status_info = f"({result.get('actual_status', 'N/A')})" if 'actual_status' in result else ""
            self.log(f"{emoji} {test_case.name} {status_info}")
            
            # Brief pause between tests
            time.sleep(0.5)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate comprehensive test report"""
        total_tests = len(results)
        passed = sum(1 for r in results if r.get("success", False))
        failed = total_tests - passed
        
        avg_duration = sum(r.get("duration", 0) for r in results) / total_tests if total_tests > 0 else 0
        
        report = f"""# 🌐 API TESTING REPORT

**Generated:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Base URL:** {self.base_url}

## 📊 Summary
- **Total Tests:** {total_tests}
- **Passed:** {passed} ✅
- **Failed:** {failed} ❌
- **Success Rate:** {(passed/total_tests*100):.1f}%
- **Average Response Time:** {avg_duration*1000:.2f}ms

## 🔍 Detailed Results

"""
        
        for result in results:
            emoji = "✅" if result.get("success", False) else "❌"
            report += f"\n### {emoji} {result['name']}\n"
            report += f"**Description:** {result.get('description', 'N/A')}\n"
            report += f"**Status:** {result.get('status', 'UNKNOWN')}\n"
            
            if 'method' in result and 'endpoint' in result:
                report += f"**Request:** {result['method']} {result['endpoint']}\n"
            
            if 'expected_status' in result and 'actual_status' in result:
                report += f"**Status Code:** {result['actual_status']} (expected {result['expected_status']})\n"
            
            if 'duration' in result:
                report += f"**Response Time:** {result['duration']*1000:.2f}ms\n"
            
            if 'error' in result:
                report += f"**Error:** {result['error']}\n"
            
            if 'details' in result:
                details = result['details']
                report += f"**Details:**\n"
                for key, value in details.items():
                    report += f"  - {key}: {value}\n"
        
        report += f"""
## 🎯 Performance Metrics
- **Fastest Response:** {min(r.get('duration', float('inf')) for r in results)*1000:.2f}ms
- **Slowest Response:** {max(r.get('duration', 0) for r in results)*1000:.2f}ms
- **Total Test Duration:** {sum(r.get('duration', 0) for r in results):.2f}s

## 📋 Recommendations
"""
        
        if failed > 0:
            report += "- ❌ Fix failing endpoints before production deployment\n"
        if avg_duration > 1:
            report += "- ⚡ Consider optimizing response times\n"
        if passed/total_tests > 0.9:
            report += "- ✅ API is ready for production use\n"
        
        # Save report
        report_path = PROJECT_ROOT / "API_TEST_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        
        self.log(f"📋 API test report saved to: {report_path}")
        return report_path

def main():
    """Main function to run API testing"""
    print("=" * 60)
    print("🌐 COMPREHENSIVE API ENDPOINT TESTER")
    print("=" * 60)
    
    tester = APITester()
    
    try:
        # Start server
        if not tester.start_api_server():
            print("❌ Failed to start API server. Exiting.")
            return
        
        # Run tests
        print("\n🧪 Running comprehensive API tests...")
        results = tester.run_all_tests()
        
        # Generate report
        print("\n📋 Generating test report...")
        report_path = tester.generate_report(results)
        
        # Summary
        passed = sum(1 for r in results if r.get("success", False))
        total = len(results)
        
        print(f"\n✨ API Testing Complete!")
        print(f"📊 Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
        print(f"📋 Full report: {report_path}")
        
    finally:
        # Stop server
        tester.stop_api_server()

if __name__ == "__main__":
    main()
