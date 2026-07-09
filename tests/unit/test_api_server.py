"""
API Server Test Suite
Tests the enhanced FastAPI server endpoints
"""

import requests
import json
import time
import sys
import subprocess
import threading
from typing import Dict, Any

class APIServerTester:
    """Test the enhanced FastAPI server."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.server_process = None
        
    def start_server(self):
        """Start the FastAPI server."""
        print("🚀 Starting Enhanced FastAPI Server...")
        try:
            self.server_process = subprocess.Popen([
                sys.executable, "enhanced_fastapi_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Check if server is running
            if self.is_server_running():
                print("✅ Server started successfully!")
                return True
            else:
                print("❌ Server failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            return False
    
    def is_server_running(self) -> bool:
        """Check if the server is running."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_server(self):
        """Stop the FastAPI server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("🛑 Server stopped")
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        print("\n1. Testing Health Endpoint")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    def test_price_prediction_endpoint(self):
        """Test the price prediction endpoint."""
        print("\n2. Testing Price Prediction Endpoint")
        print("-" * 40)
        
        test_cases = [
            {
                "name": "Toyota Corolla GLI 2020",
                "data": {
                    "make": "Toyota",
                    "model": "Corolla",
                    "year": 2020,
                    "engine_capacity": 1300,
                    "transmission": "manual",
                    "location": "Lahore",
                    "variant": "gli"
                }
            },
            {
                "name": "Honda Civic VTi 2019",
                "data": {
                    "make": "Honda",
                    "model": "Civic",
                    "year": 2019,
                    "engine_capacity": 1800,
                    "transmission": "automatic",
                    "location": "Karachi",
                    "variant": "vti"
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   {i}. Testing: {test_case['name']}")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=test_case['data'],
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"      ✅ Success ({response_time:.3f}s)")
                    print(f"      💰 Price: {result['predicted_price']:,} PKR")
                    print(f"      📊 Confidence: {result['confidence']:.2f}")
                    print(f"      📈 Range: {result['price_range']['min']:,.0f} - {result['price_range']['max']:,.0f}")
                else:
                    print(f"      ❌ Error: {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"      ❌ Exception: {e}")
    
    def test_recommendations_endpoint(self):
        """Test the recommendations endpoint."""
        print("\n3. Testing Recommendations Endpoint")
        print("-" * 40)
        
        test_cases = [
            {
                "name": "Budget Cars (25 Lakh)",
                "data": {
                    "budget": 2500000,
                    "preferences": {
                        "transmission": "manual"
                    },
                    "max_results": 5
                }
            },
            {
                "name": "Premium Cars (50 Lakh)",
                "data": {
                    "budget": 5000000,
                    "preferences": {
                        "transmission": "automatic",
                        "min_year": 2018
                    },
                    "max_results": 3
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n   {i}. Testing: {test_case['name']}")
            
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/recommendations",
                    json=test_case['data'],
                    timeout=10
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"      ✅ Success ({response_time:.3f}s)")
                    print(f"      📊 Found: {result['total_found']} recommendations")
                    
                    for j, rec in enumerate(result['recommendations'][:3], 1):
                        print(f"      {j}. {rec['make']} {rec['model']} {rec['year']} - {rec['price']:,} PKR")
                        
                else:
                    print(f"      ❌ Error: {response.status_code}")
                    print(f"      Response: {response.text}")
                    
            except Exception as e:
                print(f"      ❌ Exception: {e}")
    
    def test_dashboard_stats_endpoint(self):
        """Test the dashboard stats endpoint."""
        print("\n4. Testing Dashboard Stats Endpoint")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats")
            
            if response.status_code == 200:
                result = response.json()
                print("      ✅ Success")
                print(f"      📊 Total Cars: {result.get('total_cars', 'N/A')}")
                print(f"      📈 Avg Price: {result.get('average_price', 'N/A')}")
                print(f"      🏭 Top Brand: {result.get('top_brand', 'N/A')}")
            else:
                print(f"      ❌ Error: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"      ❌ Exception: {e}")
    
    def test_performance_metrics(self):
        """Test API performance metrics."""
        print("\n5. Testing Performance Metrics")
        print("-" * 40)
        
        # Test multiple requests for performance
        test_data = {
            "make": "Toyota",
            "model": "Corolla",
            "year": 2020,
            "engine_capacity": 1300,
            "transmission": "manual",
            "location": "Lahore",
            "variant": "gli"
        }
        
        num_requests = 5
        total_time = 0
        successful_requests = 0
        
        print(f"   Testing {num_requests} concurrent requests...")
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/predict",
                    json=test_data,
                    timeout=10
                )
                request_time = time.time() - start_time
                
                if response.status_code == 200:
                    successful_requests += 1
                    total_time += request_time
                    print(f"   Request {i+1}: {request_time:.3f}s ✅")
                else:
                    print(f"   Request {i+1}: Failed ❌")
                    
            except Exception as e:
                print(f"   Request {i+1}: Exception - {e}")
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            print(f"\n   📊 Performance Summary:")
            print(f"   Success Rate: {successful_requests}/{num_requests} ({successful_requests/num_requests*100:.1f}%)")
            print(f"   Average Response Time: {avg_time:.3f}s")
            print(f"   Requests per Second: {1/avg_time:.1f}")
    
    def run_all_tests(self):
        """Run all API tests."""
        print("="*60)
        print("ENHANCED API SERVER TEST SUITE")
        print("="*60)
        
        # Start server
        if not self.start_server():
            print("❌ Cannot start server, aborting tests")
            return
        
        try:
            # Wait for server to be ready
            time.sleep(2)
            
            # Run tests
            self.test_health_endpoint()
            self.test_price_prediction_endpoint()
            self.test_recommendations_endpoint()
            self.test_dashboard_stats_endpoint()
            self.test_performance_metrics()
            
            print("\n" + "="*60)
            print("ALL API TESTS COMPLETED! 🎉")
            print("="*60)
            
        finally:
            # Stop server
            self.stop_server()

def main():
    """Main function to run API tests."""
    tester = APIServerTester()
    
    # Check if server is already running
    if tester.is_server_running():
        print("✅ Server is already running, using existing instance")
        tester.server_process = None  # Don't try to stop it
    
    # Run tests
    tester.run_all_tests()

if __name__ == "__main__":
    main()
