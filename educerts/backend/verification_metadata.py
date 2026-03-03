"""
Verification Metadata Management

This module defines the structure and serialization for certificate verification data
that gets embedded in PDF ribbons and displayed in popups.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import hashlib


@dataclass
class SignatureDetails:
    """Details about cryptographic signature verification."""
    valid: bool
    algorithm: str
    public_key: str
    timestamp: str
    signature_value: Optional[str] = None


@dataclass
class ContentIntegrityDetails:
    """Details about PDF content hash verification."""
    hash_valid: bool
    algorithm: str
    expected_hash: Optional[str]
    computed_hash: Optional[str]
    tamper_detected: bool = False


@dataclass
class RegistryDetails:
    """Details about document registry verification."""
    valid: bool
    merkle_root: str
    document_store: str
    anchored_at: Optional[str] = None
    revoked: bool = False


@dataclass
class IssuerDetails:
    """Details about certificate issuer verification."""
    name: str
    verified: bool
    identity_proof: str
    organization: Optional[str] = None
    url: Optional[str] = None


@dataclass
class CertificateMetadata:
    """Basic certificate information."""
    certificate_id: str
    student_name: str
    course_name: str
    cert_type: str
    issued_date: str
    organization: str
    template_version: Optional[str] = "1.0"


@dataclass
class VerificationMetadata:
    """
    Complete verification metadata structure for PDF ribbons.
    This contains all information needed for verification display.
    """
    # Overall verification status
    is_verified: bool
    verification_timestamp: str
    
    # Certificate details
    certificate: CertificateMetadata
    
    # Verification components
    signature: SignatureDetails
    content_integrity: ContentIntegrityDetails
    registry: RegistryDetails
    issuer: IssuerDetails
    
    # Additional metadata
    verification_url: str
    ribbon_version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self, indent: Optional[int] = None) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationMetadata':
        """Create instance from dictionary."""
        # Handle nested dataclasses
        certificate_data = data.get('certificate', {})
        signature_data = data.get('signature', {})
        content_integrity_data = data.get('content_integrity', {})
        registry_data = data.get('registry', {})
        issuer_data = data.get('issuer', {})
        
        return cls(
            is_verified=data.get('is_verified', False),
            verification_timestamp=data.get('verification_timestamp', ''),
            certificate=CertificateMetadata(**certificate_data),
            signature=SignatureDetails(**signature_data),
            content_integrity=ContentIntegrityDetails(**content_integrity_data),
            registry=RegistryDetails(**registry_data),
            issuer=IssuerDetails(**issuer_data),
            verification_url=data.get('verification_url', ''),
            ribbon_version=data.get('ribbon_version', '1.0')
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'VerificationMetadata':
        """Create instance from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def get_verification_summary(self) -> Dict[str, bool]:
        """Get summary of all verification checks."""
        return {
            "signature_valid": self.signature.valid,
            "content_integrity": self.content_integrity.hash_valid,
            "registry_valid": self.registry.valid,
            "issuer_verified": self.issuer.verified,
            "not_revoked": not self.registry.revoked,
            "overall_valid": self.is_verified
        }
    
    def get_display_status(self) -> str:
        """Get human-readable verification status."""
        if self.is_verified:
            return "VERIFIED"
        elif self.content_integrity.tamper_detected:
            return "TAMPERED"
        elif self.registry.revoked:
            return "REVOKED"
        else:
            return "UNVERIFIED"
    
    def get_status_color(self) -> str:
        """Get color code for verification status."""
        if self.is_verified:
            return "#2563eb"  # Blue
        elif self.content_integrity.tamper_detected:
            return "#dc2626"  # Red
        elif self.registry.revoked:
            return "#ea580c"  # Orange
        else:
            return "#6b7280"  # Gray


