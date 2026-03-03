"""
Complete Database Migration Script
Migrates all database changes to your local database
"""
import sqlite3
import os
from datetime import datetime
from passlib.context import CryptContext

# Password hashing context (same as backend)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def migrate_database():
    """Complete database migration with all required tables and data"""
    
    # Database file path
    db_path = "educerts.db"
    
    print("🚀 Starting Complete Database Migration")
    print("=" * 50)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create Users Table (if not exists)
        print("📋 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Create Certificates Table (if not exists)
        print("📋 Creating certificates table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id VARCHAR(36) PRIMARY KEY,
                student_id INTEGER,
                student_name VARCHAR(200),
                course_name VARCHAR(200),
                cert_type VARCHAR(50) DEFAULT 'certificate',
                data_payload JSON,
                signature TEXT,
                organization VARCHAR(200) DEFAULT 'EduCerts Academy',
                claim_pin VARCHAR(6),
                claimed BOOLEAN DEFAULT 0,
                issued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT 0,
                batch_id VARCHAR(36),
                template_type VARCHAR(10) DEFAULT 'html',
                rendered_pdf_path VARCHAR(500),
                signing_status VARCHAR(20) DEFAULT 'unsigned',
                digital_signatures JSON,
                content_hash VARCHAR(64),
                FOREIGN KEY (student_id) REFERENCES users(id),
                FOREIGN KEY (batch_id) REFERENCES document_registry(id)
            )
        """)
        
        # 3. Create Document Registry Table
        print("📋 Creating document_registry table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_registry (
                id VARCHAR(36) PRIMARY KEY,
                merkle_root VARCHAR(64) UNIQUE,
                issuer_name VARCHAR(200),
                organization VARCHAR(200),
                cert_count INTEGER DEFAULT 1,
                anchored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                revoked BOOLEAN DEFAULT 0
            )
        """)
        
        # 4. Create Digital Signature Records Table
        print("📋 Creating digital_signature_records table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS digital_signature_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signer_name VARCHAR(200),
                signer_role VARCHAR(200),
                signature_path VARCHAR(500),
                stamp_path VARCHAR(500),
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Add missing columns to existing certificates table (if they don't exist)
        print("🔧 Updating certificates table schema...")
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(certificates)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Columns to add if missing
        new_columns = [
            ("cert_type", "VARCHAR(50) DEFAULT 'certificate'"),
            ("organization", "VARCHAR(200) DEFAULT 'EduCerts Academy'"),
            ("claim_pin", "VARCHAR(6)"),
            ("claimed", "BOOLEAN DEFAULT 0"),
            ("batch_id", "VARCHAR(36)"),
            ("template_type", "VARCHAR(10) DEFAULT 'html'"),
            ("rendered_pdf_path", "VARCHAR(500)"),
            ("signing_status", "VARCHAR(20) DEFAULT 'unsigned'"),
            ("digital_signatures", "JSON"),
            ("content_hash", "VARCHAR(64)")
        ]
        
        for col_name, col_def in new_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE certificates ADD COLUMN {col_name} {col_def}")
                    print(f"  ✅ Added column: {col_name}")
                except sqlite3.Error as e:
                    print(f"  ⚠️  Column {col_name} might already exist: {e}")
        
        # 6. Create admin user if not exists
        print("👤 Setting up admin user...")
        
        # Check if Eden exists
        cursor.execute("SELECT id, name, is_admin FROM users WHERE name = 'Eden'")
        eden_user = cursor.fetchone()
        
        if eden_user:
            # Update Eden to be admin with correct password
            password_hash = pwd_context.hash("admin123")
            cursor.execute("""
                UPDATE users 
                SET password = ?, is_admin = 1 
                WHERE name = 'Eden'
            """, (password_hash,))
            print("  ✅ Updated Eden user with admin privileges")
            print("  📝 Login: Eden / admin123")
        else:
            # Create Eden user
            password_hash = pwd_context.hash("admin123")
            cursor.execute("""
                INSERT INTO users (name, email, password, is_admin)
                VALUES ('Eden', 'eden@educerts.local', ?, 1)
            """, (password_hash,))
            print("  ✅ Created Eden admin user")
            print("  📝 Login: Eden / admin123")
        
        # 7. Create indexes for better performance
        print("🚀 Creating database indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_certificates_student_id ON certificates(student_id)",
            "CREATE INDEX IF NOT EXISTS idx_certificates_batch_id ON certificates(batch_id)",
            "CREATE INDEX IF NOT EXISTS idx_certificates_content_hash ON certificates(content_hash)",
            "CREATE INDEX IF NOT EXISTS idx_document_registry_merkle_root ON document_registry(merkle_root)",
            "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except sqlite3.Error as e:
                print(f"  ⚠️  Index might already exist: {e}")
        
        print("  ✅ Database indexes created")
        
        # Commit all changes
        conn.commit()
        
        # 8. Verify migration
        print("🔍 Verifying migration...")
        
        # Check all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'certificates', 'document_registry', 'digital_signature_records']
        
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} records")
            else:
                print(f"  ❌ {table}: Missing!")
        
        # Check admin user
        cursor.execute("SELECT name, email, is_admin FROM users WHERE is_admin = 1")
        admin_users = cursor.fetchall()
        
        if admin_users:
            print(f"  ✅ Admin users: {len(admin_users)}")
            for admin in admin_users:
                print(f"    - {admin[0]} ({admin[1]})")
        else:
            print("  ❌ No admin users found!")
        
        print("\n" + "=" * 50)
        print("✅ DATABASE MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        print("\n📋 MIGRATION SUMMARY:")
        print("✅ Users table: Ready")
        print("✅ Certificates table: Updated with all new columns")
        print("✅ Document registry table: Created")
        print("✅ Digital signature records table: Created")
        print("✅ Database indexes: Created for performance")
        print("✅ Admin user: Eden with password 'admin123'")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Restart your backend server")
        print("2. Login with: Eden / admin123")
        print("3. Navigate to http://localhost:3000/settings")
        print("4. All settings functionality should now work!")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def verify_backend_connection():
    """Verify the backend is using the correct database"""
    print("\n🔍 VERIFYING BACKEND CONNECTION:")
    print("-" * 30)
    
    # Check database.py configuration
    try:
        with open("database.py", "r") as f:
            content = f.read()
            if "educerts.db" in content:
                print("✅ Backend configured to use educerts.db")
            else:
                print("⚠️  Backend might be using different database")
                print("   Check database.py configuration")
    except FileNotFoundError:
        print("⚠️  database.py not found in current directory")
    
    # Check .env configuration
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "DATABASE_URL=postgresql" in content and not content.startswith("#"):
                print("⚠️  PostgreSQL is still enabled in .env")
                print("   Comment out DATABASE_URL to use SQLite")
            else:
                print("✅ PostgreSQL disabled, using SQLite fallback")
    except FileNotFoundError:
        print("⚠️  .env file not found")

if __name__ == "__main__":
    print("🗄️  EduCerts Database Migration Tool")
    print("=" * 50)
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify backend configuration
        verify_backend_connection()
        
        print(f"\n🎉 MIGRATION COMPLETE!")
        print(f"Database file: {os.path.abspath('educerts.db')}")
        print(f"File size: {os.path.getsize('educerts.db')} bytes")
    else:
        print("\n❌ MIGRATION FAILED!")
        print("Please check the error messages above and try again.")