"""
Configuration for UI rendering components.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass 
class TextRendererConfig:
    """Configuration for text rendering."""
    # Font settings
    default_font_scale: float = 0.6
    default_font_thickness: int = 2
    line_spacing: int = 25
    
    # Shoot indication settings
    shoot_font_scale: float = 1.2
    shoot_font_thickness: int = 2
    shoot_padding: int = 15


@dataclass
class GestureBarRendererConfig:
    """Configuration for gesture bar rendering."""
    # Bar dimensions
    bar_width: int = 25
    bar_height: int = 180
    
    # Positioning
    bar_y_offset: int = 50
    thumb_bar_x_offset: int = 110  # From right edge
    roll_bar_x_offset: int = 55    # From right edge
    
    # Thumb state thresholds
    thumb_up_threshold: float = 0.4
    thumb_down_threshold: float = -0.4
    
    # Simple thumb status bar dimensions
    simple_thumb_width: int = 40
    simple_thumb_height: int = 100
    
    # Angle display settings
    thumb_max_degrees: int = 30
    roll_max_degrees: int = 90


@dataclass
class LandmarkRendererConfig:
    """Configuration for landmark rendering."""
    # Circle drawing settings
    landmark_radius: int = 3
    connection_thickness: int = 1
    
    # Colors (BGR format)
    landmark_color: Tuple[int, int, int] = (0, 255, 0)  # Green
    connection_color: Tuple[int, int, int] = (255, 0, 0)  # Blue


@dataclass
class DebugRendererConfig:
    """Configuration for debug information rendering."""
    # Debug text settings
    line_spacing: int = 25
    debug_start_y: int = 60
    
    # Debug info colors
    debug_text_color: Tuple[int, int, int] = (255, 255, 255)  # White
    debug_outline_color: Tuple[int, int, int] = (0, 0, 0)     # Black


@dataclass
class UIRenderingConfig:
    """Master configuration for all UI rendering components."""
    text_renderer: TextRendererConfig = field(default_factory=TextRendererConfig)
    gesture_bar_renderer: GestureBarRendererConfig = field(default_factory=GestureBarRendererConfig)
    landmark_renderer: LandmarkRendererConfig = field(default_factory=LandmarkRendererConfig)
    debug_renderer: DebugRendererConfig = field(default_factory=DebugRendererConfig)