#!/usr/bin/env python3
"""
Migration script to remove course_name column from certificates table
"""
import os
import sys
from sqlalchemy import text
from database import engine, Base

def remove_course_name_column():
    """Remove course_name column from certificates table"""
    
    # Connect to database
    with engine.connect() as conn:
        try:
            # Check if course_name column exists
            result = conn.execute(text("""
                SELECT name FROM pragma_table_info('certificates') WHERE name = 'course_name'
            """))
            
            if result.fetchone():
                print("🔧 Removing course_name column from certificates table...")
                
                # Remove the column
                conn.execute(text("ALTER TABLE certificates DROP COLUMN course_name"))
                conn.commit()
                
                print("✅ course_name column removed successfully")
            else:
                print("ℹ️ course_name column does not exist")
                
        except Exception as e:
            print(f"❌ Error removing course_name column: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("🔄 Starting migration: Remove course_name column")
    remove_course_name_column()
    print("✅ Migration completed")
