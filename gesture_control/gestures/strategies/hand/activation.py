"""
Hand activation strategy based on simple wrist rotation (Back -> Palm).
Detects a quick rotation from back of hand to palm to activate.
"""

from typing import List, Dict, Tuple
from collections import deque
import time
from ....core.types import GestureResult, CalibrationData, GestureType
from ....core.config import ApplicationConfig


class HandActivationStrategy:
    def __init__(self, config: ApplicationConfig, history_size: int = 15):
        self.config = config
        # Buffer size: 15 frames is approx 0.5s at 30fps
        # This allows for more robust detection of the gesture
        if history_size is None or history_size <= 0:
            history_size = 15
        self.smooth_buffer = deque(maxlen=history_size)

        # Cooldown to prevent multiple triggers for the same gesture
        self.last_activation_time = 0
        self.ACTIVATION_COOLDOWN = 1.5  # Seconds

    def _is_palm_facing(self, landmarks: Dict[str, Tuple[float, float, float]]) -> bool:
        """
        Determines if the palm is facing the camera.
        Uses the cross product of Wrist->Thumb and Wrist->Pinky vectors.
        """
        if "WRIST" not in landmarks or "THUMB_CMC" not in landmarks or "PINKY_MCP" not in landmarks:
            return False

        wrist = landmarks["WRIST"]
        thumb_cmc = landmarks["THUMB_CMC"]
        pinky_mcp = landmarks["PINKY_MCP"]

        # Vector from Wrist to Thumb
        ax = thumb_cmc[0] - wrist[0]
        ay = thumb_cmc[1] - wrist[1]

        # Vector from Wrist to Pinky
        bx = pinky_mcp[0] - wrist[0]
        by = pinky_mcp[1] - wrist[1]

        # Cross product Z-component: (Ax * By) - (Ay * Bx)
        # For a standard right hand facing the camera, < 0 usually means palm is facing the camera.
        # Note: If using a mirror effect or left hand, this logic might need inversion.
        cross_product = (ax * by) - (ay * bx)

        return cross_product < 0

    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], calibration: CalibrationData) -> List[GestureResult]:
        """
        Detects a simple transition: if there is a change from back (False) to palm (True) in the buffer, the activation gesture is considered detected.
        After a successful detection, a cooldown is enabled until the buffer is fully replaced with new values.
        """
        results = []
        current_time = time.time()

        # 1. Determine instantaneous orientation
        is_palm_now = self._is_palm_facing(landmarks)
        self.smooth_buffer.append(is_palm_now)

        # If cooldown is active, do not trigger until the buffer is fully refreshed
        if hasattr(self, '_cooldown_active') and self._cooldown_active:
            # Wait until the buffer is filled with the same value (all True or all False)
            if len(set(self.smooth_buffer)) == 1:
                self._cooldown_active = False
            else:
                return results

        # Buffer must be filled
        maxlen = self.smooth_buffer.maxlen if self.smooth_buffer.maxlen is not None else 0
        if len(self.smooth_buffer) < maxlen:
            return results

        buffer_list = list(self.smooth_buffer)
        # Look for at least one transition from False to True
        gesture_detected = False
        for i in range(1, len(buffer_list)):
            if buffer_list[i-1] is False and buffer_list[i] is True:
                gesture_detected = True
                break

        if gesture_detected:
            self.last_activation_time = current_time
            self.smooth_buffer.clear()  # Clear buffer for new values
            self._cooldown_active = True  # Enable cooldown until buffer is fully replaced
            results.append(GestureResult(
                gesture_type=GestureType.ACTIVATION,
                confidence=1.0,
                data={
                    "event": "rotation_activation",
                    "info": "Back -> Palm detected (toggle)"
                }
            ))

        return results
