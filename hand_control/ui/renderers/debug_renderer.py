"""
Debug information renderer for development and troubleshooting.
"""

import numpy as np
from typing import Dict, List, Any


class DebugRenderer:
    """
    Handles rendering of debug information and development data.
    """

    def __init__(self, line_spacing: int = 25, debug_start_y: int = 60):
        """
        Initialize debug renderer.

        Args:
            line_spacing: Space between debug text lines
            debug_start_y: Starting Y position for debug text
        """
        self.line_spacing = line_spacing
        self.debug_start_y = debug_start_y

    def draw_debug_info(self, frame: np.ndarray, debug_info: Dict[str, Any],
                        text_renderer, debug_color=(0, 255, 255)) -> None:
        """
        Draw formatted debug information on frame.

        Args:
            frame: OpenCV frame to draw on
            debug_info: Dictionary containing debug data
            text_renderer: Text renderer instance
            debug_color: Color for debug text in BGR format
        """
        if not isinstance(frame, np.ndarray) or not debug_info:
            return

        try:
            lines = self._format_debug_info(debug_info)
            text_renderer.draw_multiline_text(
                frame,
                lines,
                (10, self.debug_start_y),
                debug_color
            )
        except Exception:
            pass

    def _format_debug_info(self, debug_info: Dict[str, Any]) -> List[str]:
        """
        Format debug information into readable lines from summary/core data only.
        Args:
            debug_info: Dictionary containing debug data (should be summary from game_controller)
        Returns:
            List of formatted debug text lines
        """
        lines = []
        # Calibration info
        calibration_time = debug_info.get('calibration_time')
        if calibration_time is not None:
            lines.append(f"Last calibration: {calibration_time:.1f}s ago")
        else:
            lines.append("Status: Not calibrated")

        # Hand state
        hand_state = debug_info.get('hand_state', 'NONE')
        lines.append(f"Hand: {hand_state}")

        # Position gesture
        position = debug_info.get('position', None)
        if position:
            lines.append(f"Position: {position}")

        # Special action (e.g. SHOOT)
        special = debug_info.get('special', None)
        if special:
            lines.append(f"Special: {special}")

        # Head gestures summary
        head = debug_info.get('head', None)
        if head:
            lines.append(f"Head: {head}")

        return lines