class VerificationMetadataBuilder:
    """
    Builder class for constructing VerificationMetadata from various sources.
    """
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to initial state."""
        self._is_verified = False
        self._certificate = None
        self._signature = None
        self._content_integrity = None
        self._registry = None
        self._issuer = None
        self._verification_url = ""
    
    def from_certificate_and_verification(
        self, 
        cert_data: Dict[str, Any], 
        verification_result: Dict[str, Any],
        verification_url: str = ""
    ) -> 'VerificationMetadata':
        """
        Build metadata from certificate data and verification results.
        
        Args:
            cert_data: Certificate information from database
            verification_result: Results from verification API
            verification_url: URL for online verification
            
        Returns:
            VerificationMetadata: Complete verification metadata
        """
        # Extract certificate metadata
        self._certificate = CertificateMetadata(
            certificate_id=cert_data.get('id', ''),
            student_name=cert_data.get('student_name', ''),
            course_name=cert_data.get('course_name', ''),
            cert_type=cert_data.get('cert_type', 'certificate'),
            issued_date=cert_data.get('issued_at', ''),
            organization=cert_data.get('organization', 'EduCerts Academy')
        )
        
        # Extract verification results
        summary = verification_result.get('summary', {})
        data_items = verification_result.get('data', [])
        
        # Build signature details
        signature_item = next((item for item in data_items if item['type'] == 'SIGNATURE_CHECK'), {})
        self._signature = SignatureDetails(
            valid=signature_item.get('status') == 'VALID',
            algorithm="Ed25519",
            public_key=cert_data.get('signature', '')[:50] + "..." if cert_data.get('signature') else '',
            timestamp=cert_data.get('issued_at', ''),
            signature_value=cert_data.get('signature', '')[:20] + "..." if cert_data.get('signature') else ''
        )
        
        # Build content integrity details
        content_item = next((item for item in data_items if item['type'] == 'CONTENT_INTEGRITY'), {})
        content_data = content_item.get('data', {})
        self._content_integrity = ContentIntegrityDetails(
            hash_valid=content_item.get('status') == 'VALID',
            algorithm="SHA-256",
            expected_hash=content_data.get('expected', ''),
            computed_hash=content_data.get('computed', ''),
            tamper_detected=content_item.get('status') == 'INVALID'
        )
        
        # Build registry details
        registry_item = next((item for item in data_items if item['type'] == 'REGISTRY_CHECK'), {})
        self._registry = RegistryDetails(
            valid=registry_item.get('status') == 'VALID',
            merkle_root=cert_data.get('data_payload', {}).get('signature', {}).get('merkleRoot', ''),
            document_store="0x007d40224f6562461633ccfbaffd359ebb2fc9ba",
            anchored_at=cert_data.get('issued_at', ''),
            revoked=cert_data.get('revoked', False)
        )
        
        # Build issuer details
        issuer_item = next((item for item in data_items if item['type'] == 'ISSUER_IDENTITY'), {})
        issuer_data = issuer_item.get('data', {})
        self._issuer = IssuerDetails(
            name=issuer_data.get('name', cert_data.get('organization', 'EduCerts Academy')),
            verified=issuer_item.get('status') == 'VALID',
            identity_proof="DNS-TXT",
            organization=cert_data.get('organization', 'EduCerts Academy'),
            url="https://educerts.io"
        )
        
        # Set overall verification status
        self._is_verified = summary.get('all', False)
        self._verification_url = verification_url
        
        return VerificationMetadata(
            is_verified=self._is_verified,
            verification_timestamp=datetime.now().isoformat(),
            certificate=self._certificate,
            signature=self._signature,
            content_integrity=self._content_integrity,
            registry=self._registry,
            issuer=self._issuer,
            verification_url=self._verification_url
        )
    
    def from_certificate_only(self, cert_data: Dict[str, Any]) -> 'VerificationMetadata':
        """
        Build basic metadata from certificate data only (for newly issued certificates).
        
        Args:
            cert_data: Certificate information from database
            
        Returns:
            VerificationMetadata: Basic verification metadata
        """
        certificate = CertificateMetadata(
            certificate_id=cert_data.get('id', ''),
            student_name=cert_data.get('student_name', ''),
            course_name=cert_data.get('course_name', ''),
            cert_type=cert_data.get('cert_type', 'certificate'),
            issued_date=cert_data.get('issued_at', ''),
            organization=cert_data.get('organization', 'EduCerts Academy')
        )
        
        signature = SignatureDetails(
            valid=True,  # Assume valid for newly issued
            algorithm="Ed25519",
            public_key=cert_data.get('signature', '')[:50] + "..." if cert_data.get('signature') else '',
            timestamp=cert_data.get('issued_at', ''),
            signature_value=cert_data.get('signature', '')[:20] + "..." if cert_data.get('signature') else ''
        )
        
        content_integrity = ContentIntegrityDetails(
            hash_valid=bool(cert_data.get('content_hash')),
            algorithm="SHA-256",
            expected_hash=cert_data.get('content_hash', ''),
            computed_hash=cert_data.get('content_hash', ''),
            tamper_detected=False
        )
        
        registry = RegistryDetails(
            valid=True,  # Assume valid for newly issued
            merkle_root=cert_data.get('data_payload', {}).get('signature', {}).get('merkleRoot', ''),
            document_store="0x007d40224f6562461633ccfbaffd359ebb2fc9ba",
            anchored_at=cert_data.get('issued_at', ''),
            revoked=cert_data.get('revoked', False)
        )
        
        issuer = IssuerDetails(
            name=cert_data.get('organization', 'EduCerts Academy'),
            verified=True,  # Assume verified for newly issued
            identity_proof="DNS-TXT",
            organization=cert_data.get('organization', 'EduCerts Academy'),
            url="https://educerts.io"
        )
        
        return VerificationMetadata(
            is_verified=True,  # Assume verified for newly issued
            verification_timestamp=datetime.now().isoformat(),
            certificate=certificate,
            signature=signature,
            content_integrity=content_integrity,
            registry=registry,
            issuer=issuer,
            verification_url=f"https://educerts.io/verify?id={cert_data.get('id', '')}"
        )


def validate_metadata_schema(data: Dict[str, Any]) -> bool:
    """
    Validate that a dictionary conforms to the VerificationMetadata schema.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        'is_verified', 'verification_timestamp', 'certificate', 
        'signature', 'content_integrity', 'registry', 'issuer', 'verification_url'
    ]
    
    try:
        # Check top-level fields
        for field in required_fields:
            if field not in data:
                return False
        
        # Check nested structures
        cert_fields = ['certificate_id', 'student_name', 'course_name', 'cert_type', 'issued_date', 'organization']
        for field in cert_fields:
            if field not in data['certificate']:
                return False
        
        sig_fields = ['valid', 'algorithm', 'public_key', 'timestamp']
        for field in sig_fields:
            if field not in data['signature']:
                return False
        
        return True
        
    except (KeyError, TypeError):
        return False


