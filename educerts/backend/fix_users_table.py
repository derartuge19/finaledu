"""
Fix the users table schema to match the model
"""
import sqlite3
from datetime import datetime

def fix_users_table():
    """Fix users table to match SQLAlchemy model"""
    
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    try:
        # Check if created_at column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'created_at' not in columns:
            print("Adding created_at column to users table...")
            
            # Add the column without default first
            cursor.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
            
            # Update existing records with current timestamp
            current_time = datetime.now().isoformat()
            cursor.execute("UPDATE users SET created_at = ? WHERE created_at IS NULL", (current_time,))
            
            conn.commit()
            print("✅ Added created_at column and updated existing records")
        else:
            print("✅ created_at column already exists")
        
        # Verify the fix
        cursor.execute("SELECT id, name, created_at FROM users")
        users = cursor.fetchall()
        
        print(f"✅ Users table now has {len(users)} records:")
        for user in users:
            print(f"  - ID: {user[0]}, Name: {user[1]}, Created: {user[2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing users table: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔧 Fixing Users Table Schema")
    print("=" * 30)
    
    if fix_users_table():
        print("\n✅ Users table fixed successfully!")
        print("Now restart the backend and test authentication.")
    else:
        print("\n❌ Failed to fix users table")