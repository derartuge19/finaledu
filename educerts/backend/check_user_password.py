import sqlite3
from passlib.context import CryptContext

# Use the same password context as the auth system
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Get user details
cursor.execute("SELECT id, name, email, password, is_admin FROM users WHERE name = 'Eden';")
user = cursor.fetchone()

if user:
    print(f"User found: {user[1]} ({user[2]})")
    print(f"Admin: {user[4]}")
    
    # Create new password using the correct hashing
    new_password = "admin123"
    new_hash = pwd_context.hash(new_password)
    
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user[0]))
    conn.commit()
    print(f"✓ Password updated to '{new_password}' using pbkdf2_sha256")
    
    # Verify it works
    if pwd_context.verify(new_password, new_hash):
        print("✓ Password verification successful")
    else:
        print("✗ Password verification failed")
else:
    print("User 'Eden' not found")

conn.close()