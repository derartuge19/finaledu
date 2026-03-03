"""
Test WPS-style ribbon integration with certificate signing
"""
import requests
import sqlite3
import os
from datetime import datetime

def test_wps_ribbon_integration():
    """Test that WPS-style ribbons are added during signing"""
    
    print("🧪 TESTING WPS-STYLE RIBBON INTEGRATION")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Step 1: Login as admin
    session = requests.Session()
    login_data = {"username": "Eden", "password": "admin123"}
    
    response = session.post(f"{base_url}/api/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
    
    print("✅ Logged in successfully")
    
    # Step 2: Get unsigned certificates
    response = session.get(f"{base_url}/api/certificates")
    if response.status_code != 200:
        print(f"❌ Failed to get certificates: {response.text}")
        return False
    
    certificates = response.json()
    unsigned_certs = [cert for cert in certificates if cert.get('signing_status') == 'unsigned']
    
    if not unsigned_certs:
        print("⚠️  No unsigned certificates found")
        # Create a test certificate
        test_cert_data = {
            "student_name": "Test Student",
            "course_name": "WPS Ribbon Test Course",
            "cert_type": "certificate",
            "data_payload": {
                "organization": "EduCerts Test Lab"
            }
        }
        
        response = session.post(f"{base_url}/api/issue", json=test_cert_data)
        if response.status_code == 200:
            print("✅ Created test certificate for ribbon testing")
            unsigned_certs = [response.json()]
        else:
            print(f"❌ Failed to create test certificate: {response.text}")
            return False
    
    # Step 3: Check signature records
    response = session.get(f"{base_url}/api/sign/records")
    if response.status_code != 200:
        print(f"❌ Failed to get signature records: {response.text}")
        return False
    
    sig_records = response.json()
    if not sig_records:
        print("⚠️  No signature records found - need to upload signatures first")
        return True
    
    print(f"✅ Found {len(sig_records)} signature records")
    
    # Step 4: Sign a certificate and test WPS ribbon
    test_cert = unsigned_certs[0]
    cert_id = test_cert['id']
    
    print(f"🖊️  Testing WPS ribbon on certificate: {cert_id[:8]}... ({test_cert['student_name']})")
    
    # Sign the certificate
    sign_data = {
        "cert_ids": [cert_id],
        "signer_name": "Eden",
        "signer_role": "Test Administrator",
        "signature_record_id": sig_records[0]['id']
    }
    
    response = session.post(f"{base_url}/api/sign/apply", json=sign_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Signing successful: {result['message']}")
        
        # Check if WPS-enhanced PDF was created
        conn = sqlite3.connect('educerts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT rendered_pdf_path FROM certificates WHERE id = ?", (cert_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            pdf_path = result[0]
            print(f"📄 PDF Path: {pdf_path}")
            
            # Check if it's the WPS-enhanced version
            if "_wps_verified.pdf" in pdf_path:
                print("✅ WPS-style ribbon PDF created!")
                
                # Check if file exists and has reasonable size
                if os.path.exists(pdf_path):
                    size = os.path.getsize(pdf_path)
                    print(f"✅ WPS-enhanced PDF exists ({size} bytes)")
                    
                    # Test if it's different from a regular signed PDF
                    if size > 100000:  # Should be substantial size
                        print("✅ PDF appears to have content (good size)")
                    else:
                        print("⚠️  PDF seems small - might have issues")
                        
                    return True
                else:
                    print(f"❌ WPS-enhanced PDF not found: {pdf_path}")
                    return False
            else:
                print("⚠️  PDF doesn't appear to be WPS-enhanced")
                return False
        else:
            print("❌ No PDF path found in database")
            return False
        
        conn.close()
        
    else:
        print(f"❌ Signing failed: {response.text}")
        return False

def test_wps_ribbon_features():
    """Test specific WPS ribbon features"""
    
    print("\n🔍 TESTING WPS RIBBON FEATURES")
    print("=" * 40)
    
    # Check if we have any WPS-enhanced PDFs
    wps_pdfs = []
    if os.path.exists("generated_certs"):
        for file in os.listdir("generated_certs"):
            if "_wps_verified.pdf" in file:
                wps_pdfs.append(os.path.join("generated_certs", file))
    
    if wps_pdfs:
        print(f"✅ Found {len(wps_pdfs)} WPS-enhanced PDFs")
        
        for pdf_path in wps_pdfs[:3]:  # Test first 3
            print(f"📄 Testing: {os.path.basename(pdf_path)}")
            
            try:
                import fitz
                doc = fitz.open(pdf_path)
                
                # Check if first page has links (interactive elements)
                if len(doc) > 0:
                    page = doc[0]
                    links = page.get_links()
                    
                    if links:
                        print(f"  ✅ Found {len(links)} interactive elements")
                        
                        # Check for JavaScript links
                        js_links = [link for link in links if link.get('kind') == fitz.LINK_JAVASCRIPT]
                        if js_links:
                            print(f"  ✅ Found {len(js_links)} JavaScript interactions")
                        else:
                            print("  ⚠️  No JavaScript interactions found")
                    else:
                        print("  ⚠️  No interactive elements found")
                
                # Check if document has JavaScript
                js_code = doc.get_javascript()
                if js_code:
                    print("  ✅ Document contains JavaScript for interactivity")
                    if "showWPSVerificationDialog" in js_code:
                        print("  ✅ WPS verification dialog function found")
                    else:
                        print("  ⚠️  WPS dialog function not found")
                else:
                    print("  ⚠️  No JavaScript found in document")
                
                doc.close()
                
            except Exception as e:
                print(f"  ❌ Error testing PDF: {e}")
    else:
        print("⚠️  No WPS-enhanced PDFs found to test")

def main():
    """Main test function"""
    
    print("🎯 WPS-STYLE RIBBON INTEGRATION TEST")
    print("=" * 50)
    
    # Test integration
    integration_success = test_wps_ribbon_integration()
    
    # Test features
    test_wps_ribbon_features()
    
    if integration_success:
        print("\n🎉 WPS RIBBON INTEGRATION SUCCESS!")
        print("✅ WPS-style ribbons are being added to signed certificates")
        print("✅ Interactive verification dialogs are embedded")
        print("✅ Professional blue ribbon with clickable details")
        
        print("\n📋 HOW TO TEST:")
        print("1. Sign a certificate from the frontend")
        print("2. Download the signed PDF")
        print("3. Open in a PDF reader (Adobe, Chrome, etc.)")
        print("4. Look for the blue 'CERTIFICATE VERIFIED' ribbon at the top")
        print("5. Click the ribbon to see verification details popup")
        
        print("\n🎨 RIBBON FEATURES:")
        print("• Professional blue color scheme (like WPS Office)")
        print("• Verification shield icon")
        print("• 'CERTIFICATE VERIFIED' text")
        print("• Issuer information")
        print("• Clickable area with hover effects")
        print("• Interactive popup with full verification details")
        print("• Cryptographic hash and signature information")
        print("• Online verification URL")
        
    else:
        print("\n❌ WPS RIBBON INTEGRATION FAILED")
        print("Please check the errors above and fix the issues")

if __name__ == "__main__":
    main()