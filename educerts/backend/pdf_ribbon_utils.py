"""
PDF Verification Ribbon Utilities

This module provides functionality to embed interactive verification ribbons
into PDF certificates, similar to WPS Office upgrade prompts.
"""

import fitz  # PyMuPDF
import json
import os
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from verification_metadata import VerificationMetadata
from ribbon_styling import RibbonStyle
from pdf_javascript_templates import JavaScriptTemplates
from ribbon_error_handling import RibbonError, RibbonErrorHandler


@dataclass
class RibbonPosition:
    """Defines the position and dimensions of the verification ribbon"""
    x: float = 0
    y: float = 0
    width: float = 595  # A4 width in points
    height: float = 30
    page: int = 0  # First page


class VerificationRibbon:
    """
    Main class for creating and embedding interactive verification ribbons in PDFs
    """
    
    def __init__(self, verification_data: VerificationMetadata, styling: Optional[RibbonStyle] = None):
        """
        Initialize the verification ribbon
        
        Args:
            verification_data: Structured verification metadata
            styling: Optional custom styling, defaults to blue verified style
        """
        self.verification_data = verification_data
        self.styling = styling or RibbonStyle()
        
    def embed_ribbon(self, pdf_path: str, output_path: str) -> bool:
        """
        Embeds interactive verification ribbon into PDF
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path for output PDF with ribbon
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Open the PDF document
            doc = fitz.open(pdf_path)
            
            if len(doc) == 0:
                raise RibbonError("PDF document has no pages")
            
            # Get the first page for ribbon placement
            page = doc[0]
            
            # Calculate ribbon position to avoid content overlap
            ribbon_pos = self._calculate_ribbon_position(page)
            
            # Create the ribbon annotation
            self._create_ribbon_annotation(page, ribbon_pos)
            
            # Embed verification metadata
            self._embed_verification_metadata(doc)
            
            # Add interactive JavaScript
            self._add_interactive_javascript(doc)
            
            # Save the enhanced PDF
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            print(f"✓ Successfully embedded verification ribbon in {output_path}")
            return True
            
        except Exception as e:
            error_handler = RibbonErrorHandler()
            return error_handler.handle_embedding_error(e, pdf_path, output_path)
    
    def _calculate_ribbon_position(self, page: fitz.Page) -> RibbonPosition:
        """
        Calculate optimal ribbon position to avoid content overlap
        
        Args:
            page: PDF page object
            
        Returns:
            RibbonPosition: Calculated position and dimensions
        """
        page_rect = page.rect
        
        # Position ribbon at the very top of the page
        ribbon_pos = RibbonPosition(
            x=0,
            y=page_rect.height - self.styling.height,  # Top of page
            width=page_rect.width,
            height=self.styling.height,
            page=0
        )
        
        # Check for existing content in ribbon area
        text_blocks = page.get_text("blocks")
        for block in text_blocks:
            block_rect = fitz.Rect(block[:4])
            ribbon_rect = fitz.Rect(ribbon_pos.x, ribbon_pos.y, 
                                  ribbon_pos.x + ribbon_pos.width, 
                                  ribbon_pos.y + ribbon_pos.height)
            
            # If content overlaps, adjust ribbon position
            if block_rect.intersects(ribbon_rect):
                # Move ribbon slightly down to avoid overlap
                ribbon_pos.y = max(0, ribbon_pos.y - 5)
                break
        
        return ribbon_pos
    
    def _create_ribbon_annotation(self, page: fitz.Page, position: RibbonPosition):
        """
        Create the visual ribbon annotation
        
        Args:
            page: PDF page object
            position: Ribbon position and dimensions
        """
        # Create rectangle for ribbon
        ribbon_rect = fitz.Rect(position.x, position.y, 
                               position.x + position.width, 
                               position.y + position.height)
        
        # Determine ribbon color based on verification status
        if self.verification_data.is_verified():
            bg_color = self.styling.verified_color
            text_color = self.styling.text_color
            status_text = "🔒 VERIFIED - EduCerts"
        else:
            bg_color = self.styling.warning_color
            text_color = self.styling.warning_text_color
            status_text = "⚠️ UNVERIFIED - EduCerts"
        
        # Create background rectangle annotation
        bg_annot = page.add_rect_annot(ribbon_rect)
        bg_annot.set_colors(stroke=bg_color, fill=bg_color)
        bg_annot.set_border(width=0)
        bg_annot.update()
        
        # Add text annotation for ribbon content
        text_rect = fitz.Rect(position.x + 10, position.y + 5,
                             position.x + position.width - 10, 
                             position.y + position.height - 5)
        
        text_annot = page.add_freetext_annot(text_rect, status_text)
        text_annot.set_info(title="EduCerts Verification", content=status_text)
        text_annot.set_text_color(text_color)
        text_annot.set_font_size(self.styling.font_size)
        text_annot.set_font("helv")
        text_annot.set_border(width=0)
        text_annot.update()
        
        # Make the ribbon clickable by adding a button widget
        widget_rect = ribbon_rect
        widget = page.add_widget(fitz.PDF_WIDGET_TYPE_BUTTON, widget_rect)
        widget.field_name = "verification_ribbon"
        widget.field_label = "Click for verification details"
        widget.button_caption = ""  # No visible caption, just clickable area
        widget.set_field_action("JavaScript", "showVerificationPopup();")
        widget.update()
    
    def _embed_verification_metadata(self, doc: fitz.Document):
        """
        Embed verification metadata in PDF for offline access
        
        Args:
            doc: PDF document object
        """
        # Convert verification data to JSON
        metadata_json = json.dumps(asdict(self.verification_data), indent=2)
        
        # Store in PDF metadata
        current_metadata = doc.metadata
        current_metadata["verification_data"] = metadata_json
        current_metadata["verification_status"] = "verified" if self.verification_data.is_verified() else "unverified"
        current_metadata["verification_timestamp"] = datetime.now().isoformat()
        
        doc.set_metadata(current_metadata)
    
    def _add_interactive_javascript(self, doc: fitz.Document):
        """
        Add JavaScript for interactive popup functionality
        
        Args:
            doc: PDF document object
        """
        # Get JavaScript template with verification data
        js_templates = JavaScriptTemplates()
        js_code = js_templates.generate_popup_javascript(self.verification_data)
        
        # Add JavaScript to PDF
        try:
            doc.add_javascript("verification_popup", js_code)
            print("✓ Added interactive JavaScript to PDF")
        except Exception as e:
            print(f"WARNING: Could not add JavaScript: {e}")
            # Continue without JavaScript - ribbon will still be visible


def create_verification_ribbon(pdf_path: str, output_path: str, 
                             verification_data: VerificationMetadata,
                             styling: Optional[RibbonStyle] = None) -> bool:
    """
    Convenience function to create and embed a verification ribbon
    
    Args:
        pdf_path: Input PDF file path
        output_path: Output PDF file path
        verification_data: Verification metadata
        styling: Optional custom styling
        
    Returns:
        bool: True if successful, False otherwise
    """
    ribbon = VerificationRibbon(verification_data, styling)
    return ribbon.embed_ribbon(pdf_path, output_path)


def extract_verification_data(pdf_path: str) -> Optional[VerificationMetadata]:
    """
    Extract verification metadata from a PDF with embedded ribbon
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        VerificationMetadata or None if not found
    """
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        if "verification_data" in metadata:
            data_json = metadata["verification_data"]
            data_dict = json.loads(data_json)
            return VerificationMetadata(**data_dict)
        
        return None
        
    except Exception as e:
        print(f"ERROR: Could not extract verification data: {e}")
        return None


def validate_ribbon_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Validate that a PDF has a properly embedded verification ribbon
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        dict: Validation results
    """
    results = {
        "has_ribbon": False,
        "has_metadata": False,
        "has_javascript": False,
        "is_valid": False,
        "errors": []
    }
    
    try:
        doc = fitz.open(pdf_path)
        
        # Check for verification metadata
        metadata = doc.metadata
        if "verification_data" in metadata:
            results["has_metadata"] = True
        else:
            results["errors"].append("No verification metadata found")
        
        # Check for ribbon annotations on first page
        if len(doc) > 0:
            page = doc[0]
            annotations = page.annots()
            
            ribbon_found = False
            for annot in annotations:
                if annot.type[1] in ["FreeText", "Square", "Widget"]:
                    ribbon_found = True
                    break
            
            results["has_ribbon"] = ribbon_found
            if not ribbon_found:
                results["errors"].append("No ribbon annotations found")
        
        # Check for JavaScript
        js_names = doc.get_javascript()
        if js_names and "verification_popup" in str(js_names):
            results["has_javascript"] = True
        else:
            results["errors"].append("No interactive JavaScript found")
        
        doc.close()
        
        # Overall validation
        results["is_valid"] = (results["has_ribbon"] and 
                              results["has_metadata"] and 
                              len(results["errors"]) == 0)
        
    except Exception as e:
        results["errors"].append(f"PDF validation error: {e}")
    
    return results


if __name__ == "__main__":
    # Test the ribbon system
    from verification_metadata import create_test_verification_data
    
    test_data = create_test_verification_data()
    
    # Test ribbon creation
    success = create_verification_ribbon(
        "test_input.pdf",
        "test_output_with_ribbon.pdf", 
        test_data
    )
    
    if success:
        print("✓ Test ribbon creation successful")
        
        # Validate the result
        validation = validate_ribbon_pdf("test_output_with_ribbon.pdf")
        print(f"Validation results: {validation}")
    else:
        print("✗ Test ribbon creation failed")