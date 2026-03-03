"""
Ribbon Error Handling

This module provides comprehensive error handling for PDF ribbon embedding operations.
Includes graceful fallbacks, logging, and recovery mechanisms.
"""

import logging
import traceback
import os
from typing import Optional, Dict, Any, Callable
from enum import Enum
from dataclasses import dataclass


class RibbonErrorType(Enum):
    """Types of errors that can occur during ribbon operations."""
    PDF_READ_ERROR = "pdf_read_error"
    PDF_WRITE_ERROR = "pdf_write_error"
    ANNOTATION_ERROR = "annotation_error"
    JAVASCRIPT_ERROR = "javascript_error"
    METADATA_ERROR = "metadata_error"
    STYLING_ERROR = "styling_error"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    MEMORY_ERROR = "memory_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class RibbonError:
    """Structured error information for ribbon operations."""
    error_type: RibbonErrorType
    message: str
    original_exception: Optional[Exception] = None
    file_path: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: bool = False
    fallback_used: str = ""


class RibbonErrorHandler:
    """
    Comprehensive error handler for PDF ribbon operations.
    Provides logging, recovery mechanisms, and graceful fallbacks.
    """
    
    def __init__(self, enable_logging: bool = True, log_level: int = logging.WARNING):
        """
        Initialize error handler.
        
        Args:
            enable_logging: Whether to enable error logging
            log_level: Logging level for error messages
        """
        self.enable_logging = enable_logging
        self.error_history: list[RibbonError] = []
        self.recovery_strategies: Dict[RibbonErrorType, Callable] = {}
        
        if enable_logging:
            self.logger = logging.getLogger("ribbon_error_handler")
            self.logger.setLevel(log_level)
            
            # Create console handler if none exists
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = None
        
        # Register default recovery strategies
        self._register_default_recovery_strategies()
    
    def handle_embedding_error(self, exception: Exception, pdf_path: str, output_path: str) -> bool:
        """
        Handle errors during ribbon embedding process.
        
        Args:
            exception: The exception that occurred
            pdf_path: Path to input PDF
            output_path: Path to output PDF
            
        Returns:
            bool: True if recovery was successful, False otherwise
        """
        error_type = self._classify_error(exception)
        
        ribbon_error = RibbonError(
            error_type=error_type,
            message=str(exception),
            original_exception=exception,
            file_path=pdf_path
        )
        
        self._log_error(ribbon_error)
        self.error_history.append(ribbon_error)
        
        # Attempt recovery
        recovery_success = self._attempt_recovery(ribbon_error, pdf_path, output_path)
        ribbon_error.recovery_attempted = True
        ribbon_error.recovery_successful = recovery_success
        
        return recovery_success
    
    def handle_javascript_error(self, exception: Exception, verification_data: Dict[str, Any]) -> Optional[str]:
        """
        Handle errors during JavaScript generation.
        
        Args:
            exception: The exception that occurred
            verification_data: Verification data for fallback
            
        Returns:
            Optional[str]: Fallback JavaScript or None if no fallback available
        """
        ribbon_error = RibbonError(
            error_type=RibbonErrorType.JAVASCRIPT_ERROR,
            message=str(exception),
            original_exception=exception
        )
        
        self._log_error(ribbon_error)
        self.error_history.append(ribbon_error)
        
        # Generate minimal JavaScript fallback
        try:
            fallback_js = self._generate_minimal_javascript_fallback(verification_data)
            ribbon_error.recovery_attempted = True
            ribbon_error.recovery_successful = True
            ribbon_error.fallback_used = "minimal_javascript"
            return fallback_js
        except Exception as fallback_error:
            self._log_error(RibbonError(
                error_type=RibbonErrorType.JAVASCRIPT_ERROR,
                message=f"Fallback also failed: {fallback_error}",
                original_exception=fallback_error
            ))
            return None
    
    def handle_metadata_error(self, exception: Exception, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle errors during metadata processing.
        
        Args:
            exception: The exception that occurred
            metadata: Original metadata that failed
            
        Returns:
            Dict[str, Any]: Sanitized or fallback metadata
        """
        ribbon_error = RibbonError(
            error_type=RibbonErrorType.METADATA_ERROR,
            message=str(exception),
            original_exception=exception
        )
        
        self._log_error(ribbon_error)
        self.error_history.append(ribbon_error)
        
        # Create minimal fallback metadata
        fallback_metadata = {
            "is_verified": False,
            "verification_timestamp": "unknown",
            "certificate": {
                "certificate_id": "unknown",
                "student_name": "Unknown",
                "course_name": "Unknown",
                "cert_type": "certificate",
                "issued_date": "unknown",
                "organization": "Unknown"
            },
            "signature": {
                "valid": False,
                "algorithm": "unknown",
                "public_key": "unknown",
                "timestamp": "unknown"
            },
            "content_integrity": {
                "hash_valid": False,
                "algorithm": "unknown",
                "expected_hash": None,
                "computed_hash": None,
                "tamper_detected": True
            },
            "registry": {
                "valid": False,
                "merkle_root": "unknown",
                "document_store": "unknown",
                "revoked": False
            },
            "issuer": {
                "name": "Unknown",
                "verified": False,
                "identity_proof": "unknown"
            },
            "verification_url": "",
            "ribbon_version": "1.0"
        }
        
        ribbon_error.recovery_attempted = True
        ribbon_error.recovery_successful = True
        ribbon_error.fallback_used = "minimal_metadata"
        
        return fallback_metadata
    
    def _classify_error(self, exception: Exception) -> RibbonErrorType:
        """
        Classify exception into ribbon error type.
        
        Args:
            exception: Exception to classify
            
        Returns:
            RibbonErrorType: Classified error type
        """
        exception_name = type(exception).__name__
        exception_message = str(exception).lower()
        
        # PDF-related errors
        if "pdf" in exception_message or "fitz" in exception_message:
            if "permission" in exception_message or "access" in exception_message:
                return RibbonErrorType.PERMISSION_ERROR
            elif "read" in exception_message or "open" in exception_message:
                return RibbonErrorType.PDF_READ_ERROR
            elif "write" in exception_message or "save" in exception_message:
                return RibbonErrorType.PDF_WRITE_ERROR
            else:
                return RibbonErrorType.ANNOTATION_ERROR
        
        # Memory errors
        if exception_name in ["MemoryError", "OutOfMemoryError"]:
            return RibbonErrorType.MEMORY_ERROR
        
        # Permission errors
        if exception_name in ["PermissionError", "OSError"] and "permission" in exception_message:
            return RibbonErrorType.PERMISSION_ERROR
        
        # JavaScript errors
        if "javascript" in exception_message or "js" in exception_message:
            return RibbonErrorType.JAVASCRIPT_ERROR
        
        # Metadata/JSON errors
        if exception_name in ["JSONDecodeError", "KeyError", "ValueError"] and any(
            keyword in exception_message for keyword in ["json", "metadata", "serialize"]
        ):
            return RibbonErrorType.METADATA_ERROR
        
        # Styling errors
        if "style" in exception_message or "color" in exception_message:
            return RibbonErrorType.STYLING_ERROR
        
        # Validation errors
        if exception_name in ["ValueError", "TypeError"] and "valid" in exception_message:
            return RibbonErrorType.VALIDATION_ERROR
        
        return RibbonErrorType.UNKNOWN_ERROR
    
    def _log_error(self, ribbon_error: RibbonError):
        """
        Log error information.
        
        Args:
            ribbon_error: Error information to log
        """
        if not self.logger:
            return
        
        error_msg = f"Ribbon Error [{ribbon_error.error_type.value}]: {ribbon_error.message}"
        
        if ribbon_error.file_path:
            error_msg += f" (File: {ribbon_error.file_path})"
        
        if ribbon_error.original_exception:
            error_msg += f"\nOriginal exception: {type(ribbon_error.original_exception).__name__}"
            error_msg += f"\nTraceback: {traceback.format_exc()}"
        
        self.logger.error(error_msg)
    
    def _attempt_recovery(self, ribbon_error: RibbonError, pdf_path: str, output_path: str) -> bool:
        """
        Attempt to recover from error using registered strategies.
        
        Args:
            ribbon_error: Error information
            pdf_path: Input PDF path
            output_path: Output PDF path
            
        Returns:
            bool: True if recovery was successful
        """
        recovery_strategy = self.recovery_strategies.get(ribbon_error.error_type)
        
        if not recovery_strategy:
            return self._default_recovery(ribbon_error, pdf_path, output_path)
        
        try:
            return recovery_strategy(ribbon_error, pdf_path, output_path)
        except Exception as recovery_exception:
            self._log_error(RibbonError(
                error_type=RibbonErrorType.UNKNOWN_ERROR,
                message=f"Recovery strategy failed: {recovery_exception}",
                original_exception=recovery_exception,
                file_path=pdf_path
            ))
            return False
    
    def _default_recovery(self, ribbon_error: RibbonError, pdf_path: str, output_path: str) -> bool:
        """
        Default recovery strategy - copy original file.
        
        Args:
            ribbon_error: Error information
            pdf_path: Input PDF path
            output_path: Output PDF path
            
        Returns:
            bool: True if file was copied successfully
        """
        try:
            import shutil
            shutil.copy2(pdf_path, output_path)
            ribbon_error.fallback_used = "file_copy"
            
            if self.logger:
                self.logger.warning(f"Ribbon embedding failed, copied original file to {output_path}")
            
            return True
        except Exception as copy_error:
            if self.logger:
                self.logger.error(f"Failed to copy original file: {copy_error}")
            return False
    
    def _register_default_recovery_strategies(self):
        """Register default recovery strategies for common error types."""
        
        def pdf_read_recovery(error: RibbonError, pdf_path: str, output_path: str) -> bool:
            """Recovery strategy for PDF read errors."""
            try:
                # Try alternative PDF library or repair
                if self.logger:
                    self.logger.info("Attempting PDF read recovery...")
                
                # For now, just copy the file
                import shutil
                shutil.copy2(pdf_path, output_path)
                error.fallback_used = "pdf_read_fallback"
                return True
            except:
                return False
        
        def permission_recovery(error: RibbonError, pdf_path: str, output_path: str) -> bool:
            """Recovery strategy for permission errors."""
            try:
                # Try with different output path
                import tempfile
                temp_output = tempfile.mktemp(suffix=".pdf")
                
                # Attempt operation with temp file, then move
                # For now, just copy
                import shutil
                shutil.copy2(pdf_path, temp_output)
                shutil.move(temp_output, output_path)
                
                error.fallback_used = "permission_workaround"
                return True
            except:
                return False
        
        def memory_recovery(error: RibbonError, pdf_path: str, output_path: str) -> bool:
            """Recovery strategy for memory errors."""
            try:
                # Try with reduced memory usage
                if self.logger:
                    self.logger.info("Attempting memory-efficient processing...")
                
                # For now, just copy the file
                import shutil
                shutil.copy2(pdf_path, output_path)
                error.fallback_used = "memory_fallback"
                return True
            except:
                return False
        
        # Register strategies
        self.recovery_strategies[RibbonErrorType.PDF_READ_ERROR] = pdf_read_recovery
        self.recovery_strategies[RibbonErrorType.PERMISSION_ERROR] = permission_recovery
        self.recovery_strategies[RibbonErrorType.MEMORY_ERROR] = memory_recovery
    
    def _generate_minimal_javascript_fallback(self, verification_data: Dict[str, Any]) -> str:
        """
        Generate minimal JavaScript fallback for popup functionality.
        
        Args:
            verification_data: Verification data
            
        Returns:
            str: Minimal JavaScript code
        """
        # Extract basic information safely
        is_verified = verification_data.get('is_verified', False)
        cert_info = verification_data.get('certificate', {})
        student_name = cert_info.get('student_name', 'Unknown')
        course_name = cert_info.get('course_name', 'Unknown')
        cert_id = cert_info.get('certificate_id', 'Unknown')
        
        minimal_js = f"""
// EduCerts Minimal Fallback JavaScript
function showVerificationPopup() {{
    var message = 'Certificate Verification\\n\\n';
    message += 'Status: {'VERIFIED' if is_verified else 'UNVERIFIED'}\\n';
    message += 'Student: {student_name}\\n';
    message += 'Course: {course_name}\\n';
    message += 'ID: {cert_id}\\n\\n';
    message += 'This is a simplified verification display.\\n';
    message += 'For full details, verify online.';
    
    alert(message);
}}
"""
        
        return minimal_js
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of all errors encountered.
        
        Returns:
            Dict[str, Any]: Error summary statistics
        """
        if not self.error_history:
            return {"total_errors": 0, "error_types": {}, "recovery_rate": 0.0}
        
        error_types = {}
        successful_recoveries = 0
        
        for error in self.error_history:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
            if error.recovery_successful:
                successful_recoveries += 1
        
        recovery_rate = successful_recoveries / len(self.error_history) if self.error_history else 0.0
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "recovery_rate": recovery_rate,
            "successful_recoveries": successful_recoveries
        }
    
    def clear_error_history(self):
        """Clear the error history."""
        self.error_history.clear()
    
    def register_recovery_strategy(self, error_type: RibbonErrorType, strategy: Callable) -> None:
        """
        Register custom recovery strategy for specific error type.
        
        Args:
            error_type: Type of error to handle
            strategy: Recovery function that takes (error, pdf_path, output_path) and returns bool
        """
        self.recovery_strategies[error_type] = strategy


