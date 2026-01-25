from ..base import GestureDetectionStrategy
from typing import List, Dict, Tuple, Optional
import math
from ....core.types import GestureResult, CalibrationData, GestureType, RotationVector
from ....core.config import ApplicationConfig
from ....utils.math_utils import quantize_value, clamp_confidence


class HeadOrientationStrategy(GestureDetectionStrategy):
    """
    Detects head gestures: Tilt (Roll), Turn (Yaw), Nod (Pitch).
    Uses normalized metrics relative to face width to be distance-invariant.
    """

    def __init__(self, config: ApplicationConfig):
        super().__init__(config)
        head_config = config.strategies.head
        self.tilt_neutral_range = head_config.tilt_threshold_deg
        self.turn_neutral_range = head_config.turn_threshold_ratio
        self.nod_neutral_range = head_config.nod_threshold_ratio
        self.turn_gain = head_config.turn_gain
        self.tilt_gain = head_config.tilt_gain
        self.nod_gain = head_config.nod_gain

        self.tilt_scale = max(self.tilt_neutral_range * 3.0, 12.0)
        self.turn_scale = max(self.turn_neutral_range * 3.0, 0.18)
        self.nod_scale = max(self.nod_neutral_range * 3.0, 0.15)

    def _get_angle(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Returns angle in degrees between two points. Positive = Clockwise (right tilt).
        """
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle_rad = math.atan2(dy, dx)
        return math.degrees(angle_rad)

    def compute_neutral_pose(
        self,
        landmarks: Dict[str, Tuple[float, float, float]]
    ) -> Optional[Dict[str, float]]:
        metrics = self._compute_face_metrics(landmarks)
        if not metrics:
            return None
        roll_angle, yaw_ratio, pitch_ratio = metrics
        return {
            "roll": roll_angle,
            "yaw": yaw_ratio,
            "pitch": pitch_ratio
        }

    def detect(
        self,
        landmarks: Dict[str, Tuple[float, float, float]],
        calibration: CalibrationData
    ) -> List[GestureResult]:
        results = []
        if not calibration or not calibration.is_calibrated:
            return results
        if (calibration.head_roll_neutral is None or
                calibration.head_yaw_neutral is None or
                calibration.head_pitch_neutral is None):
            return results
        metrics = self._compute_face_metrics(landmarks)
        if not metrics:
            return results

        roll_angle, yaw_ratio, pitch_ratio = metrics

        roll_neutral = (
            calibration.head_roll_neutral
            if calibration and calibration.head_roll_neutral is not None
            else 0.0
        )
        yaw_neutral = (
            calibration.head_yaw_neutral
            if calibration and calibration.head_yaw_neutral is not None
            else 0.0
        )
        pitch_neutral = (
            calibration.head_pitch_neutral
            if calibration and calibration.head_pitch_neutral is not None
            else 0.0
        )

        roll_delta = roll_angle - roll_neutral
        yaw_delta = yaw_ratio - yaw_neutral
        pitch_delta = pitch_ratio - pitch_neutral

        if abs(roll_delta) <= self.tilt_neutral_range:
            roll_delta = 0.0
        if abs(yaw_delta) <= self.turn_neutral_range:
            yaw_delta = 0.0
        if abs(pitch_delta) <= self.nod_neutral_range:
            pitch_delta = 0.0

        roll_delta *= self.tilt_gain
        yaw_delta *= self.turn_gain
        pitch_delta *= self.nod_gain

        if abs(roll_delta) > 0:
            direction = "right" if roll_delta > 0 else "left"
            confidence = self._axis_confidence(abs(roll_delta), self.tilt_scale)
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_TILT,
                confidence=confidence,
                data={
                    "direction": direction,
                    "angle": roll_delta,
                    "value": roll_delta,
                    "debug": roll_angle,
                    "neutral": roll_neutral
                }
            ))

        if abs(yaw_delta) > 0:
            direction = "left" if yaw_delta < 0 else "right"
            confidence = self._axis_confidence(abs(yaw_delta), self.turn_scale)
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_TURN,
                confidence=confidence,
                data={
                    "direction": direction,
                    "ratio": yaw_delta,
                    "value": yaw_delta,
                    "debug": yaw_ratio,
                    "neutral": yaw_neutral
                }
            ))

        if abs(pitch_delta) > 0:
            direction = "down" if pitch_delta > 0 else "up"
            confidence = self._axis_confidence(abs(pitch_delta), self.nod_scale)
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_NOD,
                confidence=confidence,
                data={
                    "direction": direction,
                    "delta": pitch_delta,
                    "value": pitch_delta,
                    "debug": pitch_ratio,
                    "neutral": pitch_neutral
                }
            ))

        # Add combined rotation vector result AFTER individual results
        # Normalize values to -1.0 to 1.0 range for RotationVector
        normalized_tilt = max(-1.0, min(1.0, roll_delta / self.tilt_scale))
        normalized_turn = max(-1.0, min(1.0, yaw_delta / self.turn_scale))
        normalized_nod = max(-1.0, min(1.0, pitch_delta / self.nod_scale))
        
        # Create combined rotation vector
        rotation_vector = RotationVector(
            tilt=normalized_tilt,
            turn=normalized_turn, 
            nod=normalized_nod
        )
        
        # Add combined result if there's any head movement
        if abs(normalized_tilt) > 0 or abs(normalized_turn) > 0 or abs(normalized_nod) > 0:
            max_confidence = 0.0
            if abs(roll_delta) > 0:
                max_confidence = max(
                    max_confidence,
                    self._axis_confidence(abs(roll_delta), self.tilt_scale)
                )
            if abs(yaw_delta) > 0:
                max_confidence = max(
                    max_confidence,
                    self._axis_confidence(abs(yaw_delta), self.turn_scale)
                )
            if abs(pitch_delta) > 0:
                max_confidence = max(
                    max_confidence,
                    self._axis_confidence(abs(pitch_delta), self.nod_scale)
                )

            results.append(GestureResult(
                gesture_type=GestureType.HEAD_ORIENTATION,
                confidence=max_confidence,
                data={
                    'rotation_vector': rotation_vector,
                    # Keep individual values for UI and downstream mapping
                    'tilt': normalized_tilt,
                    'turn': normalized_turn,
                    'nod': normalized_nod
                }
            ))
        
        return results

    def _compute_face_metrics(
        self,
        landmarks: Dict[str, Tuple[float, float, float]]
    ) -> Optional[Tuple[float, float, float]]:
        required_keys = ["LEFT_EAR", "RIGHT_EAR", "NOSE"]
        if not all(k in landmarks for k in required_keys):
            return None

        left_ear = landmarks["LEFT_EAR"]
        right_ear = landmarks["RIGHT_EAR"]
        nose = landmarks["NOSE"]

        dx = right_ear[0] - left_ear[0]
        dy = right_ear[1] - left_ear[1]
        face_width = math.sqrt(dx * dx + dy * dy)
        if face_width == 0:
            return None

        roll_angle = self._get_angle(left_ear[:2], right_ear[:2])
        roll_angle = quantize_value(roll_angle, 0.5)

        mid_x = (left_ear[0] + right_ear[0]) / 2
        yaw_ratio = (nose[0] - mid_x) / face_width
        yaw_ratio = quantize_value(yaw_ratio, 0.01)

        mid_y = (left_ear[1] + right_ear[1]) / 2
        pitch_ratio = (nose[1] - mid_y) / face_width
        pitch_ratio = quantize_value(pitch_ratio, 0.01)

        return roll_angle, yaw_ratio, pitch_ratio

    def _axis_confidence(self, value: float, scale: float) -> float:
        return clamp_confidence(0.6 + (value / scale) * 0.6)