def create_sample_metadata() -> VerificationMetadata:
    """Create sample verification metadata for testing."""
    return VerificationMetadata(
        is_verified=True,
        verification_timestamp=datetime.now().isoformat(),
        certificate=CertificateMetadata(
            certificate_id="abc123-def456-ghi789",
            student_name="John Doe",
            course_name="Computer Science Fundamentals",
            cert_type="certificate",
            issued_date="2024-03-15",
            organization="EduCerts Academy"
        ),
        signature=SignatureDetails(
            valid=True,
            algorithm="Ed25519",
            public_key="ed25519_public_key_sample...",
            timestamp="2024-03-15T10:30:00Z",
            signature_value="signature_sample..."
        ),
        content_integrity=ContentIntegrityDetails(
            hash_valid=True,
            algorithm="SHA-256",
            expected_hash="sha256_hash_sample...",
            computed_hash="sha256_hash_sample...",
            tamper_detected=False
        ),
        registry=RegistryDetails(
            valid=True,
            merkle_root="merkle_root_sample...",
            document_store="0x007d40224f6562461633ccfbaffd359ebb2fc9ba",
            anchored_at="2024-03-15T10:30:00Z",
            revoked=False
        ),
        issuer=IssuerDetails(
            name="EduCerts Academy (Verified)",
            verified=True,
            identity_proof="DNS-TXT",
            organization="EduCerts Academy",
            url="https://educerts.io"
        ),
        verification_url="https://educerts.io/verify?id=abc123-def456-ghi789"
    )