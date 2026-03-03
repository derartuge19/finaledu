"""
Check which certificates have content hashes stored.
"""

from database import SessionLocal
from models import Certificate

db = SessionLocal()

certs = db.query(Certificate).all()
print(f"Total certificates: {len(certs)}")

with_hash = [c for c in certs if c.content_hash]
print(f"Certificates WITH hash: {len(with_hash)}")

without_hash = [c for c in certs if not c.content_hash]
print(f"Certificates WITHOUT hash: {len(without_hash)}")

if without_hash:
    print(f"\nCertificates missing hash:")
    for c in without_hash[:10]:
        print(f"  - {c.id[:8]}: {c.student_name} - {c.course_name}")
    
    if len(without_hash) > 10:
        print(f"  ... and {len(without_hash) - 10} more")
    
    print("\n⚠️  WARNING: These certificates will NOT detect tampering!")
    print("Run 'python backfill_content_hashes.py' to fix this.")

db.close()
