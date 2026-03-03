import sqlite3

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Get all users and their admin status
cursor.execute("SELECT id, name, email, is_admin FROM users;")
users = cursor.fetchall()

print("Current users:")
for user in users:
    admin_status = "ADMIN" if user[3] else "USER"
    print(f"  ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Status: {admin_status}")

# Check if any admin exists
admin_count = sum(1 for user in users if user[3])
print(f"\nTotal users: {len(users)}")
print(f"Admin users: {admin_count}")

if admin_count == 0:
    print("\n⚠️  No admin users found! The settings page requires admin access.")
    print("Creating admin user...")
    
    # Make the first user an admin
    if users:
        first_user_id = users[0][0]
        cursor.execute("UPDATE users SET is_admin = 1 WHERE id = ?", (first_user_id,))
        conn.commit()
        print(f"✓ Made user '{users[0][1]}' an admin")
    else:
        print("No users exist. Please create a user first.")

conn.close()