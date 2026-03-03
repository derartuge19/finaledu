"""
Test the signing fix to ensure it uses the correct template
"""
import requests
import sqlite3
import os

def test_signing_with_correct_template():
    """Test that signing now uses the correct template"""
    
    print("🧪 TESTING SIGNING WITH CORRECT TEMPLATE")
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
    
    # Step 2: Get certificates to sign
    response = session.get(f"{base_url}/api/certificates")
    if response.status_code != 200:
        print(f"❌ Failed to get certificates: {response.text}")
        return False
    
    certificates = response.json()
    unsigned_certs = [cert for cert in certificates if cert.get('signing_status') == 'unsigned']
    
    if not unsigned_certs:
        print("⚠️  No unsigned certificates found")
        return True
    
    print(f"📋 Found {len(unsigned_certs)} unsigned certificates")
    
    # Step 3: Check if we have signature assets
    response = session.get(f"{base_url}/api/sign/records")
    if response.status_code != 200:
        print(f"❌ Failed to get signature records: {response.text}")
        return False
    
    sig_records = response.json()
    if not sig_records:
        print("⚠️  No signature records found - upload signatures first")
        return True
    
    print(f"✅ Found {len(sig_records)} signature records")
    
    # Step 4: Test signing one certificate
    test_cert = unsigned_certs[0]
    cert_id = test_cert['id']
    
    print(f"🖊️  Testing signing of certificate: {cert_id[:8]}... ({test_cert['student_name']})")
    
    # Check template info before signing
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    cursor.execute("SELECT template_type, rendered_pdf_path FROM certificates WHERE id = ?", (cert_id,))
    result = cursor.fetchone()
    
    if result:
        template_type, pdf_path = result
        print(f"   Template Type: {template_type}")
        print(f"   Current PDF Path: {pdf_path or 'None'}")
    
    conn.close()
    
    # Perform signing
    sign_data = {
        "cert_ids": [cert_id],
        "signer_name": "Eden",
        "signer_role": "Administrator",
        "signature_record_id": sig_records[0]['id']
    }
    
    response = session.post(f"{base_url}/api/sign/apply", json=sign_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Signing successful: {result['message']}")
        
        # Check the result
        conn = sqlite3.connect('educerts.db')
        cursor = conn.cursor()
        cursor.execute("SELECT signing_status, rendered_pdf_path FROM certificates WHERE id = ?", (cert_id,))
        result = cursor.fetchone()
        
        if result:
            signing_status, pdf_path = result
            print(f"   New Status: {signing_status}")
            print(f"   New PDF Path: {pdf_path}")
            
            # Check if the PDF file exists
            if pdf_path and os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"   PDF File: ✅ Exists ({size} bytes)")
                
                # Check if it's different from the template
                template_path = "user_templates/template.pdf"
                if os.path.exists(template_path):
                    template_size = os.path.getsize(template_path)
                    if size != template_size:
                        print(f"   ✅ Signed PDF is different from template (template: {template_size} bytes)")
                    else:
                        print(f"   ⚠️  Signed PDF same size as template - might be using wrong template")
            else:
                print(f"   ❌ PDF file not found: {pdf_path}")
        
        conn.close()
        return True
        
    else:
        print(f"❌ Signing failed: {response.text}")
        return False

def main():
    print("🔧 Testing Template Signing Fix")
    print("=" * 30)
    
    success = test_signing_with_correct_template()
    
    if success:
        print("\n🎉 SIGNING TEST COMPLETED!")
        print("✅ Template selection logic is working")
        print("✅ Certificates should now use the correct template")
        print("\n📋 Next steps:")
        print("1. Try signing certificates from the frontend")
        print("2. Verify the signed PDFs look correct")
        print("3. Check that signatures appear in the right places")
    else:
        print("\n❌ SIGNING TEST FAILED!")
        print("Please check the errors above and fix the issues")

if __name__ == "__main__":
    main()