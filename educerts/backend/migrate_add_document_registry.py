"""
Migration to add document_registry table
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_registry';")
    if cursor.fetchone():
        print("✓ document_registry table already exists")
        conn.close()
        return
    
    # Create the table
    cursor.execute("""
        CREATE TABLE document_registry (
            id VARCHAR(36) PRIMARY KEY,
            merkle_root VARCHAR(64) UNIQUE,
            issuer_name VARCHAR(200),
            organization VARCHAR(200),
            cert_count INTEGER DEFAULT 1,
            anchored_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            revoked BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    print("✓ Created document_registry table")
    
    # Verify creation
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_registry';")
    if cursor.fetchone():
        print("✓ Table creation verified")
    else:
        print("✗ Table creation failed")
    
    conn.close()

if __name__ == "__main__":
    migrate()