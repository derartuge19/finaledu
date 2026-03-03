"""
Fix Eden's password to work with the frontend
"""
import sqlite3
from passlib.context import CryptContext

# Use the same password context as the backend
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Connect to the database
conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Set a simple password for Eden
new_password = "admin123"
password_hash = pwd_context.hash(new_password)

# Update Eden's password
cursor.execute("UPDATE users SET password = ? WHERE name = 'Eden'", (password_hash,))
conn.commit()

# Verify the update
cursor.execute("SELECT id, name, email, is_admin FROM users WHERE name = 'Eden'")
user = cursor.fetchone()

if user:
    print(f"✓ Updated password for user: {user[1]} ({user[2]})")
    print(f"  Admin status: {user[3]}")
    print(f"  New password: {new_password}")
    
    # Test password verification
    cursor.execute("SELECT password FROM users WHERE name = 'Eden'")
    stored_hash = cursor.fetchone()[0]
    
    if pwd_context.verify(new_password, stored_hash):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")
else:
    print("✗ User Eden not found")

conn.close()

print(f"\nTo use the settings page:")
print(f"1. Go to http://localhost:3000/login")
print(f"2. Login with: Eden / {new_password}")
print(f"3. Navigate to http://localhost:3000/settings")