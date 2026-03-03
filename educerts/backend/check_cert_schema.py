import sqlite3

conn = sqlite3.connect('educerts.db')
cursor = conn.cursor()

# Get certificates table schema
cursor.execute("PRAGMA table_info(certificates);")
columns = cursor.fetchall()
print("Certificates table columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check for required columns
required_columns = [
    'batch_id', 'template_type', 'rendered_pdf_path', 
    'signing_status', 'digital_signatures', 'content_hash'
]

existing_columns = [col[1] for col in columns]
missing_columns = [col for col in required_columns if col not in existing_columns]

if missing_columns:
    print(f"\nMissing columns: {missing_columns}")
else:
    print("\n✓ All required columns exist")

conn.close()