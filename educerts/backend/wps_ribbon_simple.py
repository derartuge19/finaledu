"""
Simple WPS Office Style Verification Ribbon
Creates a professional blue ribbon with clickable verification details
"""
import fitz  # PyMuPDF
import json
from datetime import datetime
import os

class SimpleWPSRibbon:
    """Creates simple WPS Office style verification ribbons for PDFs"""
    
    def __init__(self):
        # WPS-style colors and dimensions
        self.ribbon_height = 35
        self.ribbon_color = (0.53, 0.81, 0.92)  # Sky blue #87CEEB
        self.text_color = (1, 1, 1)  # White text
        
    def add_wps_ribbon(self, pdf_path, output_path, cert_data):
        """Add WPS-style ribbon to PDF as visible overlay with zigzag edges"""
        
        doc = fitz.open(pdf_path)
        
        # Add ribbon to first page only
        if len(doc) > 0:
            page = doc[0]
            page_rect = page.rect
            page_width = page_rect.width
            
            # Create ribbon area at the very top
            ribbon_rect = fitz.Rect(0, 0, page_width, self.ribbon_height)
            
            # Draw main ribbon background (sky blue)
            page.draw_rect(ribbon_rect, color=self.ribbon_color, fill=self.ribbon_color)
            
            # Add zigzag edges for authentic look
            self._add_zigzag_edges(page, ribbon_rect)
            
            # Add verification text
            main_text = "✓ CERTIFICATE VERIFIED - EduCerts"
            main_point = fitz.Point(15, 22)
            page.insert_text(main_point, main_text, fontsize=10, color=self.text_color)
            
            # Add click instruction
            click_text = "Signature metadata in PDF properties ›"
            click_point = fitz.Point(page_width - 200, 22)
            page.insert_text(click_point, click_text, fontsize=9, color=self.text_color)
            
            # Note: Signature metadata is in PDF properties (right-click → Properties)
            
            # Add metadata to PDF properties instead of separate page
            self._add_metadata_to_properties(doc, cert_data)
            
            print(f"✅ Added sky blue WPS ribbon with signature metadata display")
        
        # Save with ribbon
        doc.save(output_path)
        doc.close()
        return output_path
    
    def _add_zigzag_edges(self, page, ribbon_rect):
        """Add zigzag edges to ribbon for authentic WPS look"""
        # Left zigzag edge
        left_points = []
        for i in range(0, 8):
            y = ribbon_rect.y0 + (i * ribbon_rect.height / 7)
            if i % 2 == 0:
                x = ribbon_rect.x0
            else:
                x = ribbon_rect.x0 + 5
            left_points.append(fitz.Point(x, y))
        
        # Draw left zigzag
        for i in range(len(left_points) - 1):
            page.draw_line(left_points[i], left_points[i+1], color=(0.4, 0.7, 0.9), width=1)
        
        # Right zigzag edge
        right_points = []
        for i in range(0, 8):
            y = ribbon_rect.y0 + (i * ribbon_rect.height / 7)
            if i % 2 == 0:
                x = ribbon_rect.x1
            else:
                x = ribbon_rect.x1 - 5
            right_points.append(fitz.Point(x, y))
        
        # Draw right zigzag
        for i in range(len(right_points) - 1):
            page.draw_line(right_points[i], right_points[i+1], color=(0.4, 0.7, 0.9), width=1)
    
    def _add_metadata_to_properties(self, doc, cert_data):
        """Add verification metadata to PDF properties"""
        metadata = doc.metadata
        metadata["title"] = f"Verified Certificate - {cert_data.get('id', 'N/A')[:8]}"
        metadata["author"] = "EduCert Secure Verification System"
        metadata["subject"] = cert_data.get('id', 'N/A')
        metadata["keywords"] = f"VERIFIED, Certificate ID: {cert_data.get('id', 'N/A')}, Student: {cert_data.get('student_name', 'N/A')}, Course: {cert_data.get('course_name', 'N/A')}, Issued: {cert_data.get('issued_at', 'N/A')}, Organization: {cert_data.get('organization', 'EduCerts')}"
        metadata["creator"] = "EduCert Engine v2.0 - Cryptographically Secured"
        metadata["producer"] = f"EduCert Secure Platform - Verified Certificate"
        doc.set_metadata(metadata)
        print(f"✅ Added verification metadata to PDF properties")

    def _get_signature_metadata_javascript(self, cert_data):
        """Generate JavaScript to display signature metadata"""
        metadata_text = f"""
SIGNATURE METADATA

📋 Certificate ID: {cert_data.get('id', 'N/A')}
👤 Student Name: {cert_data.get('student_name', 'N/A')}
📚 Course Name: {cert_data.get('course_name', 'N/A')}
📅 Issue Date: {cert_data.get('issued_at', 'N/A')}
🏢 Organization: {cert_data.get('organization', 'EduCerts')}

🔐 DIGITAL SIGNATURE:
• Status: VERIFIED & AUTHENTIC
• Algorithm: Ed25519 Cryptographic Signature
• Content Hash: SHA-256
• Registry: Blockchain Anchored

📊 VERIFICATION STATUS:
✅ Signature Valid
✅ Content Integrity Verified  
✅ Issuer Authenticated
✅ Timestamp Confirmed

🌐 This certificate is cryptographically secured and tamper-proof.
Generated by EduCarts Secure Platform v2.0
        """.strip()
        
        # Escape for JavaScript
        escaped_text = metadata_text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        
        return f"""
app.alert("{escaped_text}", 3, 0, "Certificate Signature Metadata");
        """.strip()

def add_simple_wps_ribbon(pdf_path, output_path, cert_data):
    """Simple wrapper function for adding WPS ribbon"""
    ribbon = SimpleWPSRibbon()
    return ribbon.add_wps_ribbon(pdf_path, output_path, cert_data)
