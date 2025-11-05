from .base import GestureDetectionStrategy
from typing import Dict, Tuple, List
import math
from ...core.types import CalibrationData, GestureResult, GestureType, PositionGesture
from ...core.config import ApplicationConfig
from ...core.config.strategies_config import StrategiesConfig
from ...utils.math_utils import quantize_value, calculate_distance_3d, normalize_confidence


class PositionDetectionStrategy(GestureDetectionStrategy):
    """Strategy for detecting position-based gestures."""
    
    def __init__(self, config: ApplicationConfig):
        super().__init__(config)
        # Load strategies config
        self.strategies_config = StrategiesConfig()
        self.position_step = self.strategies_config.position.position_step
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect position-based gestures relative to calibration."""
        try:
            if not calibration.is_calibrated or "WRIST" not in landmarks:
                return [GestureResult(
                    gesture_type=GestureType.POSITION,
                    confidence=1.0,
                    data={'position_gesture': PositionGesture.CENTER}
                )]
            
            if not calibration.reference_position:
                return []
            
            current_wrist = landmarks["WRIST"]
            initial_pos = calibration.reference_position
            
            # Calculate displacement (landmarks already quantized in recognizer)
            dx = current_wrist[0] - initial_pos[0]
            dy = current_wrist[1] - initial_pos[1]
            
            # Calculate distance from center with quantization
            raw_distance = math.sqrt(dx*dx + dy*dy)  # Keep 2D for position detection
            
            # Apply deadzone
            deadzone = self.config.gestures.position_threshold * 100  # Convert to pixels
            if raw_distance <= deadzone:
                position_gesture = PositionGesture.CENTER
                confidence = 1.0 - (raw_distance / deadzone) * self.strategies_config.position.center_confidence_multiplier
            else:
                # Determine primary direction
                if abs(dx) > abs(dy):
                    position_gesture = PositionGesture.RIGHT if dx > 0 else PositionGesture.LEFT
                else:
                    position_gesture = PositionGesture.DOWN if dy > 0 else PositionGesture.UP
                
                # Calculate confidence based on distance from deadzone
                confidence = min(1.0, (raw_distance - deadzone) / (deadzone * self.strategies_config.position.edge_confidence_multiplier) + self.strategies_config.position.edge_confidence_base)
            
            return [GestureResult(
                gesture_type=GestureType.POSITION,
                confidence=confidence,
                data={
                    'position_gesture': position_gesture,
                    'displacement': (dx, dy),
                    'distance': raw_distance
                }
            )]
            
        except Exception as e:
            return []
