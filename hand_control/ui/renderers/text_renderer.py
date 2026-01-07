"""
Text rendering component for OpenCV-based visualization.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


class TextRenderer:
    """
    Handles text rendering with outlines and formatting.
    """
    
    def __init__(self, font_scale: float = 0.6, font_thickness: int = 2, 
                 line_spacing: int = 25):
        """
        Initialize text renderer.
        
        Args:
            font_scale: Scale factor for font size
            font_thickness: Thickness of text lines
            line_spacing: Space between text lines
        """
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.line_spacing = line_spacing
    
    def draw_text_with_outline(self, frame: np.ndarray, text: str, 
                              position: Tuple[int, int], color: Tuple[int, int, int],
                              outline_color: Tuple[int, int, int] = (0, 0, 0),
                              font_scale: Optional[float] = None, 
                              thickness: Optional[int] = None) -> None:
        """
        Draw text with outline for better visibility.
        
        Args:
            frame: OpenCV frame to draw on
            text: Text to render
            position: (x, y) position for text
            color: Text color in BGR format
            outline_color: Outline color in BGR format
            font_scale: Optional custom font scale
            thickness: Optional custom thickness
        """
        font_scale = font_scale or self.font_scale
        thickness = thickness or self.font_thickness
        
        # Draw outline (thicker, darker text)
        outline_thickness = thickness + 2
        cv2.putText(frame, text, position, self.font, font_scale, 
                   outline_color, outline_thickness)
        
        # Draw main text on top  
        cv2.putText(frame, text, position, self.font, font_scale, 
                   color, thickness)
    
    def draw_status_text(self, frame: np.ndarray, status_message: str,
                        color: Tuple[int, int, int] = (0, 255, 0)) -> None:
        """
        Draw status message at top of frame.
        
        Args:
            frame: OpenCV frame to draw on
            status_message: Status text to display
            color: Text color in BGR format
        """
        if not isinstance(frame, np.ndarray) or not status_message:
            return
        
        try:
            self.draw_text_with_outline(
                frame, 
                status_message, 
                (10, 30), 
                color
            )
        except Exception:
            pass
    
    def draw_multiline_text(self, frame: np.ndarray, lines: List[str],
                           start_position: Tuple[int, int],
                           color: Tuple[int, int, int]) -> None:
        """
        Draw multiple lines of text.
        
        Args:
            frame: OpenCV frame to draw on
            lines: List of text lines to draw
            start_position: Starting (x, y) position
            color: Text color in BGR format
        """
        try:
            x, y = start_position
            for line in lines:
                self.draw_text_with_outline(frame, line, (x, y), color)
                y += self.line_spacing
        except Exception:
            pass
    
    def draw_shoot_indication(self, frame: np.ndarray) -> None:
        """
        Draw prominent action indication in center of frame.
        
        Args:
            frame: OpenCV frame to draw on
        """
        try:
            # Get frame dimensions
            h, w = frame.shape[:2]
            
            # Draw prominent ACTION indicator in center
            text = "ACTION"
            font_scale = 1.2
            thickness = 2
            
            # Calculate text size and position for center alignment
            text_size = cv2.getTextSize(text, self.font, font_scale, thickness)[0]
            text_x = (w - text_size[0]) // 2
            text_y = (h + text_size[1]) // 2
            
            # Add background rectangle
            padding = 15
            cv2.rectangle(frame, 
                         (text_x - padding, text_y - text_size[1] - padding), 
                         (text_x + text_size[0] + padding, text_y + padding), 
                         (0, 0, 0), -1)  # Black background
            
            # Draw the text in bright red
            cv2.putText(frame, text, (text_x, text_y), self.font, font_scale, 
                       (0, 0, 255), thickness, cv2.LINE_AA)
            
        except Exception:
            pass
