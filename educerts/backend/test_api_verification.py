"""
Test the actual API verification endpoint with a tampered PDF.
This simulates exactly what happens when you upload through the frontend.
"""

import requests
import os
import fitz  # PyMuPDF
from database import SessionLocal
from models import Certificate

API_BASE = "http://localhost:8000"

def test_api_verification():
    print("="*60)
    print("API VERIFICATION TEST")
    print("="*60)
    
    db = SessionLocal()
    
    # Get a certificate
    cert = db.query(Certificate).first()
    if not cert:
        print("❌ No certificates found!")
        return False
    
    print(f"\n1. Testing certificate: {cert.id[:8]}")
    print(f"   Student: {cert.student_name}")
    
    if not cert.rendered_pdf_path or not os.path.exists(cert.rendered_pdf_path):
        print(f"❌ PDF not found: {cert.rendered_pdf_path}")
        return False
    
    # Test 1: Verify ORIGINAL PDF via API
    print("\n2. Uploading ORIGINAL PDF to /api/verify/pdf...")
    try:
        with open(cert.rendered_pdf_path, 'rb') as f:
            files = {'file': ('certificate.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE}/api/verify/pdf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API Response: {response.status_code}")
            print(f"   Overall Valid: {result['summary']['all']}")
            print(f"   Content Integrity: {result['summary'].get('contentIntegrity', 'N/A')}")
            
            # Check content integrity specifically
            content_check = next((d for d in result['data'] if d['type'] == 'CONTENT_INTEGRITY'), None)
            if content_check:
                print(f"   Content Hash Status: {content_check['status']}")
                if content_check['status'] == 'VALID':
                    print("   ✅ PASS: Original PDF verified as authentic!")
                else:
                    print(f"   ❌ FAIL: Original PDF marked as {content_check['status']}")
                    return False
            else:
                print("   ⚠️  WARNING: No content integrity check in response!")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test 2: Create and verify TAMPERED PDF
    print("\n3. Creating TAMPERED PDF...")
    tampered_path = cert.rendered_pdf_path.replace(".pdf", "_TAMPERED_API.pdf")
    
    try:
        # Create tampered version
        doc = fitz.open(cert.rendered_pdf_path)
        page = doc[0]
        
        # Add tampering text
        page.insert_text((100, 100), "TAMPERED: Fake Name", fontsize=12, color=(1, 0, 0))
        
        doc.save(tampered_path)
        doc.close()
        
        print(f"   ✅ Created: {tampered_path}")
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    
    # Test 3: Verify TAMPERED PDF via API
    print("\n4. Uploading TAMPERED PDF to /api/verify/pdf...")
    try:
        with open(tampered_path, 'rb') as f:
            files = {'file': ('certificate.pdf', f, 'application/pdf')}
            response = requests.post(f"{API_BASE}/api/verify/pdf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API Response: {response.status_code}")
            print(f"   Overall Valid: {result['summary']['all']}")
            print(f"   Content Integrity: {result['summary'].get('contentIntegrity', 'N/A')}")
            
            # Check content integrity
            content_check = next((d for d in result['data'] if d['type'] == 'CONTENT_INTEGRITY'), None)
            if content_check:
                print(f"   Content Hash Status: {content_check['status']}")
                print(f"   Hash Match: {content_check['data'].get('match', 'N/A')}")
                
                # THIS IS THE KEY CHECK
                if content_check['status'] == 'INVALID' and result['summary']['all'] == False:
                    print("   ✅ PASS: Tampering detected! Certificate marked as INVALID!")
                elif content_check['status'] == 'INVALID' and result['summary']['all'] == True:
                    print("   ❌ FAIL: Tampering detected BUT certificate still marked as VALID!")
                    print("   🐛 BUG: Content hash check not failing overall verification!")
                    return False
                else:
                    print(f"   ❌ FAIL: Tampering NOT detected! Status: {content_check['status']}")
                    return False
            else:
                print("   ❌ FAIL: No content integrity check in response!")
                return False
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   {response.json()}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(tampered_path):
            try:
                os.remove(tampered_path)
                print(f"   🗑️  Cleaned up: {tampered_path}")
            except:
                pass
    
    print("\n" + "="*60)
    print("✅ ALL API TESTS PASSED!")
    print("="*60)
    print("\nThe API correctly:")
    print("- Verifies original PDFs as VALID")
    print("- Detects tampered PDFs as INVALID")
    print("- Fails overall verification when content is tampered")
    
    db.close()
    return True

if __name__ == "__main__":
    print("\nMake sure the backend is running on http://localhost:8000")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        exit(0)
    
    success = test_api_verification()
    if not success:
        print("\n⚠️  API verification is NOT working correctly!")
        exit(1)
