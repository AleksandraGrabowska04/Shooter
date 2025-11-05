from .base import GestureDetectionStrategy
from typing import Dict, Tuple, List
import math
from ...core.types import CalibrationData, GestureResult, GestureType, OrientationGesture
from ...core.config import ApplicationConfig
from ...core.config.strategies_config import StrategiesConfig
from ...utils.math_utils import calculate_distance_2d


class OrientationDetectionStrategy(GestureDetectionStrategy):
    """Strategy for detecting orientation-based gestures."""
    
    def __init__(self, config: ApplicationConfig):
        super().__init__(config)
        # Load strategies config
        self.strategies_config = StrategiesConfig()
        self.angle_step = self.strategies_config.orientation.angle_step
    
    def _quantize_value(self, value: float, step: float) -> float:
        """Quantize value to nearest step."""
        return round(value / step) * step
    
    def _calculate_roll_angle(self, landmarks: Dict, calibration: CalibrationData) -> float:
        """Calculate roll angle from hand landmarks."""
        if not calibration.reference_orientation:
            return 0.0
        
        # Current orientation vector (index to pinky)
        index_mcp = landmarks["INDEX_FINGER_MCP"]
        pinky_mcp = landmarks["PINKY_MCP"]
        current_vector = (
            index_mcp[0] - pinky_mcp[0],
            index_mcp[1] - pinky_mcp[1],
            index_mcp[2] - pinky_mcp[2]
        )
        
        # Calculate angle with initial orientation
        initial_vector = calibration.reference_orientation.get('side_vector', (1, 0, 0))
        
        # Calculate dot product and magnitudes
        dot_product = sum(c * i for c, i in zip(current_vector, initial_vector))
        mag1 = math.sqrt(sum(x*x for x in current_vector)) + 1e-10
        mag2 = math.sqrt(sum(x*x for x in initial_vector)) + 1e-10
        
        # Calculate angle
        cos_angle = max(-1, min(1, dot_product / (mag1 * mag2)))
        angle_rad = math.acos(cos_angle)
        
        # Determine sign based on X component difference
        sign = 1 if current_vector[0] > initial_vector[0] else -1
        raw_angle = sign * angle_rad

        # Limit to ±30 degrees (±0.523 radians)
        max_angle = math.pi / 6  # 30 degrees in radians
        return max(-max_angle, min(max_angle, raw_angle))
    
    def _detect_thumb_state(self, landmarks: Dict) -> OrientationGesture:
        """Detect thumb state using position-based logic."""
        try:
            # Get key landmarks
            wrist = landmarks["WRIST"]
            thumb_tip = landmarks["THUMB_TIP"]
            index_mcp = landmarks["INDEX_FINGER_MCP"]
            middle_mcp = landmarks["MIDDLE_FINGER_MCP"]
            
            # 2D positions for stability
            thumb_pos = (thumb_tip[0], thumb_tip[1])
            index_pos = (index_mcp[0], index_mcp[1])
            middle_pos = (middle_mcp[0], middle_mcp[1])
            wrist_pos = (wrist[0], wrist[1])
            
            # Calculate distances using shared utility
            thumb_to_index = calculate_distance_2d(thumb_pos, index_pos)
            thumb_to_middle = calculate_distance_2d(thumb_pos, middle_pos)
            index_to_middle = calculate_distance_2d(index_pos, middle_pos)
            thumb_to_wrist = calculate_distance_2d(thumb_pos, wrist_pos)
            index_to_wrist = calculate_distance_2d(index_pos, wrist_pos)
            
            # Check if thumb is folded (close to other fingers)
            avg_finger_dist = (thumb_to_index + thumb_to_middle) / 2
            finger_spread = index_to_middle
            thumb_folded = avg_finger_dist < finger_spread * self.strategies_config.orientation.thumb_fold_multiplier
            
            # Check if thumb is extended (far from wrist compared to index)
            thumb_extended = thumb_to_wrist > index_to_wrist * self.strategies_config.orientation.thumb_extend_multiplier
            
            if thumb_folded and not thumb_extended:
                return OrientationGesture.THUMB_DOWN
            elif thumb_extended and not thumb_folded:
                return OrientationGesture.THUMB_UP
            else:
                return OrientationGesture.NEUTRAL
                
        except KeyError:
            return OrientationGesture.NEUTRAL
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect orientation-based gestures."""
        try:
            if not calibration.is_calibrated:
                return [GestureResult(
                    gesture_type=GestureType.ORIENTATION,
                    confidence=1.0,
                    data={'orientation_gesture': OrientationGesture.NEUTRAL}
                )]
            
            # Calculate roll angle
            roll_angle = self._calculate_roll_angle(landmarks, calibration)
            quantized_roll = self._quantize_value(roll_angle, self.angle_step)
            
            # Detect thumb state
            thumb_state = self._detect_thumb_state(landmarks)
            
            # Detect multiple orientation gestures simultaneously
            roll_threshold = self.config.gestures.orientation_threshold * (math.pi / 180)
            results = []
            
            # Always include basic orientation data
            base_data = {
                'roll_angle': quantized_roll,
                'thumb_state': thumb_state
            }
            
            # Add thumb gesture if detected
            if thumb_state in [OrientationGesture.THUMB_UP, OrientationGesture.THUMB_DOWN]:
                results.append(GestureResult(
                    gesture_type=GestureType.ORIENTATION,
                    confidence=0.9,
                    data={
                        'orientation_gesture': thumb_state,
                        **base_data
                    }
                ))
            
            # Add roll gesture if detected (can be simultaneous with thumb)
            if abs(quantized_roll) > roll_threshold:
                roll_gesture = (OrientationGesture.ROLL_LEFT 
                               if quantized_roll < 0 
                               else OrientationGesture.ROLL_RIGHT)
                roll_confidence = min(1.0, abs(quantized_roll) / roll_threshold)
                
                results.append(GestureResult(
                    gesture_type=GestureType.ORIENTATION,
                    confidence=roll_confidence,
                    data={
                        'orientation_gesture': roll_gesture,
                        **base_data
                    }
                ))
            
            # If no gestures detected, return neutral
            if not results:
                results.append(GestureResult(
                    gesture_type=GestureType.ORIENTATION,
                    confidence=0.8,
                    data={
                        'orientation_gesture': OrientationGesture.NEUTRAL,
                        **base_data
                    }
                ))
            
            return results
            
        except Exception as e:
            return []
