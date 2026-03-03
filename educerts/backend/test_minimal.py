"""
Minimal test to check what's working
"""
import requests

def test_endpoints():
    base_url = "http://localhost:8000"
    
    endpoints = [
        "/",
        "/api/certificates", 
        "/api/me",
        "/api/sign/records"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"{endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text}")
        except Exception as e:
            print(f"{endpoint}: Connection error - {e}")

if __name__ == "__main__":
    test_endpoints()