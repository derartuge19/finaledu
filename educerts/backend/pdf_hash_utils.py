

import hashlib
import re
import fitz  # PyMuPDF
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_pdf_text(text: str) -> str:
    """
    Normalizes PDF text for consistent hashing.
    
    This ensures that PDFs with identical content but different formatting
    (whitespace, line endings) produce identical hashes.
    
    Args:
        text: Raw text extracted from PDF
        
    Returns:
        Normalized text string
        
    Normalization steps:
    - Strips leading/trailing whitespace
    - Normalizes line endings to \\n
    - Collapses multiple spaces to single space
    - Removes carriage returns
    """
    if not text:
        return ""
    
    # Normalize line endings to \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapse multiple spaces to single space
    text = re.sub(r' +', ' ', text)
    
    # Collapse multiple newlines to single newline
    text = re.sub(r'\n+', '\n', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def compute_pdf_content_hash(pdf_path: str) -> str:
    """
    Computes SHA-256 hash of PDF text content.
    
    This function extracts text from all pages of a PDF, normalizes it,
    and computes a cryptographic hash. The hash can be used to detect
    any tampering with the PDF content.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Hex string of SHA-256 hash (64 characters)
        
    Raises:
        ValueError: If PDF cannot be read or parsed
        FileNotFoundError: If PDF file doesn't exist
        
    Example:
        >>> hash_val = compute_pdf_content_hash("certificate.pdf")
        >>> print(hash_val)
        'a3f5b8c9d2e1f4a7b6c5d8e9f2a1b4c7d6e5f8a9b2c1d4e7f6a5b8c9d2e1f4a7'
    """
    try:
        # Open PDF document
        doc = fitz.open(pdf_path)
        
        # Extract text from all pages
        all_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            all_text += page_text
        
        doc.close()
        
        # Normalize text for consistent hashing
        normalized_text = normalize_pdf_text(all_text)
        
        # Compute SHA-256 hash
        hash_obj = hashlib.sha256(normalized_text.encode('utf-8'))
        content_hash = hash_obj.hexdigest()
        
        logger.info(f"Computed content hash for {pdf_path}: {content_hash[:8]}...")
        
        return content_hash
        
    except FileNotFoundError:
        logger.error(f"PDF file not found: {pdf_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to compute hash for {pdf_path}: {e}")
        raise ValueError(f"Cannot compute PDF hash: {e}")


def embed_hash_in_pdf_metadata(pdf_path: str, content_hash: str, cert_id: str) -> None:
    """
    Embeds content hash and cert ID in PDF metadata.
    
    This allows offline verification by embedding the hash directly in the PDF.
    Since PyMuPDF only supports standard PDF metadata fields, we embed:
    - content_hash in the 'keywords' field
    - cert_id in the 'subject' field
    
    Args:
        pdf_path: Path to the PDF file (will be modified in place)
        content_hash: SHA-256 hash to embed
        cert_id: Certificate UUID
        
    Raises:
        ValueError: If PDF cannot be opened or modified
        
    Note:
        This function modifies the PDF file in place. The original file is overwritten.
    """
    try:
        doc = fitz.open(pdf_path)
        
        # Get current metadata
        metadata = doc.metadata
        
        # Embed content hash in keywords field (standard PDF metadata)
        # Format: "content_hash:<hash>"
        metadata['keywords'] = f"content_hash:{content_hash}"
        
        # Embed cert ID in subject field (standard PDF metadata)
        metadata['subject'] = cert_id
        
        # Add producer and creator info
        metadata['producer'] = "EduCert Secure Verification System"
        metadata['creator'] = "EduCert Engine v2.0"
        
        # Set the metadata
        doc.set_metadata(metadata)
        
        # Save changes (incremental save to preserve existing content)
        doc.saveIncr()
        doc.close()
        
        logger.info(f"Embedded hash {content_hash[:8]}... in {pdf_path}")
        
    except Exception as e:
        logger.error(f"Failed to embed hash in {pdf_path}: {e}")
        raise ValueError(f"Cannot embed hash in PDF metadata: {e}")


def extract_hash_from_pdf_metadata(pdf_path: str) -> Dict[str, Optional[str]]:
    """
    Extracts embedded hash and cert ID from PDF metadata.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Dict with keys:
        - 'content_hash': SHA-256 hash (or None if not found)
        - 'cert_id': Certificate UUID (or None if not found)
        
    Raises:
        ValueError: If PDF cannot be opened
        
    Example:
        >>> metadata = extract_hash_from_pdf_metadata("certificate.pdf")
        >>> print(metadata['content_hash'])
        'a3f5b8c9d2e1f4a7b6c5d8e9f2a1b4c7d6e5f8a9b2c1d4e7f6a5b8c9d2e1f4a7'
        >>> print(metadata['cert_id'])
        '550e8400-e29b-41d4-a716-446655440000'
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        # Extract content hash from keywords field
        # Format: "content_hash:<hash>"
        content_hash = None
        keywords = metadata.get('keywords', '')
        if keywords and keywords.startswith('content_hash:'):
            content_hash = keywords.replace('content_hash:', '')
        
        # Extract cert ID from subject field
        cert_id = metadata.get('subject')
        
        result = {
            'content_hash': content_hash,
            'cert_id': cert_id
        }
        
        logger.info(f"Extracted metadata from {pdf_path}: hash={content_hash[:8] if content_hash else 'None'}..., cert_id={cert_id[:8] if cert_id else 'None'}...")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to extract metadata from {pdf_path}: {e}")
        raise ValueError(f"Cannot extract metadata from PDF: {e}")


def verify_pdf_content_hash(pdf_path: str, expected_hash: str) -> bool:
    """
    Verifies that a PDF's content matches the expected hash.
    
    This is a convenience function that computes the hash and compares it
    to the expected value.
    
    Args:
        pdf_path: Path to the PDF file
        expected_hash: Expected SHA-256 hash
        
    Returns:
        True if hashes match, False otherwise
        
    Example:
        >>> is_valid = verify_pdf_content_hash("cert.pdf", "a3f5b8c9...")
        >>> if is_valid:
        ...     print("Certificate is authentic")
        ... else:
        ...     print("Certificate has been tampered with!")
    """
    try:
        computed_hash = compute_pdf_content_hash(pdf_path)
        matches = (computed_hash == expected_hash)
        
        if matches:
            logger.info(f"Hash verification PASSED for {pdf_path}")
        else:
            logger.warning(f"Hash verification FAILED for {pdf_path}")
            logger.warning(f"  Expected: {expected_hash}")
            logger.warning(f"  Computed: {computed_hash}")
        
        return matches
        
    except Exception as e:
        logger.error(f"Hash verification error for {pdf_path}: {e}")
        return False
