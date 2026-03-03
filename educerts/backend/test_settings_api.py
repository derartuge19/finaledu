import requests
import json

# Test the settings API endpoints
base_url = "http://localhost:8000"

def test_api():
    print("Testing Settings API endpoints...")
    
    # Test 1: Get signature records (should work for admin)
    try:
        response = requests.get(f"{base_url}/api/sign/records")
        print(f"GET /api/sign/records: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Records found: {len(data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")
    
    # Test 2: Check if user endpoint works
    try:
        response = requests.get(f"{base_url}/api/me")
        print(f"GET /api/me: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  User: {data}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")
    
    # Test 3: Check certificates endpoint
    try:
        response = requests.get(f"{base_url}/api/certificates")
        print(f"GET /api/certificates: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Certificates found: {len(data)}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")

if __name__ == "__main__":
    test_api()