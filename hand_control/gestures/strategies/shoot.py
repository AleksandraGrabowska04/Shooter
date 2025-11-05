from .base import GestureDetectionStrategy
from typing import Dict, Tuple, List
from ...core.types import CalibrationData, GestureResult, GestureType
from ...core.config.strategies_config import StrategiesConfig


class ShootDetectionStrategy(GestureDetectionStrategy):
    """Strategy for detecting shoot gesture (transition from thumb_up to neutral)."""
    
    def __init__(self, config):
        """Initialize shoot detection strategy."""
        super().__init__(config)
        # Load strategies config
        self.strategies_config = StrategiesConfig()
        
        self.last_thumb_state = None
        self.thumb_transition_buffer = []
        self.buffer_size = 3  # Small buffer for responsive shooting
        
        # Sequential shooting tracking and throttling
        self.consecutive_shots = 0
        self.last_shoot_time = 0
        self.shoot_sequence_timeout = self.strategies_config.shoot.sequence_timeout
        self.shoot_throttle_time = self.strategies_config.shoot.min_fist_duration
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect shoot gesture based on thumb_up to neutral transition."""
        try:
            import time
            from ...core.types import OrientationGesture
            from .orientation import OrientationDetectionStrategy
            
            current_time = time.time()
            
            # Create orientation detector to get thumb state
            orientation_detector = OrientationDetectionStrategy(self.config)
            orientation_results = orientation_detector.detect(landmarks, calibration)
            
            current_thumb_state = OrientationGesture.NEUTRAL
            
            # Find current thumb state from orientation results
            for result in orientation_results:
                if (result.data and 'orientation_gesture' in result.data):
                    gesture = result.data['orientation_gesture']
                    if gesture == OrientationGesture.THUMB_UP:
                        current_thumb_state = OrientationGesture.THUMB_UP
                        break
            
            # Add to buffer
            self.thumb_transition_buffer.append(current_thumb_state)
            if len(self.thumb_transition_buffer) > self.buffer_size:
                self.thumb_transition_buffer.pop(0)
            
            # Check for thumb_up -> neutral transition
            shoot_detected = False
            
            if (len(self.thumb_transition_buffer) >= 2 and
                self.last_thumb_state == OrientationGesture.THUMB_UP and
                current_thumb_state == OrientationGesture.NEUTRAL):
                
                # Check throttle period to prevent rapid firing
                if current_time - self.last_shoot_time >= self.shoot_throttle_time:
                    # Confirm transition with buffer check
                    thumb_up_count = sum(1 for state in self.thumb_transition_buffer[-3:] 
                                       if state == OrientationGesture.THUMB_UP)
                    if thumb_up_count >= 1:  # At least one thumb_up in recent history
                        shoot_detected = True
                        
                        # Handle consecutive shots tracking
                        if current_time - self.last_shoot_time <= self.shoot_sequence_timeout:
                            # Within sequence timeout - increment consecutive shots
                            self.consecutive_shots += 1
                        else:
                            # Start new sequence
                            self.consecutive_shots = 1
                        
                        self.last_shoot_time = current_time
            
            # Check if sequence has timed out (reset counter)
            if (self.consecutive_shots > 0 and 
                current_time - self.last_shoot_time > self.shoot_sequence_timeout):
                self.consecutive_shots = 0
            
            # Update last state
            self.last_thumb_state = current_thumb_state
            
            if shoot_detected:
                return [GestureResult(
                    gesture_type=GestureType.SPECIAL,
                    confidence=0.9,
                    data={
                        'gesture_name': 'SHOOT',
                        'transition': 'thumb_up_to_neutral',
                        'current_state': current_thumb_state.value,
                        'buffer': [s.value for s in self.thumb_transition_buffer],
                        'consecutive_shots': self.consecutive_shots,
                        'sequence_active': self.consecutive_shots > 1
                    }
                )]
            
            return []
            
        except Exception as e:
            return []
    
    def _calculate_distance(self, point1: Tuple[float, float, float], 
                          point2: Tuple[float, float, float]) -> float:
        """Calculate 3D distance between two points."""
        return ((point1[0] - point2[0])**2 + 
                (point1[1] - point2[1])**2 + 
                (point1[2] - point2[2])**2) ** 0.5
