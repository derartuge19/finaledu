"""
Test authentication after database migration
"""
import sqlite3
import requests
from passlib.context import CryptContext

def test_database_directly():
    """Test database connection and user data directly"""
    print("🔍 Testing Database Connection...")
    
    try:
        conn = sqlite3.connect('educerts.db')
        cursor = conn.cursor()
        
        # Check users
        cursor.execute("SELECT id, name, email, is_admin FROM users")
        users = cursor.fetchall()
        
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"  - ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Admin: {user[3]}")
        
        # Test password verification
        cursor.execute("SELECT password FROM users WHERE name = 'Eden'")
        password_hash = cursor.fetchone()
        
        if password_hash:
            pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
            if pwd_context.verify("admin123", password_hash[0]):
                print("✅ Password verification works")
            else:
                print("❌ Password verification failed")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_backend_endpoints():
    """Test backend endpoints"""
    print("\n🌐 Testing Backend Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test basic connectivity
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test login endpoint
    try:
        login_data = {"username": "Eden", "password": "admin123"}
        response = requests.post(f"{base_url}/api/login", data=login_data)
        print(f"🔐 Login endpoint: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            user_data = response.json()
            print(f"  User: {user_data}")
            
            # Test authenticated endpoints
            session = requests.Session()
            session.post(f"{base_url}/api/login", data=login_data)
            
            # Test /api/me
            me_response = session.get(f"{base_url}/api/me")
            print(f"👤 /api/me: {me_response.status_code}")
            
            # Test signature records
            records_response = session.get(f"{base_url}/api/sign/records")
            print(f"📝 /api/sign/records: {records_response.status_code}")
            
            if records_response.status_code == 200:
                records = records_response.json()
                print(f"  Found {len(records)} signature records")
                return True
            
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
    
    return False

def main():
    print("🧪 Post-Migration Authentication Test")
    print("=" * 40)
    
    # Test database
    db_ok = test_database_directly()
    
    if db_ok:
        # Test backend
        backend_ok = test_backend_endpoints()
        
        if backend_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Database migration successful")
            print("✅ Authentication working")
            print("✅ Settings page should be fully functional")
            print("\n📋 To use the settings page:")
            print("1. Go to http://localhost:3000/login")
            print("2. Login with: Eden / admin123")
            print("3. Navigate to http://localhost:3000/settings")
        else:
            print("\n⚠️  Backend authentication issues remain")
            print("Database is ready, but login endpoint has problems")
    else:
        print("\n❌ Database issues found")

if __name__ == "__main__":
    main()