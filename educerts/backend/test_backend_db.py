import requests
import json

# Test if the backend can access the database
def test_backend_db():
    try:
        # Test a simple endpoint that doesn't require auth
        response = requests.get("http://localhost:8000/")
        print(f"Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        
        # Test certificates endpoint (should work without auth)
        response = requests.get("http://localhost:8000/api/certificates")
        print(f"Certificates endpoint: {response.status_code}")
        if response.status_code == 200:
            certs = response.json()
            print(f"  Found {len(certs)} certificates")
        else:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_backend_db()