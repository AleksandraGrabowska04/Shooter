"""
Gesture processor for analyzing and categorizing gesture results.
"""

from typing import List, Dict, Optional

from ...core.interfaces import ILogger
from ...core.types import (
    GestureResult, GestureType, HandState, PositionGesture, 
    OrientationGesture, MotionGesture
)


class GestureProcessor:
    """
    Processes and categorizes gesture detection results.
    """
    
    def __init__(self, logger: ILogger):
        """
        Initialize gesture processor.
        
        Args:
            logger: Logger instance for debugging
        """
        self.logger = logger
        self._debug_mode = False
    
    def categorize_gestures(self, gesture_results: List[GestureResult]) -> Dict[GestureType, List[GestureResult]]:
        """
        Categorize gesture results by type, allowing multiple results per type.
        
        Args:
            gesture_results: List of detected gestures
            
        Returns:
            Dictionary mapping gesture types to sorted results
        """
        gesture_data = {}
        
        for gesture in gesture_results:
            if gesture.gesture_type not in gesture_data:
                gesture_data[gesture.gesture_type] = []
            gesture_data[gesture.gesture_type].append(gesture)
        
        # Sort each type by confidence (highest first)
        for gesture_type in gesture_data:
            gesture_data[gesture_type].sort(key=lambda g: g.confidence, reverse=True)
        
        return gesture_data
    
    def determine_hand_state(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> HandState:
        """
        Determine hand state from gesture data.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            Detected hand state
        """
        if GestureType.HAND_STATE in gesture_data and gesture_data[GestureType.HAND_STATE]:
            gesture = gesture_data[GestureType.HAND_STATE][0]
            hand_data = gesture.data
            if hand_data and 'hand_state' in hand_data and gesture.confidence >= 0.5:
                result = hand_data['hand_state']
                if self._debug_mode:
                    self.logger.debug(f"[HAND] State detected: {result.value} (confidence: {gesture.confidence:.2f}, bent_ratio: {hand_data.get('bent_ratio', 'N/A'):.2f})")
                return result
        
        if self._debug_mode:
            self.logger.debug("[WARN] No confident hand state detected - returning OPEN")
        return HandState.OPEN
    
    def determine_position_gesture(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> PositionGesture:
        """
        Determine position gesture from gesture data.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            Detected position gesture
        """
        if GestureType.POSITION in gesture_data and gesture_data[GestureType.POSITION]:
            position_data = gesture_data[GestureType.POSITION][0].data
            if position_data and 'position_gesture' in position_data:
                return position_data['position_gesture']
        
        return PositionGesture.CENTER
    
    def determine_orientation_gesture(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> OrientationGesture:
        """
        Determine primary orientation gesture from gesture data.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            Primary orientation gesture
        """
        if GestureType.ORIENTATION in gesture_data and gesture_data[GestureType.ORIENTATION]:
            # Return the highest confidence orientation gesture
            best_gesture = gesture_data[GestureType.ORIENTATION][0]
            if best_gesture.data and 'orientation_gesture' in best_gesture.data:
                return best_gesture.data['orientation_gesture']
        
        return OrientationGesture.NEUTRAL
    
    def get_all_orientation_gestures(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> List[OrientationGesture]:
        """
        Get all detected orientation gestures.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            List of all detected orientation gestures
        """
        gestures = []
        if GestureType.ORIENTATION in gesture_data:
            for result in gesture_data[GestureType.ORIENTATION]:
                if result.data and 'orientation_gesture' in result.data:
                    gesture = result.data['orientation_gesture']
                    if gesture != OrientationGesture.NEUTRAL:
                        gestures.append(gesture)
        return gestures
    
    def determine_motion_gesture(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> MotionGesture:
        """
        Determine motion gesture from gesture data.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            Detected motion gesture
        """
        if GestureType.MOTION in gesture_data and gesture_data[GestureType.MOTION]:
            motion_data = gesture_data[GestureType.MOTION][0].data
            if motion_data and 'motion_gesture' in motion_data:
                return motion_data['motion_gesture']
        
        return MotionGesture.STATIC
    
    def check_special_gestures(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> Optional[str]:
        """
        Check for special gestures like SHOOT.
        
        Args:
            gesture_data: Categorized gesture results
            
        Returns:
            Special gesture name if detected, None otherwise
        """
        if GestureType.SPECIAL in gesture_data and gesture_data[GestureType.SPECIAL]:
            special_data = gesture_data[GestureType.SPECIAL][0].data
            if special_data and 'gesture_name' in special_data:
                return special_data['gesture_name']
        
        return None
    
    def find_primary_gesture(self, gesture_results: List[GestureResult]) -> Optional[GestureResult]:
        """
        Find the primary (highest confidence) gesture.
        
        Args:
            gesture_results: List of gesture results
            
        Returns:
            Gesture with highest confidence or None
        """
        if not gesture_results:
            return None
        
        # Return gesture with highest confidence
        return max(gesture_results, key=lambda g: g.confidence)
    
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = enabled