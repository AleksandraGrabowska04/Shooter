"""
User interface configuration settings.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class UIConfig:
    """User interface configuration"""
    # Display settings
    show_landmarks: bool = True
    show_debug_info: bool = False
    
    # Colors (BGR format for OpenCV)
    landmark_color: Tuple[int, int, int] = (0, 255, 0)
    connection_color: Tuple[int, int, int] = (255, 0, 0)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    debug_color: Tuple[int, int, int] = (0, 255, 255)
    
    # Text settings
    font_scale: float = 0.7
    text_thickness: int = 2
    line_spacing: int = 30
    
    # Window settings
    window_name: str = "Hand Control"
    window_resizable: bool = True
    
    def __post_init__(self):
        """Validate UI configuration after initialization."""
        if self.font_scale <= 0:
            raise ValueError("Font scale must be positive")
        if self.text_thickness <= 0:
            raise ValueError("Text thickness must be positive")
        if self.line_spacing <= 0:
            raise ValueError("Line spacing must be positive")
        
        # Validate colors are within RGB range
        for color_name, color in [
            ('landmark_color', self.landmark_color),
            ('connection_color', self.connection_color),
            ('text_color', self.text_color),
            ('debug_color', self.debug_color)
        ]:
            if not all(0 <= c <= 255 for c in color):
                raise ValueError(f"{color_name} values must be between 0 and 255")