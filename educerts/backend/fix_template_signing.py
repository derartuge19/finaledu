"""
Fix the template signing issue
"""
import sqlite3
import os

def fix_certificate_templates():
    """Fix certificate template information"""
    
    print("🔧 FIXING CERTIFICATE TEMPLATE ISSUE")
    print("=" * 50)
    
    conn = sqlite3.connect('educerts.db')
    cursor = conn.cursor()
    
    # Check if we have a PDF template
    pdf_template_path = "user_templates/template.pdf"
    has_pdf_template = os.path.exists(pdf_template_path)
    
    if has_pdf_template:
        print(f"✅ Found PDF template: {pdf_template_path}")
        
        # Update certificates to use PDF template if they don't have a rendered path
        cursor.execute("""
            UPDATE certificates 
            SET template_type = 'pdf' 
            WHERE template_type = 'html' AND rendered_pdf_path IS NULL
        """)
        
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} certificates to use PDF template")
        
    else:
        print("⚠️  No PDF template found, certificates will use HTML rendering")
    
    # Show current certificate status
    cursor.execute("""
        SELECT id, student_name, template_type, rendered_pdf_path, signing_status
        FROM certificates 
        ORDER BY issued_at DESC
    """)
    
    certs = cursor.fetchall()
    print(f"\n📋 Certificate Status ({len(certs)} total):")
    
    for cert in certs:
        cert_id, student_name, template_type, pdf_path, signing_status = cert
        status_icon = "✅" if signing_status == "signed" else "⏳"
        print(f"  {status_icon} {cert_id[:8]}... - {student_name}")
        print(f"     Template: {template_type}, Status: {signing_status}")
        
        if pdf_path and os.path.exists(pdf_path):
            print(f"     PDF: ✅ {pdf_path}")
        elif pdf_path:
            print(f"     PDF: ❌ {pdf_path} (missing)")
        else:
            print(f"     PDF: ⏳ (will be generated)")
        print()
    
    conn.commit()
    conn.close()
    
    print("🎯 NEXT STEPS:")
    print("1. Restart the backend server")
    print("2. Try signing certificates again")
    print("3. They should now use the correct PDF template")
    
    return True

if __name__ == "__main__":
    fix_certificate_templates()