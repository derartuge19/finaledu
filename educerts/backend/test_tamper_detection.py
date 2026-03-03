"""
Test that tamper detection is working correctly.
This simulates what you're doing manually.
"""

import os
import fitz  # PyMuPDF
from database import SessionLocal
from models import Certificate
import pdf_hash_utils

def test_tamper_detection():
    print("="*60)
    print("TAMPER DETECTION TEST")
    print("="*60)
    
    db = SessionLocal()
    
    # Get a certificate
    cert = db.query(Certificate).first()
    if not cert:
        print("❌ No certificates found in database!")
        return False
    
    print(f"\n1. Testing certificate: {cert.id[:8]}")
    print(f"   Student: {cert.student_name}")
    print(f"   Course: {cert.course_name}")
    
    if not cert.content_hash:
        print("❌ Certificate has no content hash!")
        print("   Run: python backfill_content_hashes.py")
        return False
    
    print(f"   Stored hash: {cert.content_hash[:16]}...")
    
    # Check if PDF exists
    if not cert.rendered_pdf_path or not os.path.exists(cert.rendered_pdf_path):
        print(f"❌ PDF file not found: {cert.rendered_pdf_path}")
        return False
    
    print(f"   PDF path: {cert.rendered_pdf_path}")
    
    # Test 1: Verify original PDF
    print("\n2. Testing ORIGINAL PDF (should be valid)...")
    try:
        computed_hash = pdf_hash_utils.compute_pdf_content_hash(cert.rendered_pdf_path)
        print(f"   Computed hash: {computed_hash[:16]}...")
        
        if computed_hash == cert.content_hash:
            print("   ✅ PASS: Original PDF hash matches!")
        else:
            print("   ❌ FAIL: Original PDF hash doesn't match!")
            print(f"      Expected: {cert.content_hash}")
            print(f"      Got: {computed_hash}")
            return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test 2: Create tampered PDF
    print("\n3. Creating TAMPERED PDF (modifying student name)...")
    tampered_path = cert.rendered_pdf_path.replace(".pdf", "_TAMPERED.pdf")
    
    try:
        # Open original PDF
        doc = fitz.open(cert.rendered_pdf_path)
        
        # Get first page
        page = doc[0]
        
        # Get text to find student name
        text = page.get_text()
        print(f"   Original text contains: '{cert.student_name}'")
        
        # Create a new PDF with modified text
        # We'll add a text annotation to simulate tampering
        rect = fitz.Rect(100, 100, 300, 120)
        page.insert_text((100, 100), "TAMPERED: John Hacker", fontsize=12)
        
        # Save tampered PDF
        doc.save(tampered_path)
        doc.close()
        
        print(f"   ✅ Created tampered PDF: {tampered_path}")
        
    except Exception as e:
        print(f"   ❌ ERROR creating tampered PDF: {e}")
        return False
    
    # Test 3: Verify tampered PDF
    print("\n4. Testing TAMPERED PDF (should be INVALID)...")
    try:
        tampered_hash = pdf_hash_utils.compute_pdf_content_hash(tampered_path)
        print(f"   Tampered hash: {tampered_hash[:16]}...")
        
        if tampered_hash != cert.content_hash:
            print("   ✅ PASS: Tampering detected! Hashes don't match!")
            print(f"      Original: {cert.content_hash[:16]}...")
            print(f"      Tampered: {tampered_hash[:16]}...")
        else:
            print("   ❌ FAIL: Tampering NOT detected! Hashes match!")
            print("      This should not happen!")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        # Clean up tampered file
        if os.path.exists(tampered_path):
            try:
                os.remove(tampered_path)
                print(f"   🗑️  Cleaned up: {tampered_path}")
            except:
                pass
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nTamper detection is working correctly!")
    print("\nWhat this means:")
    print("- Original PDFs will verify as VALID")
    print("- Modified PDFs will be detected as TAMPERED")
    print("- The system is protecting against document forgery")
    
    db.close()
    return True

if __name__ == "__main__":
    success = test_tamper_detection()
    if not success:
        print("\n⚠️  Tamper detection is NOT working correctly!")
        print("Please check the errors above.")
        exit(1)
