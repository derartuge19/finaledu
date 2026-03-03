"""
Migration to add digital_signature_records table
"""
import sqlite3
from datetime import datetime

def migrate():
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='digital_signature_records';")
    if cursor.fetchone():
        print("✓ digital_signature_records table already exists")
        conn.close()
        return
    
    # Create the table
    cursor.execute("""
        CREATE TABLE digital_signature_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signer_name VARCHAR(200),
            signer_role VARCHAR(200),
            signature_path VARCHAR(500),
            stamp_path VARCHAR(500),
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✓ Created digital_signature_records table")
    
    # Verify creation
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='digital_signature_records';")
    if cursor.fetchone():
        print("✓ Table creation verified")
    else:
        print("✗ Table creation failed")
    
    conn.close()

if __name__ == "__main__":
    migrate()