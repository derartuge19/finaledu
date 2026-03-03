import requests
import sqlite3
import os
import glob

def find_backend_database():
    # Create a unique user to track
    import time
    timestamp = str(int(time.time()))
    
    signup_data = {
        "name": f"tracker_{timestamp}",
        "email": f"tracker_{timestamp}@example.com",
        "password": "tracker123456"
    }
    
    print(f"Creating tracker user: {signup_data['name']}")
    
    # Create user through API
    response = requests.post("http://localhost:8000/api/signup", json=signup_data)
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data['id']
        print(f"Created user with ID: {user_id}")
        
        # Search for database files that contain this user
        search_paths = [
            "*.db",
            "../*.db", 
            "../../*.db",
            os.path.expanduser("~/*.db"),
            "C:/temp/*.db",
            "C:/Users/*/AppData/Local/Temp/*.db"
        ]
        
        print("\nSearching for database files...")
        for pattern in search_paths:
            try:
                files = glob.glob(pattern)
                for db_file in files:
                    try:
                        conn = sqlite3.connect(db_file)
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
                        if cursor.fetchone():
                            cursor.execute(f"SELECT id, name FROM users WHERE id = {user_id}")
                            user = cursor.fetchone()
                            if user:
                                print(f"✓ Found user in: {os.path.abspath(db_file)}")
                                print(f"  User: {user}")
                        conn.close()
                    except:
                        pass
            except:
                pass
                
        # Also check current directory more thoroughly
        print(f"\nChecking current directory: {os.getcwd()}")
        for file in os.listdir('.'):
            if file.endswith('.db'):
                try:
                    conn = sqlite3.connect(file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
                    if cursor.fetchone():
                        cursor.execute("SELECT COUNT(*) FROM users")
                        count = cursor.fetchone()[0]
                        print(f"  {file}: {count} users")
                        cursor.execute("SELECT id, name FROM users ORDER BY id DESC LIMIT 3")
                        recent = cursor.fetchall()
                        for user in recent:
                            print(f"    {user[0]}: {user[1]}")
                    conn.close()
                except Exception as e:
                    print(f"  {file}: Error - {e}")
    else:
        print(f"Failed to create user: {response.text}")

if __name__ == "__main__":
    find_backend_database()