import requests

print("Testing PakWheels Dashboard Server...")

# Test the main page
try:
    response = requests.get('http://localhost:5000/')
    print(f"Main page status: {response.status_code}")
    if "Loading PakWheels Dashboard" in response.text:
        print("✅ React HTML is loading")
    else:
        print("❌ Not serving React HTML")
except Exception as e:
    print(f"❌ Main page error: {e}")

# Test static file
try:
    response = requests.get('http://localhost:5000/static/js/main.c2c95771.js')
    print(f"JavaScript file status: {response.status_code}")
    if response.status_code == 200:
        print("✅ JavaScript file loading correctly")
    else:
        print("❌ JavaScript file not found - this is the issue!")
except Exception as e:
    print(f"❌ JavaScript file error: {e}")

# Test API
try:
    response = requests.get('http://localhost:5000/api/health')
    print(f"API health status: {response.status_code}")
    if response.status_code == 200:
        print("✅ API working")
        data = response.json()
        print(f"API response: {data.get('service')}")
    else:
        print("❌ API not working")
except Exception as e:
    print(f"❌ API error: {e}")
