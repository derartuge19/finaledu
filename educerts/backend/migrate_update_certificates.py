"""
Migration to add missing columns to certificates table
"""
import sqlite3

def migrate():
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(certificates);")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    # Define columns to add
    columns_to_add = [
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
    
    # Add missing columns
    for col_name, col_def in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE certificates ADD COLUMN {col_name} {col_def}")
                print(f"✓ Added column: {col_name}")
            except sqlite3.Error as e:
                print(f"✗ Failed to add column {col_name}: {e}")
    
    conn.commit()
    
    # Verify all columns exist now
    cursor.execute("PRAGMA table_info(certificates);")
    final_columns = [col[1] for col in cursor.fetchall()]
    print(f"\nFinal columns: {final_columns}")
    
    conn.close()

if __name__ == "__main__":
    migrate()