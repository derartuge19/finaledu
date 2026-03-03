"""
Database migration script to add content_hash column to certificates table.

This migration adds cryptographic hash verification capability to the EduCerts system.
The content_hash column stores SHA-256 hashes of certificate PDF content for tamper detection.
"""

from sqlalchemy import text
import database

def upgrade():
    """Add content_hash column and index to certificates table."""
    print("Starting migration: Adding content_hash column...")
    
    with database.engine.connect() as conn:
        # Add content_hash column (nullable to support legacy certificates)
        print("  - Adding content_hash VARCHAR(64) column...")
        conn.execute(text("""
            ALTER TABLE certificates 
            ADD COLUMN content_hash VARCHAR(64);
        """))
        
        # Create index for performance
        print("  - Creating index on content_hash...")
        conn.execute(text("""
            CREATE INDEX idx_certificates_content_hash 
            ON certificates(content_hash);
        """))
        
        conn.commit()
    
    print("Migration completed successfully!")
    print("  - Column 'content_hash' added to 'certificates' table")
    print("  - Index 'idx_certificates_content_hash' created")

def downgrade():
    """Remove content_hash column and index from certificates table."""
    print("Starting rollback: Removing content_hash column...")
    
    with database.engine.connect() as conn:
        # Drop index first
        print("  - Dropping index idx_certificates_content_hash...")
        conn.execute(text("""
            DROP INDEX IF EXISTS idx_certificates_content_hash;
        """))
        
        # Drop column
        print("  - Dropping content_hash column...")
        conn.execute(text("""
            ALTER TABLE certificates 
            DROP COLUMN content_hash;
        """))
        
        conn.commit()
    
    print("Rollback completed successfully!")
    print("  - Index 'idx_certificates_content_hash' dropped")
    print("  - Column 'content_hash' removed from 'certificates' table")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_add_content_hash.py [upgrade|downgrade]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "upgrade":
        upgrade()
    elif command == "downgrade":
        downgrade()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python migrate_add_content_hash.py [upgrade|downgrade]")
        sys.exit(1)
