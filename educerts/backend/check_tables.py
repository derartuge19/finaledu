import sqlite3

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

# Check if digital_signature_records table exists
if 'digital_signature_records' in tables:
    print("✓ digital_signature_records table exists")
    cursor.execute("SELECT COUNT(*) FROM digital_signature_records;")
    count = cursor.fetchone()[0]
    print(f"Records in digital_signature_records: {count}")
else:
    print("✗ digital_signature_records table missing")

conn.close()