"""
Quick script to test authentication and admin status.
Run this to verify your admin user credentials.
"""

import requests

API_BASE = "http://localhost:8000"

def test_login_and_auth():
    print("="*60)
    print("AUTHENTICATION TEST")
    print("="*60)
    
    # Test 1: Login
    print("\n1. Testing login...")
    session = requests.Session()
    
    login_data = {
        "username": "admin",  # Change this to your admin username
        "password": "admin123"  # Change this to your admin password
    }
    
    try:
        response = session.post(
            f"{API_BASE}/api/login",
            data=login_data
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ Login successful!")
            print(f"  User: {user_data['user']['name']}")
            print(f"  Email: {user_data['user']['email']}")
            print(f"  Is Admin: {user_data['user']['is_admin']}")
            
            if not user_data['user']['is_admin']:
                print("\n⚠️  WARNING: This user is NOT an admin!")
                print("   You need admin privileges to delete certificates.")
                return False
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"  Error: {response.json().get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False
    
    # Test 2: Check /api/me
    print("\n2. Testing /api/me endpoint...")
    try:
        response = session.get(f"{API_BASE}/api/me")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✓ Authentication verified!")
            print(f"  User: {user_data['name']}")
            print(f"  Is Admin: {user_data['is_admin']}")
        else:
            print(f"✗ Auth check failed: {response.status_code}")
            print(f"  Error: {response.json().get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Auth check error: {e}")
        return False
    
    # Test 3: Try bulk-delete endpoint
    print("\n3. Testing bulk-delete endpoint (with empty list)...")
    try:
        response = session.post(
            f"{API_BASE}/api/certificates/bulk-delete",
            json={"cert_ids": []}
        )
        
        if response.status_code == 200:
            print(f"✓ Bulk-delete endpoint accessible!")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Bulk-delete failed: {response.status_code}")
            print(f"  Error: {response.json().get('detail', 'Unknown error')}")
            
            if response.status_code == 401:
                print("\n  This is a 401 Unauthorized error.")
                print("  Possible causes:")
                print("  - Cookie not being sent properly")
                print("  - Session expired")
                print("  - CORS issue")
            elif response.status_code == 403:
                print("\n  This is a 403 Forbidden error.")
                print("  Your user is not an admin!")
            
            return False
            
    except Exception as e:
        print(f"✗ Bulk-delete test error: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour authentication is working correctly.")
    print("If you're still getting 401 errors in the browser:")
    print("1. Make sure you're logged in as an admin")
    print("2. Try logging out and logging back in")
    print("3. Clear your browser cookies")
    print("4. Check browser console for CORS errors")
    return True

if __name__ == "__main__":
    test_login_and_auth()
