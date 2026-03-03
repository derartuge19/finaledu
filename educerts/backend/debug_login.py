import sqlite3
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Check all users
cursor.execute("SELECT id, name, email, password, is_admin FROM users;")
users = cursor.fetchall()

print("All users in database:")
for user in users:
    print(f"  ID: {user[0]}, Name: '{user[1]}', Email: '{user[2]}', Admin: {user[4]}")
    
    # Test password verification
    test_password = "admin123"
    try:
        if pwd_context.verify(test_password, user[3]):
            print(f"    ✓ Password '{test_password}' works for {user[1]}")
        else:
            print(f"    ✗ Password '{test_password}' doesn't work for {user[1]}")
    except Exception as e:
        print(f"    ✗ Password verification error: {e}")

conn.close()

# Also test the login logic directly
print("\nTesting login logic...")
import requests

# Test with both name and email
test_credentials = [
    {"username": "Eden", "password": "admin123"},
    {"username": "edenzewdutadesse11@gmail.com", "password": "admin123"}
]

for creds in test_credentials:
    try:
        response = requests.post("http://localhost:8000/api/login", data=creds)
        print(f"Login with {creds['username']}: {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.text}")
        else:
            print(f"  Success: {response.json()}")
    except Exception as e:
        print(f"  Connection error: {e}")