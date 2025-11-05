from .base import GestureDetectionStrategy
from typing import Dict, Tuple, List
from ...core.types import CalibrationData, GestureResult, GestureType, MotionGesture
from ...core.config import ApplicationConfig
from ...core.config.strategies_config import StrategiesConfig
from ...utils.math_utils import clamp_confidence


class MotionDetectionStrategy(GestureDetectionStrategy):
    """Strategy for detecting motion-based gestures."""
    
    def __init__(self, config: ApplicationConfig):
        super().__init__(config)
        self.motion_history: List[float] = []
        self.max_history = config.gestures.motion_history_size
        # Load strategies config
        self.strategies_config = StrategiesConfig()
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect motion-based gestures."""
        try:
            if "WRIST" not in landmarks:
                return []
            
            current_z = landmarks["WRIST"][2]
            
            # Add to motion history
            self.motion_history.append(current_z)
            if len(self.motion_history) > self.max_history:
                self.motion_history.pop(0)
            
            # Need at least 2 frames for motion detection
            if len(self.motion_history) < 2:
                return [GestureResult(
                    gesture_type=GestureType.MOTION,
                    confidence=1.0,
                    data={'motion_gesture': MotionGesture.STATIC}
                )]
            
            # Calculate Z-axis movement
            z_change = current_z - self.motion_history[-2]
            motion_threshold = self.config.gestures.motion_threshold
            
            if abs(z_change) > motion_threshold:
                if z_change > 0:
                    motion_gesture = MotionGesture.BACKWARD
                else:
                    motion_gesture = MotionGesture.FORWARD
                
                confidence = clamp_confidence(abs(z_change) / motion_threshold)
            else:
                motion_gesture = MotionGesture.STATIC
                confidence = 1.0 - (abs(z_change) / motion_threshold)
            
            return [GestureResult(
                gesture_type=GestureType.MOTION,
                confidence=confidence,
                data={
                    'motion_gesture': motion_gesture,
                    'z_change': z_change,
                    'motion_magnitude': abs(z_change)
                }
            )]
            
        except Exception as e:
            return []
