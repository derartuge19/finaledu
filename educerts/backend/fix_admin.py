import sqlite3

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Update admin status
cursor.execute("UPDATE users SET is_admin = 1 WHERE name = 'settings_admin'")
conn.commit()

# Show all users
cursor.execute("SELECT id, name, email, is_admin FROM users")
users = cursor.fetchall()
print("All users:")
for user in users:
    print(f"  {user[0]}: {user[1]} ({user[2]}) - Admin: {user[3]}")

conn.close()