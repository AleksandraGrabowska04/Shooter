from ..base import GestureDetectionStrategy
from typing import List, Dict, Tuple
import math
from ....core.types import GestureResult, CalibrationData, GestureType
from ....core.config import ApplicationConfig
from ....utils.math_utils import quantize_value, clamp_confidence
# Assuming StrategiesConfig exists and has head_orientation settings,
# otherwise we use defaults in __init__
try:
    from ....core.config.strategies_config import StrategiesConfig
except ImportError:
    StrategiesConfig = None


class HeadOrientationStrategy(GestureDetectionStrategy):
    """
    Detects head gestures: Tilt (Roll), Turn (Yaw), Nod (Pitch).
    Uses normalized metrics relative to face width to be distance-invariant.
    """

    def __init__(self, config: ApplicationConfig):
        super().__init__(config)

        # Load config or set defaults
        if StrategiesConfig:
            self.strategies_config = StrategiesConfig()
            # Assuming structure: self.strategies_config.head.tilt_threshold etc.
            # Using safe defaults if specific config structure isn't known yet
            self.tilt_threshold = getattr(
                self.strategies_config, 'head_tilt_threshold', 10.0)  # degrees
            self.turn_threshold = getattr(
                self.strategies_config, 'head_turn_threshold_ratio', 0.20)  # 20% of face width
            self.nod_threshold = getattr(
                self.strategies_config, 'head_nod_threshold_ratio', 0.15)  # 15% of face width
        else:
            self.tilt_threshold = 10.0
            self.turn_threshold = 0.20
            self.nod_threshold = 0.15

    def _get_angle(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """
        Returns angle in degrees between two points. Positive = Clockwise (right tilt).
        """
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        angle_rad = math.atan2(dy, dx)
        return math.degrees(angle_rad)

    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], calibration: CalibrationData) -> List[GestureResult]:
        results = []
        required_keys = ["LEFT_EAR", "RIGHT_EAR", "NOSE"]
        if not all(k in landmarks for k in required_keys):
            return results

        left_ear = landmarks["LEFT_EAR"]
        right_ear = landmarks["RIGHT_EAR"]
        nose = landmarks["NOSE"]

        # 1. Calculate face width (distance between ears)
        # Used to normalize offsets so detection works at any distance
        dx = right_ear[0] - left_ear[0]
        dy = right_ear[1] - left_ear[1]
        face_width = math.sqrt(dx*dx + dy*dy)

        if face_width == 0:
            return results

        # --- ROLL (Head Tilt) ---
        # Angle of the line connecting ears
        roll_angle = self._get_angle(left_ear[:2], right_ear[:2])
        roll_angle = quantize_value(roll_angle, 0.5)

        if abs(roll_angle) > self.tilt_threshold:
            # If Y points down:
            # angle > 0 means right ear is lower (larger Y) -> TILT RIGHT
            # angle < 0 means left ear is lower -> TILT LEFT
            direction = "right" if roll_angle > 0 else "left"
            confidence = clamp_confidence(abs(roll_angle) / 45.0)
            # Pass raw roll_angle as value, normalization for UI will be done in debug_info
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_TILT,
                confidence=confidence,
                data={
                    "direction": direction,
                    "angle": roll_angle,
                    "value": roll_angle,
                    "debug": roll_angle
                }
            ))

        # --- YAW (Head Turn) ---
        # Horizontal position of nose relative to center of ears
        mid_x = (left_ear[0] + right_ear[0]) / 2
        raw_yaw = nose[0] - mid_x

        # Normalize by face width
        yaw_ratio = raw_yaw / face_width
        yaw_ratio = quantize_value(yaw_ratio, 0.01)

        if abs(yaw_ratio) > self.turn_threshold:
            # Nose moves left (smaller X) -> ratio negative -> LEFT
            direction = "left" if yaw_ratio < 0 else "right"
            # Confidence based on how much we exceeded threshold
            excess = abs(yaw_ratio) - self.turn_threshold
            conf = clamp_confidence(
                min(excess / (self.turn_threshold), 1.0) + 0.5)
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_TURN,
                confidence=conf,
                data={
                    "direction": direction,
                    "ratio": yaw_ratio,
                    "value": yaw_ratio
                }
            ))

        # --- PITCH (Head Nod) ---
        # Vertical position of nose relative to center of ears
        mid_y = (left_ear[1] + right_ear[1]) / 2
        raw_pitch = nose[1] - mid_y

        # Normalize by face width (approximation, as face height varies more, but width is stable reference)
        pitch_ratio = raw_pitch / face_width
        pitch_ratio = quantize_value(pitch_ratio, 0.01)

        # Pitch ratio usually has an offset even when neutral (nose is below ears).
        # Ideally, this should be calibrated relative to 'neutral' pose in CalibrationData.
        # Here we use a relative delta if calibration exists, otherwise raw heuristic.
        reference_pitch = 0.0
        if calibration and calibration.head_pitch_neutral:
            # Use calibration value if available
            reference_pitch = calibration.head_pitch_neutral

        # Large positive delta -> looking down, small or negative -> looking up
        pitch_delta = pitch_ratio - reference_pitch
        if abs(pitch_delta) > self.nod_threshold:
            direction = "down" if pitch_delta > 0 else "up"
            confidence = clamp_confidence(abs(pitch_delta) / 0.3)
            # Pass raw pitch_delta as value, normalization for UI will be done in debug_info
            results.append(GestureResult(
                gesture_type=GestureType.HEAD_NOD,
                confidence=confidence,
                data={
                    "direction": direction,
                    "delta": pitch_delta,
                    "value": pitch_delta,
                    "debug": pitch_delta
                }
            ))
        return results
