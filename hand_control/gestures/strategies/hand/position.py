from ..base import GestureDetectionStrategy
from typing import Dict, Tuple, List
import math
from ....core.types import CalibrationData, GestureResult, GestureType, PositionGesture, MovementVector, Vector2D
from ....core.config import ApplicationConfig
from ....core.config.strategies_config import StrategiesConfig
from ....utils.math_utils import quantize_value


class HandPositionStrategy(GestureDetectionStrategy):
    """Strategy for detecting position-based gestures (Virtual Joystick)."""

    def __init__(self, config: ApplicationConfig):
        super().__init__(config)
        self.strategies_config = StrategiesConfig()
        self.position_step = self.strategies_config.position.position_step

    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], calibration: CalibrationData) -> List[GestureResult]:
        """Detect position-based gestures relative to calibration."""
        try:
            if not calibration.is_calibrated or "WRIST" not in landmarks:
                # Default to CENTER if not ready
                return [GestureResult(
                    gesture_type=GestureType.POSITION_VECTOR,
                    confidence=1.0,
                    data={
                        'movement_vector': MovementVector(displacement=Vector2D(0.0, 0.0)),
                        'position_gesture': PositionGesture.CENTER
                    }
                )]

            if not calibration.reference_position:
                return []

            current_wrist = landmarks["WRIST"]
            initial_pos = calibration.reference_position

            # 1. Calculate raw displacement (Normalized coords 0.0-1.0)
            # Note: Y-axis in MediaPipe increases downwards (Top=0, Bottom=1)
            raw_dx = current_wrist[0] - initial_pos[0]
            raw_dy = current_wrist[1] - initial_pos[1]

            # 2. Quantize displacement to reduce jitter/micro-movements
            dx = quantize_value(raw_dx, self.position_step)
            dy = quantize_value(raw_dy, self.position_step)

            # 3. Calculate Euclidean distance from center
            distance = math.sqrt(dx * dx + dy * dy)

            # 4. Handle Deadzone
            # REMOVED "* 100" assuming config threshold matches landmark scale (0.0-1.0)
            deadzone = self.config.gestures.position_threshold

            position_gesture = PositionGesture.CENTER
            confidence = 0.0

            # 5. Logic for Direction
            if distance <= deadzone:
                # Inside deadzone -> CENTER
                position_gesture = PositionGesture.CENTER
                # Higher confidence closer to absolute 0,0
                confidence = 1.0 - \
                    (distance / deadzone) * \
                    self.strategies_config.position.center_confidence_multiplier
            else:
                # Outside deadzone -> Determine Direction
                # Check Dominant Axis
                if abs(dx) > abs(dy):
                    position_gesture = PositionGesture.RIGHT if dx > 0 else PositionGesture.LEFT
                else:
                    position_gesture = PositionGesture.DOWN if dy > 0 else PositionGesture.UP

                # Calculate confidence relative to how far out we are
                # Confidence grows as we move away from deadzone boundary
                conf_val = (distance - deadzone) / (deadzone *
                                                    self.strategies_config.position.edge_confidence_multiplier)
                confidence = min(
                    1.0, conf_val + self.strategies_config.position.edge_confidence_base)

            # 6. Handle Max Distance (Clamping)
            # Instead of resetting to CENTER, we clamp the values but keep the direction.
            max_distance = self.strategies_config.position.max_distance_from_calibration
            is_out_of_range = False

            if distance > max_distance:
                is_out_of_range = True
                # Clamp the displacement vector to the max radius circle
                scale = max_distance / distance
                dx = dx * scale
                dy = dy * scale
                distance = max_distance
                # Keep the calculated direction, don't force CENTER!
                # But maybe cap confidence at 1.0

            # 7. Create movement vector and include directional info
            movement_vector = MovementVector(displacement=Vector2D(dx, dy))

            return [GestureResult(
                gesture_type=GestureType.POSITION_VECTOR,
                confidence=confidence,
                data={
                    'movement_vector': movement_vector,
                    'displacement': (dx, dy),
                    'distance': distance,
                    'out_of_range': is_out_of_range,
                    'position_gesture': position_gesture
                }
            )]

        except Exception:
            return []
