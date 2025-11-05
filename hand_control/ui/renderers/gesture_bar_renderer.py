"""
Gesture bar renderer for visual gesture strength indicators.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Any


class GestureBarRenderer:
    """
    Handles rendering of gesture strength bars and indicators.
    """
    
    def __init__(self, bar_width: int = 25, bar_height: int = 180):
        """
        Initialize gesture bar renderer.
        
        Args:
            bar_width: Width of gesture bars
            bar_height: Height of gesture bars
        """
        self.bar_width = bar_width
        self.bar_height = bar_height
    
    def draw_gesture_bars(self, frame: np.ndarray, gesture_data: Dict[str, Any],
                         text_renderer) -> None:
        """
        Render gesture strength bars on the right side of frame.
        
        Args:
            frame: OpenCV frame to draw on
            gesture_data: Dictionary with gesture information
            text_renderer: Text renderer for labels
        """
        try:
            height, width = frame.shape[:2]
            
            # Bar configuration
            bar_y = 50
            bar_x_thumb = width - 110
            bar_x_roll = width - 55
            
            # Extract gesture values
            thumb_value = gesture_data.get('thumb_angle_rad', 0.0)
            roll_value = gesture_data.get('roll_angle_rad', 0.0)
            
            # Draw simplified thumb status bar (empty/full only)
            self._draw_thumb_status_bar(
                frame, bar_x_thumb, bar_y, thumb_value,
                text_renderer
            )
            
            self._draw_single_gesture_bar(
                frame, bar_x_roll, bar_y, roll_value, 
                "Roll", (0, 255, 0), text_renderer
            )
            
        except Exception:
            pass
    
    def _draw_single_gesture_bar(self, frame: np.ndarray, x: int, y: int,
                                level: float, label: str, 
                                color: Tuple[int, int, int], text_renderer) -> None:
        """
        Draw a single gesture strength bar.
        
        Args:
            frame: OpenCV frame to draw on
            x: X position of bar
            y: Y position of bar  
            level: Gesture level (-1.0 to 1.0)
            label: Label for the bar
            color: Bar color in BGR format
            text_renderer: Text renderer for labels
        """
        width = self.bar_width
        height = self.bar_height
        
        # Draw background bar
        cv2.rectangle(frame, (x, y), (x + width, y + height), (32, 32, 32), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (200, 200, 200), 2)
        
        # Draw center line
        center_y = y + height // 2
        cv2.line(frame, (x, center_y), (x + width, center_y), (255, 255, 255), 2)
        
        # Draw filled portion based on level
        if level > 0:
            # Positive level (upper half)
            fill_height = int(level * height // 2)
            cv2.rectangle(frame, (x + 3, center_y - fill_height), 
                         (x + width - 3, center_y), color, -1)
        elif level < 0:
            # Negative level (lower half)
            fill_height = int(-level * height // 2)
            cv2.rectangle(frame, (x + 3, center_y), 
                         (x + width - 3, center_y + fill_height), color, -1)
        
        # Draw label with outline
        text_renderer.draw_text_with_outline(frame, label, (x, y - 4), (0, 255, 0))
        
        # Draw value with outline
        max_degrees = 30 if label == "Thumb" else 90
        angle_degrees = level * max_degrees
        value_text = f"{angle_degrees:.0f}deg"
        text_renderer.draw_text_with_outline(frame, value_text, (x, y + height + 18), (0, 255, 0))

    def _draw_thumb_status_bar(self, frame, x, y, thumb_value, text_renderer):
        """Draw simplified thumb status bar - only empty or full."""
        width = 40
        height = 100
        
        # Draw background bar
        cv2.rectangle(frame, (x, y), (x + width, y + height), (32, 32, 32), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height), (200, 200, 200), 2)
        
        # Determine thumb state based on value
        # If thumb_value > 0.4 = extended (thumb_up) else neutral
        if thumb_value > 0.4:
            # Thumb up - fill entire bar green
            cv2.rectangle(frame, (x + 3, y + 3), (x + width - 3, y + height - 3), (0, 255, 0), -1)
            status_text = "UP"
        else:
            # Neutral - leave empty (just background)
            status_text = "NEUTRAL"
        
        # Draw label with outline
        text_renderer.draw_text_with_outline(frame, "Thumb", (x, y - 4), (0, 255, 0))
        
        # Draw status text with outline
        text_renderer.draw_text_with_outline(frame, status_text, (x, y + height + 18), (0, 255, 0))