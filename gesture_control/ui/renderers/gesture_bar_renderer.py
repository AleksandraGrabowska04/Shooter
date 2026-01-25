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

    def draw_gesture_bars(self, frame: np.ndarray, gesture_data: Dict[str, Any], text_renderer) -> None:
        """
        Render head gesture strength bars (tilt, turn, nod) on the right side of the frame.
        Args:
            frame: OpenCV frame to draw on
            gesture_data: Dictionary with head gesture strengths (e.g. head_tilt, head_turn, head_nod)
            text_renderer: Text renderer for labels
        """
        try:
            height, width = frame.shape[:2]
            bar_y = 50
            bar_spacing = 50
            bar_labels = [
                ("head_tilt", "Tilt", (255, 200, 0)),
                ("head_turn", "Turn", (0, 255, 255)),
                ("head_nod", "Nod", (0, 200, 255)),
            ]
            for i, (key, label, color) in enumerate(bar_labels):
                bar_x = width - (self.bar_width + bar_spacing) * \
                    (len(bar_labels) - i)
                value = 0.0
                if key in gesture_data and isinstance(gesture_data[key], dict):
                    value = float(gesture_data[key].get('value', 0.0))
                # Clamp value to [-1, 1] for bar rendering
                print(key, value)  # Debug print
                value = max(-1.0, min(1.0, value))
                self._draw_single_gesture_bar(
                    frame, bar_x, bar_y, value, label, color, text_renderer
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
        cv2.rectangle(frame, (x, y), (x + width, y + height),
                      (200, 200, 200), 2)

        # Draw center line
        center_y = y + height // 2
        cv2.line(frame, (x, center_y),
                 (x + width, center_y), (255, 255, 255), 2)

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
        text_renderer.draw_text_with_outline(
            frame, label, (x, y - 4), (0, 255, 0), font_scale=0.6, thickness=1)

        # Draw value with outline
        max_degrees = 30 if label == "Thumb" else 90
        angle_degrees = level * max_degrees
        value_text = f"{angle_degrees:.0f}deg"
        text_renderer.draw_text_with_outline(
            frame, value_text, (x, y + height + 18), (0, 255, 0), font_scale=0.6, thickness=1)

    def _draw_thumb_status_bar(self, frame, x, y, thumb_value, text_renderer):
        """Draw simplified thumb status bar - only empty or full."""
        width = 40
        height = 100

        # Draw background bar
        cv2.rectangle(frame, (x, y), (x + width, y + height), (32, 32, 32), -1)
        cv2.rectangle(frame, (x, y), (x + width, y + height),
                      (200, 200, 200), 2)

        # Determine thumb state based on value
        # If thumb_value > 0.4 = extended (thumb_up) else neutral
        if thumb_value > 0.4:
            # Thumb up - fill entire bar green
            cv2.rectangle(frame, (x + 3, y + 3), (x + width -
                          3, y + height - 3), (0, 255, 0), -1)
            status_text = "UP"
        else:
            # Neutral - leave empty (just background)
            status_text = "NEUTRAL"

        # Draw label with outline
        text_renderer.draw_text_with_outline(
            frame, "Thumb", (x, y - 4), (0, 255, 0))

        # Draw status text with outline
        text_renderer.draw_text_with_outline(
            frame, status_text, (x, y + height + 18), (0, 255, 0))
