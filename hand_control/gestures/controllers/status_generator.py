"""
Status message generator for creating human-readable gesture descriptions.
"""

from typing import List, Dict, Optional

from ...core.interfaces import ILogger
from ...core.types import (
    GestureResult, GestureType, HandState, PositionGesture
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
        self._ui_buffer_size = 7  # Buffer size for smoothing
        self._stable_ui_state = HandState.OPEN

        # For activation message persistence
        self._activation_message_until = 0.0
        self._activation_message_text = ""
        self._activation_message_duration = 0.5  # seconds

    def generate_status_message(
        self,
        hand_state: HandState,
        position_gesture: PositionGesture,
        gesture_data: Dict[GestureType, List[GestureResult]],
        special_action: Optional[str] = None
    ) -> str:
        """
        Generate human-readable status message.

        Args:
            hand_state: Current hand state
            position_gesture: Detected position gesture
            gesture_data: All categorized gesture data (including Head, Activation)
            special_action: Special action if detected (e.g. SHOOT)

        Returns:
            Human-readable status message
        """

        if hand_state == HandState.NONE:
            self._ui_state_buffer.clear()
            # Even if no hand, we might detect a face/head gesture
            head_msg = self._get_head_status(gesture_data)
            if head_msg:
                return f"No Hand | {head_msg}"
            return "No hand detected"

        # --- 1. Hand State Buffering (Hysteresis) ---
        self._ui_state_buffer.append(hand_state)
        if len(self._ui_state_buffer) > self._ui_buffer_size:
            self._ui_state_buffer.pop(0)

        # Determine stable UI state
        if len(self._ui_state_buffer) >= self._ui_buffer_size:
            fist_count = sum(
                1 for s in self._ui_state_buffer if s == HandState.FIST)
            # Majority rule or threshold to switch to FIST
            if fist_count >= 2:  # Low threshold to catch Fist quickly
                self._stable_ui_state = HandState.FIST
            elif fist_count == 0:  # Only switch back to OPEN if purely Open
                self._stable_ui_state = HandState.OPEN
            # Else: keep previous state (hysteresis)

        # --- 2. Build Message ---

        import time
        now = time.time()
        # Priority: Activation
        if GestureType.ACTIVATION in gesture_data:
            self._activation_message_until = now + self._activation_message_duration
            self._activation_message_text = "[ACTIVATION] Rotation Detected!"
            return self._activation_message_text
        # If within activation message window, show it
        if now < self._activation_message_until and self._activation_message_text:
            return self._activation_message_text

        parts = []

        # Position
        if position_gesture != PositionGesture.CENTER:
            parts.append(f"{position_gesture.name}")  # e.g. RIGHT, UP

        # Special Action (Shoot)
        if special_action == "SHOOT":
            parts.append("[SHOOT]")

        # Head Gestures
        head_msg = self._get_head_status(gesture_data)
        if head_msg:
            parts.append(f"[{head_msg}]")

        return " ".join(parts)

    def _get_head_status(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> str:
        """Helper to extract head gesture string."""
        msgs = []

        # HEAD_TILT
        if GestureType.HEAD_TILT in gesture_data:
            res_list = gesture_data[GestureType.HEAD_TILT]
            if res_list:
                res = res_list[0]
                direction = ''
                if hasattr(res, 'data') and res.data:
                    direction = res.data.get('direction', '')
                msgs.append(f"TILT {str(direction).upper()}")

        # HEAD_TURN
        if GestureType.HEAD_TURN in gesture_data:
            res_list = gesture_data[GestureType.HEAD_TURN]
            if res_list:
                res = res_list[0]
                direction = ''
                if hasattr(res, 'data') and res.data:
                    direction = res.data.get('direction', '')
                msgs.append(f"TURN {str(direction).upper()}")

        # HEAD_NOD
        if GestureType.HEAD_NOD in gesture_data:
            res_list = gesture_data[GestureType.HEAD_NOD]
            if res_list:
                res = res_list[0]
                direction = ''
                if hasattr(res, 'data') and res.data:
                    direction = res.data.get('direction', '')
                msgs.append(f"NOD {str(direction).upper()}")

        return ", ".join(msgs)
