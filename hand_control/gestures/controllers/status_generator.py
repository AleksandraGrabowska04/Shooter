"""
Status message generator for creating human-readable gesture descriptions.
"""

from typing import List, Dict, Optional

from ...core.interfaces import ILogger
from ...core.types import (
    GestureResult, GestureType, HandState, PositionGesture, 
    OrientationGesture, MotionGesture
)


class StatusMessageGenerator:
    """
    Generates human-readable status messages from gesture data.
    """
    
    def __init__(self, logger: ILogger):
        """
        Initialize status message generator.
        
        Args:
            logger: Logger instance for debugging
        """
        self.logger = logger
        # UI state stability buffer to prevent flickering
        self._ui_state_buffer = []
        self._ui_buffer_size = 7  # Smaller buffer for UI responsiveness
        self._stable_ui_state = HandState.OPEN
    
    def generate_status_message(
        self, 
        hand_state: HandState,
        position_gesture: PositionGesture,
        orientation_gesture: OrientationGesture,
        motion_gesture: MotionGesture,
        gesture_data: Dict[GestureType, List[GestureResult]],
        special_action: Optional[str] = None
    ) -> str:
        """
        Generate human-readable status message.
        
        Args:
            hand_state: Current hand state
            position_gesture: Detected position gesture
            orientation_gesture: Primary orientation gesture
            motion_gesture: Detected motion gesture
            gesture_data: All categorized gesture data
            special_action: Special action if detected
            
        Returns:
            Human-readable status message
        """
        
        if hand_state == HandState.NONE:
            self._ui_state_buffer.clear()  # Clear buffer when no hand
            return "No hand detected"
        
        # Apply UI state buffering to prevent flickering
        self._ui_state_buffer.append(hand_state)
        if len(self._ui_state_buffer) > self._ui_buffer_size:
            self._ui_state_buffer.pop(0)
        
        # Determine stable UI state
        if len(self._ui_state_buffer) >= self._ui_buffer_size:
            fist_count = sum(1 for s in self._ui_state_buffer if s == HandState.FIST)
            if fist_count >= 2:  # Majority rule for fist
                self._stable_ui_state = HandState.FIST
            elif fist_count == 0:  # All open
                self._stable_ui_state = HandState.OPEN
            # Keep previous state if mixed (1 fist, 2 open or vice versa)
        
        # Use stable state for UI
        display_state = self._stable_ui_state
        
        # Start with hand state
        if display_state == HandState.FIST:
            base_msg = "[FIST] - Ready for control"
        else:
            base_msg = "[OPEN] Open hand"
        
        # Add position information
        if position_gesture != PositionGesture.CENTER:
            base_msg += f" - {position_gesture.value}"
        
        # Add orientation information (show all active gestures)
        all_orientations = self._get_all_orientation_gestures(gesture_data)
        if all_orientations:
            orientation_names = [g.value for g in all_orientations]
            base_msg += f" - {', '.join(orientation_names)}"
        
        # Check for special actions first (highest priority)
        if special_action == "SHOOT":
            return f"{base_msg} - [SHOOT!]"
        
        # Add motion information
        if motion_gesture != MotionGesture.STATIC:
            base_msg += f" - {motion_gesture.value}"
        
        return base_msg
    
    def _get_all_orientation_gestures(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> List[OrientationGesture]:
        """
        Get all detected orientation gestures.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            List of all detected orientation gestures
        """
        gestures = []
        if GestureType.ORIENTATION in gesture_data:
            for result in gesture_data[GestureType.ORIENTATION]:
                if result.data and 'orientation_gesture' in result.data:
                    gesture = result.data['orientation_gesture']
                    if gesture != OrientationGesture.NEUTRAL:
                        gestures.append(gesture)
        return gestures