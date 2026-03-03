import requests

# Test creating a user and immediately checking the database
def test_direct_signup():
    base_url = "http://localhost:8000"
    
    # Create a unique user
    import time
    timestamp = str(int(time.time()))
    
    signup_data = {
        "name": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "test12345"
    }
    
    print(f"Creating user: {signup_data['name']}")
    
    try:
        # Signup
        response = requests.post(f"{base_url}/api/signup", json=signup_data)
        print(f"Signup: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"  Created user: {user_data}")
            
            # Check database directly
            import sqlite3
            conn = sqlite3.connect('educerts.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, is_admin FROM users ORDER BY id DESC LIMIT 5")
            users = cursor.fetchall()
            print("Recent users in database:")
            for user in users:
                print(f"  {user[0]}: {user[1]} ({user[2]}) - Admin: {user[3]}")
            conn.close()
            
            # Try to login
            session = requests.Session()
            login_data = {"username": signup_data["name"], "password": "test12345"}
            
            response = session.post(f"{base_url}/api/login", data=login_data)
            print(f"Login: {response.status_code}")
            if response.status_code == 200:
                print(f"  Login success: {response.json()}")
            else:
                print(f"  Login error: {response.text}")
                
        else:
            print(f"  Signup error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_direct_signup()