import requests
import json

# Test the complete authentication flow
base_url = "http://localhost:8000"

def test_auth_flow():
    print("Testing complete authentication flow...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Step 1: Login
    login_data = {
        "username": "Eden",
        "password": "admin123"
    }
    
    try:
        response = session.post(f"{base_url}/api/login", data=login_data)
        print(f"Login attempt: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Login successful")
            user_data = response.json()
            print(f"  User: {user_data}")
            
            # Step 2: Test /api/me with session cookies
            me_response = session.get(f"{base_url}/api/me")
            print(f"GET /api/me with cookies: {me_response.status_code}")
            if me_response.status_code == 200:
                print(f"  Authenticated user: {me_response.json()}")
            
            # Step 3: Test signature records with session cookies
            records_response = session.get(f"{base_url}/api/sign/records")
            print(f"GET /api/sign/records with cookies: {records_response.status_code}")
            if records_response.status_code == 200:
                records = records_response.json()
                print(f"  Signature records: {len(records)} found")
            else:
                print(f"  Error: {records_response.text}")
                
        else:
            print(f"✗ Login failed: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_auth_flow()