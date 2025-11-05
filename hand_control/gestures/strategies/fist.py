from .base import GestureDetectionStrategy
from typing import Dict, Tuple, List
from ...core.types import CalibrationData, GestureResult, GestureType, HandState
from ...core.config.strategies_config import StrategiesConfig
from ...utils.math_utils import calculate_distance_2d, clamp_confidence


class FistDetectionStrategy(GestureDetectionStrategy):
    """Strategy for detecting fist/hand state gestures."""
    
    # Finger landmark mapping (exclude thumb for fist detection)
    # Thumb has different mechanics and shouldn't be required for fist detection
    MAIN_FINGER_TIPS = ["INDEX_FINGER_TIP", "MIDDLE_FINGER_TIP", 
                       "RING_FINGER_TIP", "PINKY_TIP"]
    MAIN_FINGER_MCPS = ["INDEX_FINGER_MCP", "MIDDLE_FINGER_MCP", 
                       "RING_FINGER_MCP", "PINKY_MCP"]
    
    # Keep thumb separate for debugging purposes
    THUMB_TIP = "THUMB_TIP"
    THUMB_MCP = "THUMB_MCP"
    
    def __init__(self, config):
        super().__init__(config)
        # Load strategies config
        self.strategies_config = StrategiesConfig()
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect fist vs open hand state using simple 2D distance method (original working approach)."""
        try:
            if "WRIST" not in landmarks:
                return []
            
            wrist = landmarks["WRIST"]
            bent_main_fingers = 0
            total_main_fingers = 0
            finger_details = []
            
            # Use the original working method: 2D distance from tip/MCP to wrist
            # Check main fingers (index, middle, ring, pinky) - EXCLUDE THUMB
            for tip_name, mcp_name in zip(self.MAIN_FINGER_TIPS, self.MAIN_FINGER_MCPS):
                if tip_name in landmarks and mcp_name in landmarks:
                    tip_pos = landmarks[tip_name]
                    mcp_pos = landmarks[mcp_name]
                    
                    # Calculate 2D distances to wrist (ignore Z-coordinate for stability)
                    tip_dist = calculate_distance_2d((tip_pos[0], tip_pos[1]), (wrist[0], wrist[1]))
                    mcp_dist = calculate_distance_2d((mcp_pos[0], mcp_pos[1]), (wrist[0], wrist[1]))
                    
                    # More lenient fist multiplier for better rotation stability
                    fist_multiplier = self.strategies_config.fist.main_finger_multiplier
                    is_bent = tip_dist < (mcp_dist * fist_multiplier)
                    
                    finger_type = tip_name.split('_')[0]
                    finger_details.append(f"{finger_type}:{is_bent}({tip_dist:.1f}<{mcp_dist*fist_multiplier:.1f})")
                    
                    if is_bent:
                        bent_main_fingers += 1
                    
                    total_main_fingers += 1
            
            # Also check thumb for debugging (but don't use in fist calculation)
            thumb_info = "N/A"
            if self.THUMB_TIP in landmarks and self.THUMB_MCP in landmarks:
                thumb_tip = landmarks[self.THUMB_TIP]
                thumb_mcp = landmarks[self.THUMB_MCP]
                
                thumb_tip_dist = calculate_distance_2d((thumb_tip[0], thumb_tip[1]), (wrist[0], wrist[1]))
                thumb_mcp_dist = calculate_distance_2d((thumb_mcp[0], thumb_mcp[1]), (wrist[0], wrist[1]))
                
                thumb_bent = thumb_tip_dist < (thumb_mcp_dist * self.strategies_config.fist.thumb_bend_multiplier)
                thumb_info = f"THUMB:{thumb_bent}({thumb_tip_dist:.1f}<{thumb_mcp_dist*0.85:.1f})"
            
            # Determine hand state based on main fingers ONLY (no thumb)
            if total_main_fingers == 0:
                return []
            
            bent_ratio = bent_main_fingers / total_main_fingers
            
            # Ultra stable fist detection - require only 1 out of 4 fingers for maximum rotation stability
            threshold = self.strategies_config.fist.bent_threshold
            if bent_ratio >= threshold:
                confidence = clamp_confidence(bent_ratio + self.strategies_config.fist.bent_confidence_boost)
                hand_state = HandState.FIST
                print(f"[FIST] DETECTED: bent_ratio={bent_ratio:.2f} ({bent_main_fingers}/{total_main_fingers}), main_fingers={finger_details}, thumb={thumb_info}")
            elif bent_ratio <= threshold:
                confidence = clamp_confidence((1.0 - bent_ratio) + self.strategies_config.fist.open_confidence_boost)
                hand_state = HandState.OPEN
                if bent_main_fingers == 0:
                    print(f"[OPEN] HAND: bent_ratio={bent_ratio:.2f} ({bent_main_fingers}/{total_main_fingers}), main_fingers={finger_details}, thumb={thumb_info}")
            else:
                confidence = self.strategies_config.fist.neutral_confidence
                hand_state = HandState.OPEN
                print(f"[INTER] MEDIATE: bent_ratio={bent_ratio:.2f} ({bent_main_fingers}/{total_main_fingers}), main_fingers={finger_details}, thumb={thumb_info}")
            
            return [GestureResult(
                gesture_type=GestureType.HAND_STATE,
                confidence=confidence,
                data={
                    'hand_state': hand_state,
                    'bent_fingers': bent_main_fingers,  # Only main fingers count
                    'total_fingers': total_main_fingers,  # Only main fingers count
                    'bent_ratio': bent_ratio,
                    'thumb_info': thumb_info  # Thumb info for debugging
                }
            )]
            
        except Exception as e:
            print(f"❌ FistDetectionStrategy error: {e}")
            return []
