from ..base import GestureDetectionStrategy
from typing import Dict, Tuple, List
from ....core.types import CalibrationData, GestureResult, GestureType, HandState
from ....core.config.strategies_config import StrategiesConfig
from ....utils.math_utils import calculate_distance_2d, clamp_confidence


class HandFistStrategy(GestureDetectionStrategy):
    """Strategy for detecting fist/hand state gestures."""
    
    # Finger landmark mapping (exclude thumb for fist detection robustness)
    MAIN_FINGER_TIPS = [
        "INDEX_FINGER_TIP", "MIDDLE_FINGER_TIP", "RING_FINGER_TIP", "PINKY_TIP"
    ]
    MAIN_FINGER_MCPS = [
        "INDEX_FINGER_MCP", "MIDDLE_FINGER_MCP", "RING_FINGER_MCP", "PINKY_MCP"
    ]
    
    def __init__(self, config):
        super().__init__(config)
        self.strategies_config = StrategiesConfig()
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect fist vs open hand state using simple 2D distance method."""
        try:
            if "WRIST" not in landmarks:
                return []

            wrist = landmarks["WRIST"]
            bent_main_fingers = 0
            total_main_fingers = 0
            finger_details = []

            # Check main fingers (index, middle, ring, pinky)
            for tip_name, mcp_name in zip(self.MAIN_FINGER_TIPS, self.MAIN_FINGER_MCPS):
                if tip_name in landmarks and mcp_name in landmarks:
                    tip_pos = landmarks[tip_name]
                    mcp_pos = landmarks[mcp_name]

                    # Calculate distances to wrist
                    tip_dist = calculate_distance_2d((tip_pos[0], tip_pos[1]), (wrist[0], wrist[1]))
                    mcp_dist = calculate_distance_2d((mcp_pos[0], mcp_pos[1]), (wrist[0], wrist[1]))

                    # Heuristic: If tip is closer to wrist than MCP (scaled), it's bent.
                    fist_multiplier = self.strategies_config.fist.main_finger_multiplier
                    is_bent = tip_dist < (mcp_dist * fist_multiplier)

                    finger_type = tip_name.split('_')[0]
                    state_char = "V" if is_bent else "|"
                    finger_details.append(f"{finger_type}:{state_char}")

                    if is_bent:
                        bent_main_fingers += 1

                    total_main_fingers += 1

            if total_main_fingers == 0:
                return []

            bent_ratio = bent_main_fingers / total_main_fingers
            
            # --- Logic Fix: Thresholds for Fist and Open ---
            # Ideally, use two thresholds. Assuming config has 'bent_threshold' (e.g., 0.8).
            # We will infer an 'open_threshold' (e.g., 0.2) or use a logic that allows for Neutral.
            
            fist_threshold = self.strategies_config.fist.bent_threshold
            # If not defined in config, assume Open is opposite of Fist with some buffer
            # e.g., if Fist is > 0.8, Open is < 0.4. 
            # For now, let's stick to the user's variable but fix the flow.
            
            confidence = 0.0
            hand_state = HandState.OPEN # Default if in the "gray zone"

            if bent_ratio >= fist_threshold:
                # Clearly a Fist
                base_conf = bent_ratio
                confidence = clamp_confidence(base_conf + self.strategies_config.fist.bent_confidence_boost)
                hand_state = HandState.FIST
                
            elif bent_ratio <= (1.0 - fist_threshold): 
                # Clearly Open (assuming symmetry, e.g., if fist is >0.8, open is <0.2)
                # Or you can hardcode a safe threshold like 0.2 or 0.3
                base_conf = 1.0 - bent_ratio
                confidence = clamp_confidence(base_conf + self.strategies_config.fist.open_confidence_boost)
                hand_state = HandState.OPEN
                
            else:
                # "Gray Zone" - 2 or 3 fingers bent. 
                # Can be treated as Low Confidence Open or Neutral.
                confidence = self.strategies_config.fist.neutral_confidence
                hand_state = HandState.OPEN # Fallback, but with low confidence
                
                # Optional: You might want to return NO result if it's ambiguous
                # return [] 

            return [GestureResult(
                gesture_type=GestureType.HAND_STATE,
                confidence=confidence,
                data={
                    'hand_state': hand_state,
                    'bent_fingers': bent_main_fingers,
                    'total_fingers': total_main_fingers,
                    'bent_ratio': bent_ratio,
                    'finger_details': finger_details
                }
            )]

        except Exception as e:
            return []