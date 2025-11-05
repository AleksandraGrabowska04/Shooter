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
        Format debug information into readable lines.
        
        Args:
            debug_info: Dictionary containing debug data
            
        Returns:
            List of formatted debug text lines
        """
        lines = []
        
        # Calibration info with time
        calibration_time = debug_info.get('calibration_time')
        if calibration_time is not None:
            lines.append(f"Last calibration: {calibration_time:.1f}s ago")
        else:
            lines.append("Status: Not calibrated")
        
        # Hand state and confidence
        hand_state = debug_info.get('hand_state', 'NONE')
        hand_confidence = debug_info.get('hand_confidence', 0)
        lines.append(f"Hand: {hand_state} ({hand_confidence:.2f})")
        
        # Current position relative to calibration
        current_pos = debug_info.get('current_position', (0, 0, 0))
        lines.append(f"Position: ({current_pos[0]:.0f}, {current_pos[1]:.0f}, {current_pos[2]:.0f})")
        
        # Relative position from calibration center
        rel_pos = debug_info.get('relative_position', (0, 0, 0))
        if any(abs(x) > 5 for x in rel_pos):
            lines.append(f"Offset: d({rel_pos[0]:.0f}, {rel_pos[1]:.0f}, {rel_pos[2]:.0f})")
        else:
            lines.append("Offset: d(Centered)")
        
        # Orientation angles with change indicators (limited to ±60 degrees)
        thumb_angle = debug_info.get('thumb_angle_rad', 0)
        roll_angle = debug_info.get('roll_angle_rad', 0)

        # Limit angles to ±30 degrees (±0.523 radians)
        max_angle = 0.523  # 30 degrees in radians
        thumb_angle = max(-max_angle, min(max_angle, thumb_angle))
        roll_angle = max(-max_angle, min(max_angle, roll_angle))

        
        # Convert to degrees for display
        degMultiplier = 180 / 3.14159
        
        thumb_deg = thumb_angle * degMultiplier
        roll_deg = roll_angle * degMultiplier
        
        if abs(thumb_deg) > 5 or abs(roll_deg) > 5:
            # Show direction for roll (dL for left, dR for right)
            roll_dir = "dL" if roll_deg < 0 else "dR"
            lines.append(f"Angles: dT={thumb_deg:.0f}deg, {roll_dir}={abs(roll_deg):.0f}deg")
        else:
            lines.append("Angles: d(Neutral)")
        
        # Active gestures
        active_gestures = []
        
        # Add position gesture
        position = debug_info.get('position_gesture', 'None')
        if position and position != 'None' and position != 'NONE':
            active_gestures.append(position)
        
        # Add orientation gestures (multiple possible)
        orientations = debug_info.get('orientation_gestures', [])
        if orientations:
            active_gestures.extend(orientations)
        
        # Add motion gesture
        motion = debug_info.get('motion_gesture', 'None')
        if motion and motion != 'None' and motion != 'NONE':
            active_gestures.append(motion)
        
        if active_gestures:
            lines.append(f"Active: {', '.join(active_gestures)}")
        else:
            lines.append("Active: None")
        
        # Special actions (shooting, etc) with combo count
        special_actions = debug_info.get('special_actions', [])
        shoot_combo = debug_info.get('shoot_combo', 0)
        
        if special_actions and isinstance(special_actions, list):
            action_text = ', '.join(special_actions)
            # Add combo count if shooting and combo > 1
            if 'SHOOT' in special_actions and shoot_combo > 1:
                action_text = action_text.replace('SHOOT', f'SHOOT x{shoot_combo}')
            lines.append(f"Special: {action_text}")
        elif debug_info.get('is_shooting', False):
            if shoot_combo > 1:
                lines.append(f"Special: SHOOTING x{shoot_combo}")
            else:
                lines.append("Special: SHOOTING")
        elif shoot_combo > 0:
            # Show combo even if not currently shooting (for brief period after last shoot)
            lines.append(f"Special: COMBO x{shoot_combo}")
        else:
            lines.append("Special: None")
        
        return lines