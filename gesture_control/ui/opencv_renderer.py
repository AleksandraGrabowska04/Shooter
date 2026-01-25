"""
OpenCV-based visualization renderer for gesture control system.
"""

import numpy as np
from typing import Optional, Dict, Any

from ..core.interfaces import IVisualizationRenderer
from ..core.config import ApplicationConfig
from ..core.types import CalibrationData
from .renderers import TextRenderer, LandmarkRenderer, DebugRenderer, GestureBarRenderer


class OpenCVRenderer(IVisualizationRenderer):
    """
    OpenCV-based visualization renderer implementation.
    
    This class coordinates specialized rendering components to handle
    visual overlays and debug information using modular architecture.
    """
    
    def __init__(self, config: ApplicationConfig):
        """
        Initialize OpenCV renderer with modular components.
        
        Args:
            config: Application configuration containing UI settings
        """
        self.config = config
        
        # Initialize specialized rendering components
        self.text_renderer = TextRenderer(
            font_scale=config.ui.font_scale,
            font_thickness=config.ui.text_thickness,
            line_spacing=config.ui.line_spacing
        )
        
        self.landmark_renderer = LandmarkRenderer(
            landmark_color=config.ui.landmark_color,
            connection_color=config.ui.connection_color
        )
        
        self.debug_renderer = DebugRenderer(
            line_spacing=config.ui.line_spacing,
            debug_start_y=60
        )
        
        self.gesture_bar_renderer = GestureBarRenderer(
            bar_width=25,
            bar_height=180
        )
        
        # Store colors for direct use
        self.text_color = config.ui.text_color
        self.debug_color = config.ui.debug_color
    
    def render_status(self, frame: Any, status_message: str) -> None:
        """
        Render status message on frame.
        
        Args:
            frame: OpenCV frame to render on
            status_message: Status text to display
        """
        if not isinstance(frame, np.ndarray):
            return
        
        try:
            # Render main status at top
            if status_message:
                self.text_renderer.draw_status_text(frame, status_message, self.text_color)
            
            # Always add ESC instruction at bottom
            height = frame.shape[0]
            self.text_renderer.draw_text_with_outline(
                frame,
                "Press ESC to exit",
                (10, height - 30),
                (150, 150, 150)  # Gray color
            )
            
        except Exception:
            pass
    
    def render_debug_info(self, frame: Any, debug_info: dict) -> None:
        """
        Render debug information on frame.
        
        Args:
            frame: OpenCV frame to render on  
            debug_info: Dictionary with debug information
        """
        if not isinstance(frame, np.ndarray) or not debug_info:
            return
        
        if not self.config.ui.show_debug_info:
            return
        
        self.debug_renderer.draw_debug_info(
            frame, debug_info, self.text_renderer, self.debug_color
        )
    
    def render_gesture_visualization(self, frame: Any, landmarks: Optional[dict], 
                                   calibration: CalibrationData) -> None:
        """
        Render gesture-specific visualization.
        
        Args:
            frame: OpenCV frame to render on
            landmarks: Hand landmarks dictionary
            calibration: Calibration data for reference points
        """
        if not isinstance(frame, np.ndarray):
            return
        
        try:
            # Draw landmarks if available
            if landmarks and self.config.ui.show_landmarks:
                self.landmark_renderer.draw_hand_landmarks(frame, landmarks)
            
            # Draw calibration visualization (always show when landmarks available)
            if landmarks:
                # Get max distance from strategies config
                max_distance = self.config.strategies.position.max_distance_from_calibration
                self.landmark_renderer.draw_calibration_visualization(
                    frame, landmarks, calibration, self.text_renderer, max_distance
                )
            
        except Exception:
            pass
    
    def render_gesture_bars(self, frame: np.ndarray, gesture_data: dict) -> None:
        """
        Render gesture strength bars on the right side of frame.
        
        Args:
            frame: OpenCV frame to render on
            gesture_data: Dictionary with gesture information
        """
        if not isinstance(frame, np.ndarray):
            return
        
        self.gesture_bar_renderer.draw_gesture_bars(
            frame, gesture_data, self.text_renderer
        )
    
    def render_shoot_indication(self, frame: np.ndarray, is_shooting: bool) -> None:
        """
        Render prominent shoot indication.
        
        Args:
            frame: OpenCV frame to render on
            is_shooting: Whether shooting is active
        """
        if not is_shooting or not isinstance(frame, np.ndarray):
            return
        
        self.text_renderer.draw_shoot_indication(frame)
    
    def get_renderer_info(self) -> Dict[str, Any]:
        """Get renderer configuration information."""
        return {
            'renderer_type': 'OpenCV_Modular',
            'components': {
                'text_renderer': True,
                'landmark_renderer': True,
                'debug_renderer': True,
                'gesture_bar_renderer': True
            },
            'show_landmarks': self.config.ui.show_landmarks,
            'show_debug_info': self.config.ui.show_debug_info,
            'colors': {
                'text': self.text_color,
                'debug': self.debug_color,
            }
        }
