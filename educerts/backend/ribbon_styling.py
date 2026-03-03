"""
Ribbon Styling System

This module provides customizable styling configurations for PDF verification ribbons.
Supports different themes, colors, and layouts for various verification states.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple
from enum import Enum


class VerificationStatus(Enum):
    """Enumeration of possible verification statuses."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    TAMPERED = "tampered"
    REVOKED = "revoked"
    ERROR = "error"


class RibbonPosition(Enum):
    """Enumeration of ribbon positions on PDF page."""
    TOP = "top"
    BOTTOM = "bottom"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"


@dataclass
class ColorScheme:
    """Color scheme for different verification states."""
    background: str
    text: str
    border: str
    accent: str
    
    @property
    def background_rgb(self) -> str:
        """Convert background color to RGB format for PDF."""
        return self._hex_to_rgb(self.background)
    
    @property
    def text_rgb(self) -> str:
        """Convert text color to RGB format for PDF."""
        return self._hex_to_rgb(self.text)
    
    @property
    def border_rgb(self) -> str:
        """Convert border color to RGB format for PDF."""
        return self._hex_to_rgb(self.border)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for PDF operations."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return f"{r:.3f} {g:.3f} {b:.3f}"
        except (ValueError, IndexError):
            # Fallback to blue if parsing fails
            return "0.149 0.388 0.922"  # #2563eb


