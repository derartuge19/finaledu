#!/usr/bin/env python3
"""
Debug script for bulk delete authentication issue
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_bulk_delete():
    print("🔍 Testing bulk delete authentication...")
    
    # First, try to login to get a session
    print("\n1. Testing login...")
    try:
        login_response = requests.post(
            f"{API_BASE}/api/login",
            data={
                "username": "admin",  # Change to your admin username
                "password": "admin123"  # Change to your admin password
            },
            allow_redirects=False
        )
        
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Login successful")
            # Extract cookies from login response
            cookies = login_response.cookies
            print(f"Cookies received: {cookies}")
            
            # Now try bulk delete with the cookies
            print("\n2. Testing bulk delete with cookies...")
            delete_response = requests.post(
                f"{API_BASE}/api/certificates/bulk-delete",
                json={"cert_ids": []},  # Empty list should work
                cookies=cookies
            )
            
            print(f"Bulk delete status: {delete_response.status_code}")
            print(f"Response: {delete_response.text}")
            
            if delete_response.status_code == 200:
                print("✅ Bulk delete works!")
            elif delete_response.status_code == 401:
                print("❌ 401 Unauthorized - Authentication failed")
                print("Possible causes:")
                print("  - Session expired")
                print("  - Cookies not being sent properly")
                print("  - Invalid credentials")
            elif delete_response.status_code == 403:
                print("❌ 403 Forbidden - Admin access required")
                print("You are logged in but not an admin")
            else:
                print(f"❌ Unexpected status: {delete_response.status_code}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_bulk_delete()
