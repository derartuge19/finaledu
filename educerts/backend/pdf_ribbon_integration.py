"""
PDF Ribbon Integration

This module provides integration functions to add verification ribbons
to signed PDF certificates within the existing signing workflow.
"""

import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from pdf_ribbon_utils import VerificationRibbon, embed_ribbon_in_pdf
from verification_metadata import VerificationMetadata, VerificationMetadataBuilder
from ribbon_styling import RibbonStyle, RibbonStylePresets, create_status_aware_style
from ribbon_error_handling import RibbonErrorHandler, safe_ribbon_embed
import models
import schemas


def add_ribbon_to_signed_certificate(
    cert: models.Certificate,
    signed_pdf_path: str,
    db: Session,
    styling: Optional[RibbonStyle] = None
) -> tuple[bool, str]:
    """
    Add interactive verification ribbon to a signed certificate PDF.
    
    Args:
        cert: Certificate database object
        signed_pdf_path: Path to the signed PDF file
        db: Database session
        styling: Optional custom styling (uses default if None)
        
    Returns:
        tuple[bool, str]: (success, output_path)
    """
    try:
        # Generate output path for ribbon-enhanced PDF
        cert_id = cert.id
        ribbon_output_path = signed_pdf_path.replace("_signed.pdf", "_signed_with_ribbon.pdf")
        
        # Create verification metadata from certificate
        verification_metadata = create_verification_metadata_from_cert(cert, db)
        
        # Use provided styling or create status-aware styling
        if styling is None:
            styling = create_status_aware_style(
                is_verified=True,  # Assume verified for newly signed certificates
                is_tampered=False,
                is_revoked=cert.revoked
            )
        
        # Embed the ribbon
        success = embed_ribbon_in_pdf(
            pdf_path=signed_pdf_path,
            output_path=ribbon_output_path,
            verification_data=verification_metadata,
            styling=styling
        )
        
        if success:
            print(f"✓ Successfully added verification ribbon to certificate {cert_id}")
            return True, ribbon_output_path
        else:
            print(f"✗ Failed to add verification ribbon to certificate {cert_id}")
            return False, signed_pdf_path
            
    except Exception as e:
        print(f"ERROR: Ribbon integration failed for certificate {cert.id}: {e}")
        return False, signed_pdf_path


def add_ribbons_to_batch_certificates(
    certificates: list[models.Certificate],
    signed_pdf_paths: Dict[str, str],
    db: Session,
    styling: Optional[RibbonStyle] = None
) -> Dict[str, tuple[bool, str]]:
    """
    Add verification ribbons to multiple signed certificates.
    
    Args:
        certificates: List of certificate database objects
        signed_pdf_paths: Dictionary mapping cert_id to signed PDF path
        db: Database session
        styling: Optional custom styling
        
    Returns:
        Dict[str, tuple[bool, str]]: Mapping of cert_id to (success, output_path)
    """
    results = {}
    
    for cert in certificates:
        cert_id = cert.id
        signed_pdf_path = signed_pdf_paths.get(cert_id)
        
        if not signed_pdf_path or not os.path.exists(signed_pdf_path):
            results[cert_id] = (False, "")
            continue
        
        success, output_path = add_ribbon_to_signed_certificate(
            cert, signed_pdf_path, db, styling
        )
        results[cert_id] = (success, output_path)
    
    return results


def create_verification_metadata_from_cert(
    cert: models.Certificate, 
    db: Session
) -> VerificationMetadata:
    """
    Create verification metadata from certificate database object.
    
    Args:
        cert: Certificate database object
        db: Database session
        
    Returns:
        VerificationMetadata: Complete verification metadata
    """
    # Convert certificate to dictionary format
    cert_data = {
        'id': cert.id,
        'student_name': cert.student_name,
        'course_name': cert.course_name,
        'cert_type': cert.cert_type,
        'issued_at': cert.issued_at.isoformat() if cert.issued_at else '',
        'organization': cert.organization,
        'signature': cert.signature,
        'content_hash': cert.content_hash,
        'revoked': cert.revoked,
        'data_payload': cert.data_payload or {}
    }
    
    # Use metadata builder to create verification metadata
    builder = VerificationMetadataBuilder()
    
    # For newly signed certificates, we assume they're valid
    # In a real scenario, you might want to run actual verification
    return builder.from_certificate_only(cert_data)


def create_verification_metadata_with_full_verification(
    cert: models.Certificate,
    db: Session
) -> VerificationMetadata:
    """
    Create verification metadata by running full verification process.
    
    Args:
        cert: Certificate database object
        db: Database session
        
    Returns:
        VerificationMetadata: Complete verification metadata with actual verification results
    """
    try:
        # Import verification function (avoiding circular imports)
        from main import verify_certificate
        
        # Create verification request
        verification_request = schemas.VerificationRequest(certificate_id=cert.id)
        
        # Run verification
        verification_result = verify_certificate(verification_request, db)
        
        # Convert certificate to dictionary format
        cert_data = {
            'id': cert.id,
            'student_name': cert.student_name,
            'course_name': cert.course_name,
            'cert_type': cert.cert_type,
            'issued_at': cert.issued_at.isoformat() if cert.issued_at else '',
            'organization': cert.organization,
            'signature': cert.signature,
            'content_hash': cert.content_hash,
            'revoked': cert.revoked,
            'data_payload': cert.data_payload or {}
        }
        
        # Use metadata builder with verification results
        builder = VerificationMetadataBuilder()
        verification_url = f"https://educerts.io/verify?id={cert.id}"
        
        return builder.from_certificate_and_verification(
            cert_data, verification_result, verification_url
        )
        
    except Exception as e:
        print(f"WARNING: Full verification failed for {cert.id}, using basic metadata: {e}")
        return create_verification_metadata_from_cert(cert, db)