@dataclass
class RibbonStyle:
    """
    Complete styling configuration for verification ribbons.
    """
    # Basic dimensions
    height: int = 30
    width_percentage: float = 0.95  # Percentage of page width
    margin: int = 10
    
    # Position and layout
    position: RibbonPosition = RibbonPosition.TOP
    border_radius: int = 4
    border_width: int = 1
    
    # Typography
    font_name: str = "Helvetica-Bold"
    font_size: int = 12
    text_align: str = "left"  # left, center, right
    
    # Colors (default to verified state)
    background_color: str = "#2563eb"  # Blue
    text_color: str = "#ffffff"        # White
    border_color: str = "#1d4ed8"      # Darker blue
    
    # Color schemes for different states
    color_schemes: Dict[VerificationStatus, ColorScheme] = field(default_factory=lambda: {
        VerificationStatus.VERIFIED: ColorScheme(
            background="#2563eb",  # Blue
            text="#ffffff",        # White
            border="#1d4ed8",      # Darker blue
            accent="#3b82f6"       # Light blue
        ),
        VerificationStatus.UNVERIFIED: ColorScheme(
            background="#6b7280",  # Gray
            text="#ffffff",        # White
            border="#4b5563",      # Darker gray
            accent="#9ca3af"       # Light gray
        ),
        VerificationStatus.TAMPERED: ColorScheme(
            background="#dc2626",  # Red
            text="#ffffff",        # White
            border="#b91c1c",      # Darker red
            accent="#ef4444"       # Light red
        ),
        VerificationStatus.REVOKED: ColorScheme(
            background="#ea580c",  # Orange
            text="#ffffff",        # White
            border="#c2410c",      # Darker orange
            accent="#f97316"       # Light orange
        ),
        VerificationStatus.ERROR: ColorScheme(
            background="#7c2d12",  # Dark red
            text="#ffffff",        # White
            border="#451a03",      # Very dark red
            accent="#dc2626"       # Red
        )
    })
    
    # Interactive features
    enable_javascript: bool = True
    enable_hover_effects: bool = True
    enable_click_animation: bool = True
    
    # Branding
    show_logo: bool = True
    logo_text: str = "EduCerts"
    show_icon: bool = True
    
    # Advanced styling
    shadow_enabled: bool = True
    shadow_color: str = "rgba(0, 0, 0, 0.1)"
    gradient_enabled: bool = False
    
    def get_color_scheme(self, status: VerificationStatus) -> ColorScheme:
        """
        Get color scheme for specific verification status.
        
        Args:
            status: Verification status
            
        Returns:
            ColorScheme: Color scheme for the status
        """
        return self.color_schemes.get(status, self.color_schemes[VerificationStatus.VERIFIED])
    
    def apply_status_colors(self, status: VerificationStatus):
        """
        Apply colors for specific verification status.
        
        Args:
            status: Verification status to apply colors for
        """
        scheme = self.get_color_scheme(status)
        self.background_color = scheme.background
        self.text_color = scheme.text
        self.border_color = scheme.border
    
    @property
    def background_color_rgb(self) -> str:
        """Get background color in RGB format for PDF operations."""
        return self._hex_to_rgb(self.background_color)
    
    @property
    def text_color_rgb(self) -> str:
        """Get text color in RGB format for PDF operations."""
        return self._hex_to_rgb(self.text_color)
    
    @property
    def border_color_rgb(self) -> str:
        """Get border color in RGB format for PDF operations."""
        return self._hex_to_rgb(self.border_color)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for PDF operations."""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        try:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return f"{r:.3f} {g:.3f} {b:.3f}"
        except (ValueError, IndexError):
            # Fallback to blue if parsing fails
            return "0.149 0.388 0.922"  # #2563eb
    
    def get_status_text(self, status: VerificationStatus) -> str:
        """
        Get display text for verification status.
        
        Args:
            status: Verification status
            
        Returns:
            str: Display text with icon
        """
        status_texts = {
            VerificationStatus.VERIFIED: "🔒 VERIFIED",
            VerificationStatus.UNVERIFIED: "⚠️ UNVERIFIED",
            VerificationStatus.TAMPERED: "🚫 TAMPERED",
            VerificationStatus.REVOKED: "❌ REVOKED",
            VerificationStatus.ERROR: "⚠️ ERROR"
        }
        
        base_text = status_texts.get(status, "❓ UNKNOWN")
        
        if self.show_logo:
            return f"{base_text} - {self.logo_text}"
        
        return base_text
    
    def calculate_ribbon_dimensions(self, page_width: float, page_height: float) -> Tuple[float, float, float, float]:
        """
        Calculate ribbon position and dimensions based on page size.
        
        Args:
            page_width: PDF page width
            page_height: PDF page height
            
        Returns:
            Tuple[float, float, float, float]: (x, y, width, height)
        """
        ribbon_width = page_width * self.width_percentage
        ribbon_height = self.height
        
        # Calculate position based on ribbon position setting
        if self.position == RibbonPosition.TOP:
            x = (page_width - ribbon_width) / 2
            y = self.margin
        elif self.position == RibbonPosition.BOTTOM:
            x = (page_width - ribbon_width) / 2
            y = page_height - ribbon_height - self.margin
        elif self.position == RibbonPosition.TOP_LEFT:
            x = self.margin
            y = self.margin
        elif self.position == RibbonPosition.TOP_RIGHT:
            x = page_width - ribbon_width - self.margin
            y = self.margin
        else:
            # Default to top center
            x = (page_width - ribbon_width) / 2
            y = self.margin
        
        return (x, y, ribbon_width, ribbon_height)
    
    def generate_css_styles(self) -> str:
        """
        Generate CSS styles for web-based popup display.
        
        Returns:
            str: CSS styles
        """
        return f"""
        .verification-ribbon {{
            background-color: {self.background_color};
            color: {self.text_color};
            border: {self.border_width}px solid {self.border_color};
            border-radius: {self.border_radius}px;
            height: {self.height}px;
            font-family: {self.font_name.replace('-', ', ')};
            font-size: {self.font_size}px;
            text-align: {self.text_align};
            cursor: pointer;
            transition: all 0.2s ease;
            {'box-shadow: 0 2px 4px ' + self.shadow_color + ';' if self.shadow_enabled else ''}
        }}
        
        .verification-ribbon:hover {{
            {'opacity: 0.9;' if self.enable_hover_effects else ''}
            {'transform: translateY(-1px);' if self.enable_hover_effects else ''}
        }}
        
        .verification-ribbon:active {{
            {'transform: translateY(0px);' if self.enable_click_animation else ''}
        }}
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert styling configuration to dictionary."""
        return {
            "height": self.height,
            "width_percentage": self.width_percentage,
            "margin": self.margin,
            "position": self.position.value,
            "border_radius": self.border_radius,
            "border_width": self.border_width,
            "font_name": self.font_name,
            "font_size": self.font_size,
            "text_align": self.text_align,
            "background_color": self.background_color,
            "text_color": self.text_color,
            "border_color": self.border_color,
            "enable_javascript": self.enable_javascript,
            "enable_hover_effects": self.enable_hover_effects,
            "enable_click_animation": self.enable_click_animation,
            "show_logo": self.show_logo,
            "logo_text": self.logo_text,
            "show_icon": self.show_icon,
            "shadow_enabled": self.shadow_enabled,
            "gradient_enabled": self.gradient_enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RibbonStyle':
        """Create RibbonStyle from dictionary."""
        # Handle position enum
        position_str = data.get('position', 'top')
        position = RibbonPosition(position_str) if position_str in [p.value for p in RibbonPosition] else RibbonPosition.TOP
        
        return cls(
            height=data.get('height', 30),
            width_percentage=data.get('width_percentage', 0.95),
            margin=data.get('margin', 10),
            position=position,
            border_radius=data.get('border_radius', 4),
            border_width=data.get('border_width', 1),
            font_name=data.get('font_name', 'Helvetica-Bold'),
            font_size=data.get('font_size', 12),
            text_align=data.get('text_align', 'left'),
            background_color=data.get('background_color', '#2563eb'),
            text_color=data.get('text_color', '#ffffff'),
            border_color=data.get('border_color', '#1d4ed8'),
            enable_javascript=data.get('enable_javascript', True),
            enable_hover_effects=data.get('enable_hover_effects', True),
            enable_click_animation=data.get('enable_click_animation', True),
            show_logo=data.get('show_logo', True),
            logo_text=data.get('logo_text', 'EduCerts'),
            show_icon=data.get('show_icon', True),
            shadow_enabled=data.get('shadow_enabled', True),
            gradient_enabled=data.get('gradient_enabled', False)
        )


class RibbonStylePresets:
    """
    Predefined styling presets for common use cases.
    """
    
    @staticmethod
    def default() -> RibbonStyle:
        """Default blue verification ribbon."""
        return RibbonStyle()
    
    @staticmethod
    def minimal() -> RibbonStyle:
        """Minimal styling with reduced visual elements."""
        return RibbonStyle(
            height=25,
            border_width=0,
            shadow_enabled=False,
            show_logo=False,
            enable_hover_effects=False,
            enable_click_animation=False
        )
    
    @staticmethod
    def professional() -> RibbonStyle:
        """Professional styling with enhanced visual elements."""
        return RibbonStyle(
            height=35,
            border_radius=6,
            font_size=14,
            shadow_enabled=True,
            gradient_enabled=True,
            text_align="center"
        )
    
    @staticmethod
    def compact() -> RibbonStyle:
        """Compact ribbon for space-constrained layouts."""
        return RibbonStyle(
            height=20,
            font_size=10,
            margin=5,
            width_percentage=0.8,
            show_logo=False
        )
    
    @staticmethod
    def high_contrast() -> RibbonStyle:
        """High contrast styling for accessibility."""
        style = RibbonStyle()
        style.color_schemes[VerificationStatus.VERIFIED] = ColorScheme(
            background="#000000",  # Black
            text="#ffffff",        # White
            border="#ffffff",      # White border
            accent="#ffffff"       # White accent
        )
        style.apply_status_colors(VerificationStatus.VERIFIED)
        return style
    
    @staticmethod
    def custom_brand(
        brand_color: str, 
        brand_name: str, 
        position: RibbonPosition = RibbonPosition.TOP
    ) -> RibbonStyle:
        """
        Create custom branded ribbon style.
        
        Args:
            brand_color: Primary brand color (hex)
            brand_name: Brand name to display
            position: Ribbon position
            
        Returns:
            RibbonStyle: Custom branded style
        """
        return RibbonStyle(
            background_color=brand_color,
            logo_text=brand_name,
            position=position,
            text_align="center"
        )


def validate_color(color: str) -> bool:
    """
    Validate hex color format.
    
    Args:
        color: Color string to validate
        
    Returns:
        bool: True if valid hex color
    """
    if not color.startswith('#'):
        return False
    
    if len(color) != 7:
        return False
    
    try:
        int(color[1:], 16)
        return True
    except ValueError:
        return False


def get_contrasting_text_color(background_color: str) -> str:
    """
    Get contrasting text color (black or white) for given background.
    
    Args:
        background_color: Background color in hex format
        
    Returns:
        str: Contrasting text color (#000000 or #ffffff)
    """
    if not validate_color(background_color):
        return "#ffffff"  # Default to white
    
    # Convert to RGB
    hex_color = background_color[1:]
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    # Calculate luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Return black for light backgrounds, white for dark backgrounds
    return "#000000" if luminance > 0.5 else "#ffffff"


def create_status_aware_style(is_verified: bool, is_tampered: bool = False, is_revoked: bool = False) -> RibbonStyle:
    """
    Create ribbon style based on verification status.
    
    Args:
        is_verified: Whether certificate is verified
        is_tampered: Whether tampering was detected
        is_revoked: Whether certificate is revoked
        
    Returns:
        RibbonStyle: Style configured for the verification status
    """
    style = RibbonStyle()
    
    if is_tampered:
        status = VerificationStatus.TAMPERED
    elif is_revoked:
        status = VerificationStatus.REVOKED
    elif is_verified:
        status = VerificationStatus.VERIFIED
    else:
        status = VerificationStatus.UNVERIFIED
    
    style.apply_status_colors(status)
    return style