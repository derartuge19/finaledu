import requests
import json

def test_signup_and_login():
    base_url = "http://localhost:8000"
    
    # Test signup first
    signup_data = {
        "name": "testuser",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    print("Testing signup...")
    try:
        response = requests.post(f"{base_url}/api/signup", json=signup_data)
        print(f"Signup: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")
    
    # Test login with new user
    print("\nTesting login with new user...")
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    try:
        session = requests.Session()
        response = session.post(f"{base_url}/api/login", data=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success: {response.json()}")
            
            # Test authenticated endpoint
            me_response = session.get(f"{base_url}/api/me")
            print(f"  /api/me: {me_response.status_code}")
            if me_response.status_code == 200:
                print(f"    User: {me_response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")

if __name__ == "__main__":
    test_signup_and_login()