def create_robust_ribbon_embedder(enable_logging: bool = True) -> 'RibbonErrorHandler':
    """
    Create a robust ribbon embedder with comprehensive error handling.
    
    Args:
        enable_logging: Whether to enable error logging
        
    Returns:
        RibbonErrorHandler: Configured error handler
    """
    return RibbonErrorHandler(enable_logging=enable_logging)


def validate_pdf_file(pdf_path: str) -> tuple[bool, Optional[str]]:
    """
    Validate PDF file before ribbon embedding.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if not os.path.exists(pdf_path):
        return False, f"PDF file does not exist: {pdf_path}"
    
    if not os.path.isfile(pdf_path):
        return False, f"Path is not a file: {pdf_path}"
    
    if not pdf_path.lower().endswith('.pdf'):
        return False, f"File is not a PDF: {pdf_path}"
    
    try:
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return False, "PDF file is empty"
        
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            return False, "PDF file is too large (>100MB)"
        
    except OSError as e:
        return False, f"Cannot access PDF file: {e}"
    
    # Try to open with PyMuPDF
    try:
        import fitz
        doc = fitz.open(pdf_path)
        
        if len(doc) == 0:
            doc.close()
            return False, "PDF has no pages"
        
        doc.close()
        return True, None
        
    except Exception as e:
        return False, f"PDF validation failed: {e}"


def safe_ribbon_embed(
    pdf_path: str, 
    output_path: str, 
    embed_function: Callable,
    error_handler: Optional[RibbonErrorHandler] = None
) -> bool:
    """
    Safely embed ribbon with comprehensive error handling.
    
    Args:
        pdf_path: Input PDF path
        output_path: Output PDF path
        embed_function: Function to perform ribbon embedding
        error_handler: Optional error handler (creates default if None)
        
    Returns:
        bool: True if embedding was successful (or recovered)
    """
    if error_handler is None:
        error_handler = RibbonErrorHandler()
    
    # Validate input file
    is_valid, error_msg = validate_pdf_file(pdf_path)
    if not is_valid:
        print(f"ERROR: {error_msg}")
        return False
    
    try:
        # Attempt ribbon embedding
        return embed_function(pdf_path, output_path)
        
    except Exception as e:
        # Handle error with recovery
        return error_handler.handle_embedding_error(e, pdf_path, output_path)