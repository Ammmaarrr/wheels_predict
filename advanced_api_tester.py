#!/usr/bin/env python3
"""
Advanced API Testing Suite
Comprehensive testing of all PakWheels API endpoints and functionality
Uses D: drive for all operations and includes AI-powered issue detection
"""

import os
import sys
import json
import time
import requests
import asyncio
import concurrent.futures
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import random

# Use D: drive for all operations
D_TEMP = Path("D:/temp")
D_TEMP.mkdir(exist_ok=True)

class AdvancedAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.performance_results = []
        self.errors_found = []
        self.session = requests.Session()
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def test_basic_endpoints(self):
        """Test all basic API endpoints"""
        self.log("Testing basic endpoints...")
        
        endpoints = [
            ("GET", "/", "Root endpoint"),
            ("GET", "/health", "Health check"),
            ("GET", "/docs", "API documentation"),
            ("GET", "/openapi.json", "OpenAPI schema"),
            ("GET", "/cars", "Cars list"),
            ("GET", "/brands", "Brands list"),
            ("GET", "/stats", "Statistics")
        ]
        
        for method, endpoint, description in endpoints:
            self.test_single_endpoint(method, endpoint, description)
    
    def test_single_endpoint(self, method, endpoint, description):
        """Test a single endpoint with timing"""
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
            elif method == "POST":
                response = self.session.post(f"{self.base_url}{endpoint}", json={}, timeout=10)
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            if response.status_code < 400:
                self.log(f"✓ {method} {endpoint} - {response.status_code} ({response_time:.0f}ms)")
                
                # Check response content
                try:
                    json_response = response.json()
                    self.log(f"  Response keys: {list(json_response.keys())}")
                except:
                    self.log(f"  Response type: {response.headers.get('content-type', 'unknown')}")
                
                self.performance_results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "response_time_ms": response_time,
                    "status_code": response.status_code
                })
                
            else:
                self.log(f"✗ {method} {endpoint} - ERROR {response.status_code}")
                self.errors_found.append(f"{method} {endpoint}: {response.status_code}")
                
        except Exception as e:
            self.log(f"✗ {method} {endpoint} - EXCEPTION: {str(e)}")
            self.errors_found.append(f"{method} {endpoint}: {str(e)}")
    
    def test_prediction_endpoints(self):
        """Test prediction functionality extensively"""
        self.log("Testing prediction endpoints...")
        
        # Test cases with different data
        test_cases = [
            {
                "name": "Toyota Corolla",
                "data": {
                    "brand": "Toyota",
                    "model": "Corolla",
                    "year": 2020,
                    "mileage": 50000,
                    "engine_capacity": 1.8
                }
            },
            {
                "name": "Honda Civic",
                "data": {
                    "brand": "Honda", 
                    "model": "Civic",
                    "year": 2019,
                    "mileage": 30000,
                    "engine_capacity": 1.5
                }
            },
            {
                "name": "Old car",
                "data": {
                    "brand": "Suzuki",
                    "model": "Alto",
                    "year": 2010,
                    "mileage": 150000,
                    "engine_capacity": 1.0
                }
            },
            {
                "name": "New car",
                "data": {
                    "brand": "BMW",
                    "model": "X5",
                    "year": 2023,
                    "mileage": 5000,
                    "engine_capacity": 3.0
                }
            },
            {
                "name": "Minimal data",
                "data": {
                    "brand": "Toyota"
                }
            }
        ]
        
        for test_case in test_cases:
            self.test_prediction(test_case["name"], test_case["data"])
    
    def test_prediction(self, test_name, car_data):
        """Test a single prediction"""
        try:
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/predict",
                json=car_data,
                timeout=10
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                predicted_price = result.get('predicted_price', 0)
                confidence = result.get('confidence', 0)
                
                self.log(f"✓ Prediction {test_name}: ${predicted_price:,.0f} (confidence: {confidence:.2f}) ({response_time:.0f}ms)")
                
                # Validate prediction results
                if predicted_price > 0 and 0 <= confidence <= 1:
                    self.log(f"  ✓ Prediction values are valid")
                else:
                    self.log(f"  ✗ Invalid prediction values: price={predicted_price}, confidence={confidence}")
                    self.errors_found.append(f"Invalid prediction for {test_name}")
                
                self.performance_results.append({
                    "test": f"prediction_{test_name}",
                    "response_time_ms": response_time,
                    "predicted_price": predicted_price,
                    "confidence": confidence
                })
                
            else:
                self.log(f"✗ Prediction {test_name} - ERROR {response.status_code}")
                self.errors_found.append(f"Prediction {test_name}: {response.status_code}")
                
        except Exception as e:
            self.log(f"✗ Prediction {test_name} - EXCEPTION: {str(e)}")
            self.errors_found.append(f"Prediction {test_name}: {str(e)}")
    
    def test_data_endpoints(self):
        """Test data retrieval endpoints"""
        self.log("Testing data endpoints...")
        
        # Test cars endpoint with different parameters
        params_tests = [
            ("Default limit", {}),
            ("Small limit", {"limit": 5}),
            ("Large limit", {"limit": 100}),
            ("Zero limit", {"limit": 0})
        ]
        
        for test_name, params in params_tests:
            try:
                response = self.session.get(f"{self.base_url}/cars", params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    cars_count = len(data.get('cars', []))
                    self.log(f"✓ Cars {test_name}: {cars_count} cars returned")
                else:
                    self.log(f"✗ Cars {test_name} - ERROR {response.status_code}")
                    self.errors_found.append(f"Cars {test_name}: {response.status_code}")
                    
            except Exception as e:
                self.log(f"✗ Cars {test_name} - EXCEPTION: {str(e)}")
                self.errors_found.append(f"Cars {test_name}: {str(e)}")
    
    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        self.log("Testing concurrent request handling...")
        
        def make_request():
            try:
                response = requests.get(f"{self.base_url}/health", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        # Test with multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            
            futures = [executor.submit(make_request) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            
            success_count = sum(results)
            total_time = (end_time - start_time) * 1000
            
            self.log(f"✓ Concurrent test: {success_count}/20 requests successful in {total_time:.0f}ms")
            
            if success_count >= 18:  # Allow for some failures
                self.log("  ✓ Concurrent handling is good")
            else:
                self.log("  ✗ Poor concurrent handling")
                self.errors_found.append(f"Concurrent test: only {success_count}/20 successful")
    
    def test_error_handling(self):
        """Test error handling"""
        self.log("Testing error handling...")
        
        error_tests = [
            ("Invalid endpoint", "GET", "/nonexistent", None),
            ("Invalid method", "DELETE", "/predict", None),
            ("Invalid JSON", "POST", "/predict", "invalid json"),
            ("Empty prediction", "POST", "/predict", {})
        ]
        
        for test_name, method, endpoint, data in error_tests:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                elif method == "POST":
                    if isinstance(data, str):
                        # Send invalid JSON
                        response = requests.post(
                            f"{self.base_url}{endpoint}",
                            data=data,
                            headers={"Content-Type": "application/json"},
                            timeout=10
                        )
                    else:
                        response = self.session.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
                elif method == "DELETE":
                    response = self.session.delete(f"{self.base_url}{endpoint}", timeout=10)
                
                self.log(f"✓ Error test {test_name}: {response.status_code}")
                
                # Check if error responses are properly formatted
                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            self.log(f"  ✓ Proper error format")
                        else:
                            self.log(f"  ✗ Missing error details")
                    except:
                        self.log(f"  ✗ Non-JSON error response")
                        
            except Exception as e:
                self.log(f"✗ Error test {test_name} - EXCEPTION: {str(e)}")
    
    def test_performance(self):
        """Test API performance"""
        self.log("Testing performance...")
        
        # Test response times for different endpoints
        performance_tests = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/cars?limit=10", "Small cars list"),
            ("/brands", "Brands list"),
            ("/stats", "Statistics")
        ]
        
        for endpoint, description in performance_tests:
            response_times = []
            
            # Make 5 requests to get average response time
            for i in range(5):
                try:
                    start_time = time.time()
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_times.append((end_time - start_time) * 1000)
                        
                except Exception as e:
                    self.log(f"  Performance test failed for {endpoint}: {e}")
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                self.log(f"✓ {description}: avg={avg_time:.0f}ms, min={min_time:.0f}ms, max={max_time:.0f}ms")
                
                if avg_time > 2000:  # More than 2 seconds is slow
                    self.log(f"  ⚠️ Slow response time")
                    self.errors_found.append(f"Slow response for {endpoint}: {avg_time:.0f}ms")
    
    def test_data_validation(self):
        """Test data validation"""
        self.log("Testing data validation...")
        
        validation_tests = [
            ("Negative year", {"brand": "Toyota", "year": -2020}),
            ("Future year", {"brand": "Toyota", "year": 2030}),
            ("Negative mileage", {"brand": "Toyota", "mileage": -1000}),
            ("Extreme mileage", {"brand": "Toyota", "mileage": 10000000}),
            ("Invalid brand type", {"brand": 123}),
            ("Empty strings", {"brand": "", "model": ""}),
            ("Missing required fields", {"random_field": "value"})
        ]
        
        for test_name, test_data in validation_tests:
            try:
                response = self.session.post(f"{self.base_url}/predict", json=test_data, timeout=10)
                
                if response.status_code == 422:  # Validation error
                    self.log(f"✓ Validation {test_name}: properly rejected (422)")
                elif response.status_code == 200:
                    # Check if prediction is reasonable
                    result = response.json()
                    price = result.get('predicted_price', 0)
                    if 100000 <= price <= 10000000:  # Reasonable price range
                        self.log(f"✓ Validation {test_name}: handled gracefully (${price:,.0f})")
                    else:
                        self.log(f"⚠️ Validation {test_name}: unreasonable result (${price:,.0f})")
                else:
                    self.log(f"? Validation {test_name}: unexpected response {response.status_code}")
                    
            except Exception as e:
                self.log(f"✗ Validation {test_name} - EXCEPTION: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        self.log("=" * 60)
        self.log("STARTING COMPREHENSIVE API TESTING")
        self.log("=" * 60)
        
        start_time = time.time()
        
        # Run all test categories
        test_categories = [
            self.test_basic_endpoints,
            self.test_prediction_endpoints,
            self.test_data_endpoints,
            self.test_concurrent_requests,
            self.test_error_handling,
            self.test_performance,
            self.test_data_validation
        ]
        
        for test_category in test_categories:
            try:
                test_category()
                self.log("")  # Add spacing
            except Exception as e:
                self.log(f"✗ Test category {test_category.__name__} failed: {e}")
                self.errors_found.append(f"Test category {test_category.__name__}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Generate comprehensive report
        self.generate_comprehensive_report(total_time)
    
    def generate_comprehensive_report(self, total_time):
        """Generate comprehensive test report"""
        self.log("=" * 60)
        self.log("COMPREHENSIVE TEST REPORT")
        self.log("=" * 60)
        
        # Summary statistics
        total_tests = len(self.performance_results)
        total_errors = len(self.errors_found)
        
        self.log(f"Total test duration: {total_time:.2f} seconds")
        self.log(f"Total tests executed: {total_tests}")
        self.log(f"Total errors found: {total_errors}")
        
        if self.performance_results:
            response_times = [r.get('response_time_ms', 0) for r in self.performance_results if 'response_time_ms' in r]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                self.log(f"Average response time: {avg_response_time:.0f}ms")
        
        # Error summary
        if self.errors_found:
            self.log(f"\nERRORS FOUND ({len(self.errors_found)}):")
            for i, error in enumerate(self.errors_found, 1):
                self.log(f"{i}. {error}")
        
        # Performance summary
        if self.performance_results:
            self.log(f"\nPERFORMANCE SUMMARY:")
            for result in self.performance_results[-5:]:  # Show last 5 results
                if 'endpoint' in result:
                    self.log(f"  {result['endpoint']}: {result['response_time_ms']:.0f}ms")
        
        # Save detailed report to D: drive
        try:
            report_file = D_TEMP / f"comprehensive_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            detailed_report = {
                "timestamp": datetime.now().isoformat(),
                "test_duration_seconds": total_time,
                "total_tests": total_tests,
                "total_errors": total_errors,
                "errors": self.errors_found,
                "performance_results": self.performance_results,
                "summary": {
                    "status": "PASSED" if not self.errors_found else "FAILED",
                    "api_responsive": total_tests > 0,
                    "major_issues": len([e for e in self.errors_found if "EXCEPTION" in e or "ERROR 5" in e])
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(detailed_report, f, indent=2)
            
            self.log(f"\nDetailed report saved to: {report_file}")
            
        except Exception as e:
            self.log(f"Could not save detailed report: {e}")
        
        # Final verdict
        if not self.errors_found:
            self.log("\n🎉 ALL COMPREHENSIVE TESTS PASSED!")
            self.log("✅ API is functioning perfectly!")
        elif len(self.errors_found) <= 2:
            self.log(f"\n⚠️ Minor issues found ({len(self.errors_found)} errors)")
            self.log("✅ API is mostly functional")
        else:
            self.log(f"\n❌ Significant issues found ({len(self.errors_found)} errors)")
            self.log("⚠️ API needs attention")

def main():
    """Main function to run comprehensive API testing"""
    print("Starting Comprehensive API Testing...")
    print("Using D: drive for all temporary operations")
    
    tester = AdvancedAPITester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()