def update_certificate_with_ribbon_path(
    cert: models.Certificate,
    ribbon_pdf_path: str,
    db: Session
) -> bool:
    """
    Update certificate database record with ribbon-enhanced PDF path.
    
    Args:
        cert: Certificate database object
        ribbon_pdf_path: Path to ribbon-enhanced PDF
        db: Database session
        
    Returns:
        bool: True if update was successful
    """
    try:
        cert.rendered_pdf_path = ribbon_pdf_path
        db.commit()
        return True
    except Exception as e:
        print(f"ERROR: Failed to update certificate {cert.id} with ribbon path: {e}")
        db.rollback()
        return False


def safe_add_ribbon_to_certificate(
    cert: models.Certificate,
    signed_pdf_path: str,
    db: Session,
    styling: Optional[RibbonStyle] = None,
    use_full_verification: bool = False
) -> tuple[bool, str]:
    """
    Safely add verification ribbon with comprehensive error handling.
    
    Args:
        cert: Certificate database object
        signed_pdf_path: Path to signed PDF
        db: Database session
        styling: Optional custom styling
        use_full_verification: Whether to run full verification (slower but more accurate)
        
    Returns:
        tuple[bool, str]: (success, final_pdf_path)
    """
    error_handler = RibbonErrorHandler(enable_logging=True)
    
    def ribbon_embed_function(input_path: str, output_path: str) -> bool:
        """Inner function for ribbon embedding."""
        # Create verification metadata
        if use_full_verification:
            verification_metadata = create_verification_metadata_with_full_verification(cert, db)
        else:
            verification_metadata = create_verification_metadata_from_cert(cert, db)
        
        # Use provided styling or create status-aware styling
        if styling is None:
            ribbon_styling = create_status_aware_style(
                is_verified=not cert.revoked,
                is_tampered=False,
                is_revoked=cert.revoked
            )
        else:
            ribbon_styling = styling
        
        # Create and embed ribbon
        ribbon = VerificationRibbon(verification_metadata, ribbon_styling)
        return ribbon.embed_ribbon(input_path, output_path)
    
    # Generate output path
    ribbon_output_path = signed_pdf_path.replace("_signed.pdf", "_signed_with_ribbon.pdf")
    
    # Use safe embedding with error handling
    success = safe_ribbon_embed(
        pdf_path=signed_pdf_path,
        output_path=ribbon_output_path,
        embed_function=ribbon_embed_function,
        error_handler=error_handler
    )
    
    if success:
        # Update certificate record
        update_success = update_certificate_with_ribbon_path(cert, ribbon_output_path, db)
        if update_success:
            return True, ribbon_output_path
        else:
            print(f"WARNING: Ribbon added but failed to update database for {cert.id}")
            return True, ribbon_output_path
    else:
        print(f"ERROR: Failed to add ribbon to certificate {cert.id}")
        return False, signed_pdf_path


def get_ribbon_styling_for_certificate(cert: models.Certificate) -> RibbonStyle:
    """
    Get appropriate ribbon styling based on certificate properties.
    
    Args:
        cert: Certificate database object
        
    Returns:
        RibbonStyle: Appropriate styling configuration
    """
    # Determine verification status
    is_verified = not cert.revoked and cert.signing_status == "signed"
    is_tampered = False  # Would need content hash verification
    is_revoked = cert.revoked
    
    # Create status-aware styling
    styling = create_status_aware_style(is_verified, is_tampered, is_revoked)
    
    # Customize based on certificate type or organization
    if cert.cert_type == "diploma":
        styling.height = 35  # Larger ribbon for diplomas
        styling.font_size = 14
    elif cert.cert_type == "certificate":
        styling.height = 30  # Standard size
        styling.font_size = 12
    else:
        styling.height = 25  # Compact for other types
        styling.font_size = 10
    
    # Customize logo text based on organization
    if cert.organization:
        styling.logo_text = cert.organization
    
    return styling


def batch_add_ribbons_with_progress(
    certificates: list[models.Certificate],
    signed_pdf_paths: Dict[str, str],
    db: Session,
    progress_callback: Optional[callable] = None
) -> Dict[str, tuple[bool, str]]:
    """
    Add ribbons to multiple certificates with progress tracking.
    
    Args:
        certificates: List of certificates
        signed_pdf_paths: Dictionary of cert_id to PDF path
        db: Database session
        progress_callback: Optional callback function for progress updates
        
    Returns:
        Dict[str, tuple[bool, str]]: Results mapping
    """
    results = {}
    total_certs = len(certificates)
    
    for i, cert in enumerate(certificates):
        cert_id = cert.id
        signed_pdf_path = signed_pdf_paths.get(cert_id)
        
        if progress_callback:
            progress_callback(i, total_certs, cert_id)
        
        if not signed_pdf_path or not os.path.exists(signed_pdf_path):
            results[cert_id] = (False, "")
            continue
        
        # Get appropriate styling for this certificate
        styling = get_ribbon_styling_for_certificate(cert)
        
        # Add ribbon safely
        success, output_path = safe_add_ribbon_to_certificate(
            cert, signed_pdf_path, db, styling
        )
        
        results[cert_id] = (success, output_path)
    
    if progress_callback:
        progress_callback(total_certs, total_certs, "Complete")
    
    return results