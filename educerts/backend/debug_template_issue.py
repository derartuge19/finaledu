"""
Debug the template selection issue
"""
import sqlite3
import os

def debug_template_issue():
    """Debug why signing is using wrong template"""
    
    print("🔍 DEBUGGING TEMPLATE SELECTION ISSUE")
    print("=" * 50)
    
    # 1. Check available templates
    print("📁 Available Templates:")
    template_dir = "user_templates"
    if os.path.exists(template_dir):
        for file in os.listdir(template_dir):
            file_path = os.path.join(template_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size} bytes)")
    else:
        print("  ❌ user_templates directory not found")
    
    # 2. Check certificates and their template info
    print("\n📋 Certificate Template Info:")
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, student_name, course_name, template_type, rendered_pdf_path 
        FROM certificates 
        ORDER BY issued_at DESC 
        LIMIT 5
    """)
    
    certs = cursor.fetchall()
    
    for cert in certs:
        cert_id, student_name, course_name, template_type, pdf_path = cert
        print(f"  📄 {cert_id[:8]}... - {student_name}")
        print(f"     Template Type: {template_type}")
        print(f"     PDF Path: {pdf_path}")
        
        # Check if the PDF file exists
        if pdf_path and os.path.exists(pdf_path):
            size = os.path.getsize(pdf_path)
            print(f"     PDF Exists: ✅ ({size} bytes)")
        elif pdf_path:
            print(f"     PDF Exists: ❌ (file not found)")
        else:
            print(f"     PDF Exists: ❌ (no path stored)")
        print()
    
    conn.close()
    
    # 3. Check the hardcoded template path in signing logic
    print("🔧 Signing Logic Analysis:")
    hardcoded_template = "user_templates/template.pdf"
    
    if os.path.exists(hardcoded_template):
        size = os.path.getsize(hardcoded_template)
        print(f"  📄 Hardcoded template exists: {hardcoded_template} ({size} bytes)")
        print("  ⚠️  ISSUE: Signing always uses this template regardless of original")
    else:
        print(f"  ❌ Hardcoded template missing: {hardcoded_template}")
    
    print("\n💡 SOLUTION NEEDED:")
    print("  1. Signing should use the certificate's original template")
    print("  2. Or allow user to select which template to use for signing")
    print("  3. Store template info with each certificate")

if __name__ == "__main__":
    debug_template_issue()