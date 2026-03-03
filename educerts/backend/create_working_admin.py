import requests
import sqlite3
import time

def create_working_admin():
    base_url = "http://localhost:8000"
    
    # Create a simple admin user
    signup_data = {
        "name": "admin",
        "email": "admin@educerts.local",
        "password": "password123"
    }
    
    print("Creating admin user...")
    try:
        response = requests.post(f"{base_url}/api/signup", json=signup_data)
        print(f"Signup: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Created user: {user_data}")
            
            # Wait a moment for the database to be written
            time.sleep(1)
            
            # Now make them admin by updating the database directly
            # We need to find the right database file
            db_files = ["educerts.db", "educerts_v2.db", "educerts_fallback.db"]
            
            for db_file in db_files:
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    
                    # Check if this database has our user
                    cursor.execute("SELECT id, name FROM users WHERE name = 'admin'")
                    user = cursor.fetchone()
                    
                    if user:
                        print(f"Found user in {db_file}: {user}")
                        
                        # Make them admin
                        cursor.execute("UPDATE users SET is_admin = 1 WHERE name = 'admin'")
                        conn.commit()
                        
                        # Verify
                        cursor.execute("SELECT id, name, is_admin FROM users WHERE name = 'admin'")
                        updated_user = cursor.fetchone()
                        print(f"Updated user: {updated_user}")
                        
                        conn.close()
                        
                        # Test login
                        print("\nTesting login...")
                        session = requests.Session()
                        login_data = {"username": "admin", "password": "password123"}
                        
                        login_response = session.post(f"{base_url}/api/login", data=login_data)
                        print(f"Login: {login_response.status_code}")
                        
                        if login_response.status_code == 200:
                            print(f"Login success: {login_response.json()}")
                            
                            # Test signature records
                            records_response = session.get(f"{base_url}/api/sign/records")
                            print(f"Signature records: {records_response.status_code}")
                            
                            if records_response.status_code == 200:
                                print(f"✓ Settings page should work! Use admin/password123")
                                return True
                            else:
                                print(f"Signature records error: {records_response.text}")
                        else:
                            print(f"Login error: {login_response.text}")
                        
                        break
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"Error with {db_file}: {e}")
            
        else:
            print(f"Signup error: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")
    
    return False

if __name__ == "__main__":
    create_working_admin()