"""
Debug the login endpoint issue
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing Backend Imports...")
    
    try:
        import models
        print("✅ models imported")
    except Exception as e:
        print(f"❌ models import failed: {e}")
        return False
    
    try:
        import database
        print("✅ database imported")
    except Exception as e:
        print(f"❌ database import failed: {e}")
        return False
    
    try:
        import auth_utils
        print("✅ auth_utils imported")
    except Exception as e:
        print(f"❌ auth_utils import failed: {e}")
        return False
    
    try:
        from sqlalchemy.orm import Session
        print("✅ SQLAlchemy imported")
    except Exception as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection using SQLAlchemy"""
    print("\n🗄️  Testing SQLAlchemy Database Connection...")
    
    try:
        from database import SessionLocal, engine
        from models import User
        
        # Test engine connection
        with engine.connect() as conn:
            print("✅ SQLAlchemy engine connection works")
        
        # Test session
        db = SessionLocal()
        try:
            users = db.query(User).all()
            print(f"✅ Found {len(users)} users via SQLAlchemy")
            
            for user in users:
                print(f"  - {user.name} (Admin: {user.is_admin})")
            
            db.close()
            return True
            
        except Exception as e:
            print(f"❌ SQLAlchemy query failed: {e}")
            db.close()
            return False
            
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def test_auth_functions():
    """Test authentication functions directly"""
    print("\n🔐 Testing Authentication Functions...")
    
    try:
        import auth_utils
        from database import SessionLocal
        from models import User
        
        # Test password verification
        test_password = "admin123"
        
        db = SessionLocal()
        user = db.query(User).filter(User.name == "Eden").first()
        
        if user:
            print(f"✅ Found user: {user.name}")
            
            # Test password verification
            if auth_utils.verify_password(test_password, user.password):
                print("✅ Password verification works")
                
                # Test token creation
                token = auth_utils.create_access_token(data={"sub": user.name})
                print(f"✅ Token creation works: {token[:20]}...")
                
                # Test token decoding
                payload = auth_utils.decode_access_token(token)
                if payload and payload.get("sub") == user.name:
                    print("✅ Token decoding works")
                    return True
                else:
                    print("❌ Token decoding failed")
            else:
                print("❌ Password verification failed")
        else:
            print("❌ User not found")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Auth function test failed: {e}")
        return False

def main():
    print("🐛 Login Endpoint Debug Tool")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import issues found - check dependencies")
        return
    
    # Test database
    if not test_database_connection():
        print("\n❌ Database connection issues found")
        return
    
    # Test auth functions
    if not test_auth_functions():
        print("\n❌ Authentication function issues found")
        return
    
    print("\n🤔 All components work individually...")
    print("The issue might be in the FastAPI endpoint itself.")
    print("\n💡 Possible solutions:")
    print("1. Check FastAPI dependencies in main.py")
    print("2. Verify OAuth2PasswordRequestForm usage")
    print("3. Check for any middleware conflicts")
    print("4. Review exception handling in login endpoint")

if __name__ == "__main__":
    main()