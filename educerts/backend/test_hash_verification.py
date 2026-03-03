"""
Simple test to verify cryptographic hash verification is working.
"""

import os
import sys
import fitz  # PyMuPDF
import pdf_hash_utils

def create_test_pdf(path, content):
    """Create a simple test PDF with given content."""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), content, fontsize=12)
    doc.save(path)
    doc.close()

def test_hash_computation():
    """Test that hash computation works correctly."""
    print("="*60)
    print("TEST 1: Hash Computation")
    print("="*60)
    
    test_pdf = "test_cert_temp.pdf"
    
    try:
        # Create test PDF
        create_test_pdf(test_pdf, "Test Certificate\nStudent: John Doe\nCourse: Computer Science")
        print("✓ Created test PDF")
        
        # Compute hash
        hash1 = pdf_hash_utils.compute_pdf_content_hash(test_pdf)
        print(f"✓ Computed hash: {hash1[:16]}...")
        
        # Compute again - should be identical
        hash2 = pdf_hash_utils.compute_pdf_content_hash(test_pdf)
        assert hash1 == hash2, "Hashes should be identical for same PDF"
        print("✓ Hash computation is deterministic")
        
        # Verify hash is 64 characters (SHA-256)
        assert len(hash1) == 64, "Hash should be 64 characters"
        print("✓ Hash is correct length (SHA-256)")
        
        print("\n✅ TEST 1 PASSED\n")
        return True
        
    finally:
        if os.path.exists(test_pdf):
            os.remove(test_pdf)

def test_tamper_detection():
    """Test that tampering is detected."""
    print("="*60)
    print("TEST 2: Tamper Detection")
    print("="*60)
    
    test_pdf1 = "test_cert_original.pdf"
    test_pdf2 = "test_cert_modified.pdf"
    
    try:
        # Create original PDF
        create_test_pdf(test_pdf1, "Student: John Doe\nGrade: A")
        hash1 = pdf_hash_utils.compute_pdf_content_hash(test_pdf1)
        print(f"✓ Original hash: {hash1[:16]}...")
        
        # Create modified PDF (tampered)
        create_test_pdf(test_pdf2, "Student: John Doe\nGrade: A+")  # Changed grade!
        hash2 = pdf_hash_utils.compute_pdf_content_hash(test_pdf2)
        print(f"✓ Modified hash: {hash2[:16]}...")
        
        # Hashes should be different
        assert hash1 != hash2, "Hashes should differ for different content"
        print("✓ Tampering detected - hashes are different")
        
        print("\n✅ TEST 2 PASSED\n")
        return True
        
    finally:
        if os.path.exists(test_pdf1):
            os.remove(test_pdf1)
        if os.path.exists(test_pdf2):
            os.remove(test_pdf2)

def test_metadata_embedding():
    """Test that metadata embedding and extraction works."""
    print("="*60)
    print("TEST 3: Metadata Embedding & Extraction")
    print("="*60)
    
    test_pdf = "test_cert_metadata.pdf"
    test_hash = "a1b2c3d4e5f6" * 5 + "abcd"  # 64 char hash
    test_cert_id = "550e8400-e29b-41d4-a716-446655440000"
    
    try:
        # Create test PDF
        create_test_pdf(test_pdf, "Test Certificate")
        print("✓ Created test PDF")
        
        # Embed metadata
        pdf_hash_utils.embed_hash_in_pdf_metadata(test_pdf, test_hash, test_cert_id)
        print("✓ Embedded hash and cert ID in metadata")
        
        # Extract metadata
        metadata = pdf_hash_utils.extract_hash_from_pdf_metadata(test_pdf)
        print(f"✓ Extracted metadata: hash={metadata['content_hash'][:16]}..., cert_id={metadata['cert_id'][:8]}...")
        
        # Verify extracted values match
        assert metadata['content_hash'] == test_hash, "Extracted hash should match embedded hash"
        assert metadata['cert_id'] == test_cert_id, "Extracted cert ID should match embedded ID"
        print("✓ Metadata extraction successful")
        
        print("\n✅ TEST 3 PASSED\n")
        return True
        
    finally:
        if os.path.exists(test_pdf):
            os.remove(test_pdf)

def test_whitespace_normalization():
    """Test that whitespace differences don't affect hash."""
    print("="*60)
    print("TEST 4: Whitespace Normalization")
    print("="*60)
    
    test_pdf1 = "test_cert_spaces1.pdf"
    test_pdf2 = "test_cert_spaces2.pdf"
    
    try:
        # Create PDFs with different whitespace but same content
        create_test_pdf(test_pdf1, "Student:  John   Doe\nGrade: A")
        create_test_pdf(test_pdf2, "Student: John Doe\nGrade: A")
        
        hash1 = pdf_hash_utils.compute_pdf_content_hash(test_pdf1)
        hash2 = pdf_hash_utils.compute_pdf_content_hash(test_pdf2)
        
        print(f"✓ Hash 1 (extra spaces): {hash1[:16]}...")
        print(f"✓ Hash 2 (normal spaces): {hash2[:16]}...")
        
        # Hashes should be identical due to normalization
        assert hash1 == hash2, "Hashes should be identical after whitespace normalization"
        print("✓ Whitespace normalization working correctly")
        
        print("\n✅ TEST 4 PASSED\n")
        return True
        
    finally:
        if os.path.exists(test_pdf1):
            os.remove(test_pdf1)
        if os.path.exists(test_pdf2):
            os.remove(test_pdf2)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CRYPTOGRAPHIC CERTIFICATE VERIFICATION TESTS")
    print("="*60 + "\n")
    
    all_passed = True
    
    try:
        all_passed &= test_hash_computation()
        all_passed &= test_tamper_detection()
        all_passed &= test_metadata_embedding()
        all_passed &= test_whitespace_normalization()
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nCryptographic verification is working correctly.")
        print("The system can now detect tampering with certificate PDFs.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("="*60)
        sys.exit(1)
