#!/usr/bin/env python3
"""
Advanced API Endpoint Tester
Tests all API endpoints extensively with various scenarios
"""

import requests
import json
import time
import subprocess
import sys
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class APITestResult:
    endpoint: str
    method: str
    status_code: int
    response_time: float
    passed: bool
    error: Optional[str] = None
    response_data: Optional[Dict] = None

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.server_process = None
        self.test_results: List[APITestResult] = []
        
    def start_api_server(self):
        """Start the API server for testing"""
        print("🚀 Starting API server...")
        try:
            self.server_process = subprocess.Popen(
                [sys.executable, "launch.py", "api"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            print("⏳ Waiting for server to start...")
            time.sleep(8)
            
            # Check if server is running
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    def stop_api_server(self):
        """Stop the API server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 API server stopped")

    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, 
                     params: Dict = None, expected_status: int = 200) -> APITestResult:
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, params=params, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, params=params, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response_time = time.time() - start_time
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500]}
            
            passed = response.status_code == expected_status
            error = None if passed else f"Expected {expected_status}, got {response.status_code}"
            
            return APITestResult(
                endpoint=endpoint,
                method=method,
                status_code=response.status_code,
                response_time=response_time,
                passed=passed,
                error=error,
                response_data=response_data
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return APITestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                passed=False,
                error=str(e)
            )

    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic Endpoints...")
        
        basic_tests = [
            ("/", "GET", 200),
            ("/docs", "GET", 200),
            ("/openapi.json", "GET", 200),
            ("/health", "GET", 200),
            ("/api/v1/health", "GET", 200),
        ]
        
        for endpoint, method, expected_status in basic_tests:
            result = self.test_endpoint(endpoint, method, expected_status=expected_status)
            self.test_results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
            
            if not result.passed:
                print(f"     Error: {result.error}")

    def test_prediction_endpoints(self):
        """Test ML prediction endpoints"""
        print("\n🤖 Testing Prediction Endpoints...")
        
        # Test data for car prediction
        test_car_data = {
            "make": "Toyota",
            "model": "Corolla",
            "year": 2020,
            "mileage": 50000,
            "transmission": "Manual",
            "fuel_type": "Petrol",
            "engine_size": "1.3L"
        }
        
        prediction_tests = [
            ("/api/v1/predict", "POST", test_car_data, 200),
            ("/api/v1/predict/price", "POST", test_car_data, 200),
            ("/api/v1/recommendations", "POST", test_car_data, 200),
            ("/api/v1/similar-cars", "POST", test_car_data, 200),
        ]
        
        for endpoint, method, data, expected_status in prediction_tests:
            result = self.test_endpoint(endpoint, method, data=data, expected_status=expected_status)
            self.test_results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
            
            if not result.passed:
                print(f"     Error: {result.error}")
            elif result.response_data:
                print(f"     Response keys: {list(result.response_data.keys())}")

    def test_data_endpoints(self):
        """Test data-related endpoints"""
        print("\n📊 Testing Data Endpoints...")
        
        data_tests = [
            ("/api/v1/cars", "GET", 200),
            ("/api/v1/cars/brands", "GET", 200),
            ("/api/v1/cars/models", "GET", 200),
            ("/api/v1/cars/years", "GET", 200),
            ("/api/v1/statistics", "GET", 200),
            ("/api/v1/market-insights", "GET", 200),
        ]
        
        for endpoint, method, expected_status in data_tests:
            result = self.test_endpoint(endpoint, method, expected_status=expected_status)
            self.test_results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
            
            if not result.passed:
                print(f"     Error: {result.error}")

    def test_upload_endpoints(self):
        """Test file upload endpoints"""
        print("\n📁 Testing Upload Endpoints...")
        
        # Create sample CSV data
        sample_data = pd.DataFrame({
            'make': ['Toyota', 'Honda'],
            'model': ['Corolla', 'Civic'],
            'year': [2020, 2021],
            'price': [1500000, 1800000]
        })
        
        csv_content = sample_data.to_csv(index=False)
        
        upload_tests = [
            ("/api/v1/upload/csv", "POST", {"csv_data": csv_content}, 200),
            ("/api/v1/upload/bulk", "POST", {"data": sample_data.to_dict('records')}, 200),
        ]
        
        for endpoint, method, data, expected_status in upload_tests:
            result = self.test_endpoint(endpoint, method, data=data, expected_status=expected_status)
            self.test_results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
            
            if not result.passed:
                print(f"     Error: {result.error}")

    def test_error_handling(self):
        """Test error handling with invalid data"""
        print("\n⚠️ Testing Error Handling...")
        
        error_tests = [
            ("/api/v1/predict", "POST", {"invalid": "data"}, 422),  # Validation error
            ("/api/v1/nonexistent", "GET", None, 404),  # Not found
            ("/api/v1/predict", "GET", None, 405),  # Method not allowed
        ]
        
        for endpoint, method, data, expected_status in error_tests:
            result = self.test_endpoint(endpoint, method, data=data, expected_status=expected_status)
            self.test_results.append(result)
            
            status_icon = "✅" if result.passed else "❌"
            print(f"  {status_icon} {method} {endpoint} - {result.status_code} ({result.response_time:.3f}s)")
            
            if not result.passed:
                print(f"     Error: {result.error}")

    def test_performance(self):
        """Test API performance with concurrent requests"""
        print("\n⚡ Testing Performance...")
        
        def concurrent_request():
            return self.test_endpoint("/", "GET")
        
        # Test concurrent requests
        import concurrent.futures
        
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(concurrent_request) for _ in range(20)]
            results = [future.result() for future in futures]
        
        total_time = time.time() - start_time
        successful_requests = len([r for r in results if r.passed])
        
        print(f"  📊 Concurrent Requests: 20")
        print(f"  ✅ Successful: {successful_requests}")
        print(f"  ⏱️ Total Time: {total_time:.3f}s")
        print(f"  📈 Requests/sec: {20/total_time:.2f}")

    def run_comprehensive_api_tests(self):
        """Run all API tests"""
        print("🧪 COMPREHENSIVE API TESTING")
        print("=" * 50)
        
        if not self.start_api_server():
            print("❌ Cannot start API server, aborting tests")
            return False
        
        try:
            # Run all test suites
            self.test_basic_endpoints()
            self.test_prediction_endpoints()
            self.test_data_endpoints()
            self.test_upload_endpoints()
            self.test_error_handling()
            self.test_performance()
            
            # Generate summary
            self.generate_api_test_report()
            
        finally:
            self.stop_api_server()
        
        return True

    def generate_api_test_report(self):
        """Generate comprehensive API test report"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.passed])
        
        avg_response_time = sum(r.response_time for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        report = f"""
# 🧪 COMPREHENSIVE API TEST REPORT

## 📊 Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed_tests}
- **Failed**: {total_tests - passed_tests}
- **Success Rate**: {(passed_tests/total_tests*100):.1f}%
- **Average Response Time**: {avg_response_time:.3f}s

## 📋 Detailed Results

"""
        
        # Group results by endpoint category
        categories = {
            "Basic Endpoints": ["/", "/docs", "/openapi.json", "/health"],
            "Prediction APIs": ["/predict", "/recommendations", "/similar-cars"],
            "Data APIs": ["/cars", "/brands", "/models", "/statistics"],
            "Upload APIs": ["/upload"],
            "Error Handling": ["/nonexistent", "invalid"]
        }
        
        for category, keywords in categories.items():
            report += f"### {category}\n\n"
            category_results = [
                r for r in self.test_results 
                if any(keyword in r.endpoint for keyword in keywords)
            ]
            
            if category_results:
                for result in category_results:
                    status_icon = "✅" if result.passed else "❌"
                    report += f"- {status_icon} **{result.method} {result.endpoint}**\n"
                    report += f"  - Status: {result.status_code}\n"
                    report += f"  - Response Time: {result.response_time:.3f}s\n"
                    if result.error:
                        report += f"  - Error: {result.error}\n"
                    report += "\n"
            else:
                report += "No tests in this category\n\n"
        
        # Save report
        with open("API_TEST_REPORT.md", 'w') as f:
            f.write(report)
        
        print(f"\n📄 API test report saved to API_TEST_REPORT.md")
        
        # Print summary
        print(f"\n📊 API Testing Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")

def main():
    """Main function for API testing"""
    tester = APITester()
    tester.run_comprehensive_api_tests()

if __name__ == "__main__":
    main()
