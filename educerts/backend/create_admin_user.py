import requests

def create_admin_user():
    base_url = "http://localhost:8000"
    
    # Create a new admin user
    signup_data = {
        "name": "settings_admin",
        "email": "settings@educerts.io",
        "password": "settings123"
    }
    
    print("Creating admin user...")
    try:
        response = requests.post(f"{base_url}/api/signup", json=signup_data)
        print(f"Signup: {response.status_code}")
        if response.status_code == 200:
            print(f"  Success: {response.json()}")
            
            # Make user admin in database
            import sqlite3
            conn = sqlite3.connect('educerts.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET is_admin = 1 WHERE name = 'settings_admin'")
            conn.commit()
            conn.close()
            print("  Made user admin")
            
            # Test login
            print("\nTesting login...")
            session = requests.Session()
            login_data = {"username": "settings_admin", "password": "settings123"}
            
            response = session.post(f"{base_url}/api/login", data=login_data)
            print(f"Login: {response.status_code}")
            if response.status_code == 200:
                print(f"  Success: {response.json()}")
                
                # Test signature records endpoint
                print("\nTesting signature records...")
                records_response = session.get(f"{base_url}/api/sign/records")
                print(f"Signature records: {records_response.status_code}")
                if records_response.status_code == 200:
                    records = records_response.json()
                    print(f"  Found {len(records)} signature records")
                else:
                    print(f"  Error: {records_response.text}")
            
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Connection error: {e}")

if __name__ == "__main__":
    create_admin_user()