"""
PDF JavaScript Templates

This module generates JavaScript code for interactive PDF verification ribbons.
The JavaScript handles popup display, user interactions, and verification data presentation.
"""

from typing import Dict, Any
from verification_metadata import VerificationMetadata
from ribbon_styling import RibbonStyle


class JavaScriptTemplates:
    """
    Generates JavaScript code for PDF verification ribbon interactivity.
    """
    
    def generate_popup_javascript(self, verification_data: VerificationMetadata) -> str:
        """
        Generate complete JavaScript code for verification popup functionality.
        
        Args:
            verification_data: Verification metadata to display
            
        Returns:
            str: JavaScript code for embedding in PDF
        """
        # Convert verification data to JavaScript object
        js_data = self._convert_to_js_object(verification_data)
        
        # Generate the complete JavaScript
        javascript_code = f"""
// EduCerts Verification Ribbon JavaScript
// Version 1.0

// Verification data embedded in PDF
var verificationData = {js_data};

// Global popup state
var popupVisible = false;
var popupElement = null;

// Main function to show verification popup
function showVerificationPopup() {{
    try {{
        if (popupVisible) {{
            hideVerificationPopup();
            return;
        }}
        
        createVerificationPopup();
        showPopup();
        popupVisible = true;
        
        // Log interaction for analytics
        console.log('EduCerts: Verification popup displayed');
        
    }} catch (error) {{
        console.error('EduCerts: Error showing popup:', error);
        // Fallback to alert if popup fails
        showFallbackAlert();
    }}
}}

// Create the popup HTML structure
function createVerificationPopup() {{
    var popupHtml = generatePopupHTML();
    
    // Create popup container
    popupElement = document.createElement('div');
    popupElement.id = 'educerts-verification-popup';
    popupElement.innerHTML = popupHtml;
    
    // Add popup styles
    addPopupStyles();
    
    // Add to document
    document.body.appendChild(popupElement);
    
    // Add event listeners
    addPopupEventListeners();
}}

// Generate HTML content for popup
function generatePopupHTML() {{
    var statusIcon = verificationData.is_verified ? '🔒' : '⚠️';
    var statusText = verificationData.is_verified ? 'VERIFIED' : 'UNVERIFIED';
    var statusColor = verificationData.is_verified ? '#2563eb' : '#dc2626';
    
    return `
    <div class="popup-overlay" onclick="hideVerificationPopup()">
        <div class="popup-content" onclick="event.stopPropagation()">
            <div class="popup-header">
                <div class="status-badge" style="background-color: ${{statusColor}}">
                    ${{statusIcon}} ${{statusText}}
                </div>
                <button class="close-button" onclick="hideVerificationPopup()">×</button>
            </div>
            
            <div class="popup-body">
                <div class="certificate-info">
                    <h3>${{verificationData.certificate.student_name}}</h3>
                    <p>${{verificationData.certificate.course_name}}</p>
                    <p class="cert-id">ID: ${{verificationData.certificate.certificate_id}}</p>
                </div>
                
                <div class="verification-details">
                    <div class="detail-section">
                        <h4>Cryptographic Verification</h4>
                        <div class="detail-item">
                            <span class="label">Digital Signature:</span>
                            <span class="value ${{verificationData.signature.valid ? 'valid' : 'invalid'}}">
                                ${{verificationData.signature.valid ? '✓ Valid' : '✗ Invalid'}}
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Content Integrity:</span>
                            <span class="value ${{verificationData.content_integrity.hash_valid ? 'valid' : 'invalid'}}">
                                ${{verificationData.content_integrity.hash_valid ? '✓ Valid' : '✗ Invalid'}}
                            </span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Registry Status:</span>
                            <span class="value ${{verificationData.registry.valid ? 'valid' : 'invalid'}}">
                                ${{verificationData.registry.valid ? '✓ Valid' : '✗ Invalid'}}
                            </span>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h4>Issuer Information</h4>
                        <div class="detail-item">
                            <span class="label">Organization:</span>
                            <span class="value">${{verificationData.issuer.name}}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Identity Proof:</span>
                            <span class="value">${{verificationData.issuer.identity_proof}}</span>
                        </div>
                        <div class="detail-item">
                            <span class="label">Issued Date:</span>
                            <span class="value">${{verificationData.certificate.issued_date}}</span>
                        </div>
                    </div>
                </div>
                
                <div class="popup-footer">
                    <a href="${{verificationData.verification_url}}" target="_blank" class="verify-online-btn">
                        Verify Online
                    </a>
                    <span class="timestamp">
                        Verified: ${{new Date(verificationData.verification_timestamp).toLocaleString()}}
                    </span>
                </div>
            </div>
        </div>
    </div>
    `;
}}

// Add CSS styles for popup
function addPopupStyles() {{
    var styleElement = document.createElement('style');
    styleElement.textContent = `
        #educerts-verification-popup {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .popup-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .popup-content {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            animation: popupSlideIn 0.3s ease-out;
        }}
        
        @keyframes popupSlideIn {{
            from {{
                opacity: 0;
                transform: translateY(-20px) scale(0.95);
            }}
            to {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}
        
        .popup-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px 16px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .status-badge {{
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .close-button {{
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
            padding: 4px;
            border-radius: 4px;
        }}
        
        .close-button:hover {{
            background-color: #f3f4f6;
        }}
        
        .popup-body {{
            padding: 20px 24px;
        }}
        
        .certificate-info {{
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .certificate-info h3 {{
            margin: 0 0 8px 0;
            font-size: 20px;
            font-weight: bold;
            color: #111827;
        }}
        
        .certificate-info p {{
            margin: 4px 0;
            color: #6b7280;
        }}
        
        .cert-id {{
            font-family: monospace;
            font-size: 12px;
            background-color: #f3f4f6;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 8px;
        }}
        
        .verification-details {{
            margin-bottom: 20px;
        }}
        
        .detail-section {{
            margin-bottom: 20px;
        }}
        
        .detail-section h4 {{
            margin: 0 0 12px 0;
            font-size: 16px;
            font-weight: 600;
            color: #111827;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .detail-item:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-weight: 500;
            color: #374151;
        }}
        
        .value {{
            font-weight: 600;
        }}
        
        .value.valid {{
            color: #059669;
        }}
        
        .value.invalid {{
            color: #dc2626;
        }}
        
        .popup-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .verify-online-btn {{
            background-color: #2563eb;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
        }}
        
        .verify-online-btn:hover {{
            background-color: #1d4ed8;
        }}
        
        .timestamp {{
            font-size: 12px;
            color: #6b7280;
        }}
    `;
    
    document.head.appendChild(styleElement);
}}

// Add event listeners for popup interactions
function addPopupEventListeners() {{
    // Close on Escape key
    document.addEventListener('keydown', function(event) {{
        if (event.key === 'Escape' && popupVisible) {{
            hideVerificationPopup();
        }}
    }});
}}

// Show the popup with animation
function showPopup() {{
    if (popupElement) {{
        popupElement.style.display = 'block';
        // Force reflow for animation
        popupElement.offsetHeight;
        popupElement.style.opacity = '1';
    }}
}}

// Hide verification popup
function hideVerificationPopup() {{
    try {{
        if (popupElement) {{
            popupElement.style.opacity = '0';
            setTimeout(function() {{
                if (popupElement && popupElement.parentNode) {{
                    popupElement.parentNode.removeChild(popupElement);
                }}
                popupElement = null;
                popupVisible = false;
            }}, 200);
        }}
    }} catch (error) {{
        console.error('EduCerts: Error hiding popup:', error);
        popupVisible = false;
    }}
}}

// Fallback alert for when popup fails
function showFallbackAlert() {{
    var message = 'Certificate Verification\\n\\n';
    message += 'Status: ' + (verificationData.is_verified ? 'VERIFIED' : 'UNVERIFIED') + '\\n';
    message += 'Student: ' + verificationData.certificate.student_name + '\\n';
    message += 'Course: ' + verificationData.certificate.course_name + '\\n';
    message += 'ID: ' + verificationData.certificate.certificate_id + '\\n\\n';
    message += 'Signature: ' + (verificationData.signature.valid ? 'Valid' : 'Invalid') + '\\n';
    message += 'Content: ' + (verificationData.content_integrity.hash_valid ? 'Valid' : 'Invalid') + '\\n';
    message += 'Registry: ' + (verificationData.registry.valid ? 'Valid' : 'Invalid') + '\\n\\n';
    message += 'Verify online: ' + verificationData.verification_url;
    
    alert(message);
}}

// Initialize ribbon functionality when PDF loads
function initializeRibbon() {{
    console.log('EduCerts: Verification ribbon initialized');
    
    // Add global click handler for ribbon
    if (typeof this.print !== 'undefined') {{
        // We're in a PDF context
        console.log('EduCerts: PDF context detected');
    }}
}}

// Auto-initialize when script loads
try {{
    initializeRibbon();
}} catch (error) {{
    console.error('EduCerts: Initialization error:', error);
}}
"""
        
        return javascript_code
    
    def _convert_to_js_object(self, verification_data: VerificationMetadata) -> str:
        """
        Convert VerificationMetadata to JavaScript object string.
        
        Args:
            verification_data: Verification metadata
            
        Returns:
            str: JavaScript object representation
        """
        import json
        
        # Convert to dictionary and then to JSON
        data_dict = verification_data.to_dict()
        
        # Convert to JavaScript object (JSON with some modifications)
        js_json = json.dumps(data_dict, indent=2)
        
        return js_json
    
    def generate_popup_html(self, verification_data: VerificationMetadata, styling: RibbonStyle) -> str:
        """
        Generate standalone HTML for verification popup (for testing).
        
        Args:
            verification_data: Verification metadata
            styling: Ribbon styling configuration
            
        Returns:
            str: HTML content for popup
        """
        status_icon = "🔒" if verification_data.is_verified else "⚠️"
        status_text = verification_data.get_display_status()
        status_color = verification_data.get_status_color()
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate Verification</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f9fafb;
        }}
        
        .verification-popup {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: 0 auto;
            overflow: hidden;
        }}
        
        .popup-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 24px 16px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .status-badge {{
            background-color: {status_color};
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .popup-body {{
            padding: 20px 24px;
        }}
        
        .certificate-info {{
            text-align: center;
            margin-bottom: 24px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .certificate-info h3 {{
            margin: 0 0 8px 0;
            font-size: 20px;
            font-weight: bold;
            color: #111827;
        }}
        
        .certificate-info p {{
            margin: 4px 0;
            color: #6b7280;
        }}
        
        .cert-id {{
            font-family: monospace;
            font-size: 12px;
            background-color: #f3f4f6;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
            margin-top: 8px;
        }}
        
        .detail-section {{
            margin-bottom: 20px;
        }}
        
        .detail-section h4 {{
            margin: 0 0 12px 0;
            font-size: 16px;
            font-weight: 600;
            color: #111827;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f3f4f6;
        }}
        
        .detail-item:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-weight: 500;
            color: #374151;
        }}
        
        .value {{
            font-weight: 600;
        }}
        
        .value.valid {{
            color: #059669;
        }}
        
        .value.invalid {{
            color: #dc2626;
        }}
        
        .popup-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .verify-online-btn {{
            background-color: #2563eb;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
        }}
        
        .verify-online-btn:hover {{
            background-color: #1d4ed8;
        }}
        
        .timestamp {{
            font-size: 12px;
            color: #6b7280;
        }}
    </style>
</head>
<body>
    <div class="verification-popup">
        <div class="popup-header">
            <div class="status-badge">
                {status_icon} {status_text}
            </div>
        </div>
        
        <div class="popup-body">
            <div class="certificate-info">
                <h3>{verification_data.certificate.student_name}</h3>
                <p>{verification_data.certificate.course_name}</p>
                <p class="cert-id">ID: {verification_data.certificate.certificate_id}</p>
            </div>
            
            <div class="verification-details">
                <div class="detail-section">
                    <h4>Cryptographic Verification</h4>
                    <div class="detail-item">
                        <span class="label">Digital Signature:</span>
                        <span class="value {'valid' if verification_data.signature.valid else 'invalid'}">
                            {'✓ Valid' if verification_data.signature.valid else '✗ Invalid'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Content Integrity:</span>
                        <span class="value {'valid' if verification_data.content_integrity.hash_valid else 'invalid'}">
                            {'✓ Valid' if verification_data.content_integrity.hash_valid else '✗ Invalid'}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Registry Status:</span>
                        <span class="value {'valid' if verification_data.registry.valid else 'invalid'}">
                            {'✓ Valid' if verification_data.registry.valid else '✗ Invalid'}
                        </span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Issuer Information</h4>
                    <div class="detail-item">
                        <span class="label">Organization:</span>
                        <span class="value">{verification_data.issuer.name}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Identity Proof:</span>
                        <span class="value">{verification_data.issuer.identity_proof}</span>
                    </div>
                    <div class="detail-item">
                        <span class="label">Issued Date:</span>
                        <span class="value">{verification_data.certificate.issued_date}</span>
                    </div>
                </div>
            </div>
            
            <div class="popup-footer">
                <a href="{verification_data.verification_url}" target="_blank" class="verify-online-btn">
                    Verify Online
                </a>
                <span class="timestamp">
                    Verified: {verification_data.verification_timestamp}
                </span>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def generate_minimal_javascript(self, verification_data: VerificationMetadata) -> str:
        """
        Generate minimal JavaScript for basic popup functionality.
        Used when full JavaScript fails or for compatibility.
        
        Args:
            verification_data: Verification metadata
            
        Returns:
            str: Minimal JavaScript code
        """
        js_data = self._convert_to_js_object(verification_data)
        
        minimal_js = f"""
// EduCerts Minimal Verification JavaScript
var verificationData = {js_data};

function showVerificationPopup() {{
    var message = 'Certificate Verification\\n\\n';
    message += 'Status: ' + (verificationData.is_verified ? 'VERIFIED' : 'UNVERIFIED') + '\\n';
    message += 'Student: ' + verificationData.certificate.student_name + '\\n';
    message += 'Course: ' + verificationData.certificate.course_name + '\\n';
    message += 'ID: ' + verificationData.certificate.certificate_id + '\\n\\n';
    message += 'Digital Signature: ' + (verificationData.signature.valid ? 'Valid' : 'Invalid') + '\\n';
    message += 'Content Integrity: ' + (verificationData.content_integrity.hash_valid ? 'Valid' : 'Invalid') + '\\n';
    message += 'Registry Status: ' + (verificationData.registry.valid ? 'Valid' : 'Invalid') + '\\n\\n';
    message += 'Issuer: ' + verificationData.issuer.name + '\\n';
    message += 'Issued: ' + verificationData.certificate.issued_date + '\\n\\n';
    message += 'Verify online: ' + verificationData.verification_url;
    
    alert(message);
}}
"""
        
        return minimal_js