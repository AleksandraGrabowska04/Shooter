"""
Gesture processor for analyzing and categorizing gesture results.
"""

from typing import List, Dict, Optional, Any

from ...core.interfaces import ILogger
from ...core.types import (
    GestureResult, GestureType, HandState, PositionGesture
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
            gesture_data[gesture_type].sort(
                key=lambda g: g.confidence, reverse=True)

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
                    self.logger.debug(
                        f"[HAND] State detected: {result.value} (confidence: {gesture.confidence:.2f}, bent_ratio: {hand_data.get('bent_ratio', 'N/A'):.2f})")
                return result

        if self._debug_mode:
            self.logger.debug(
                "[WARN] No confident hand state detected - returning OPEN")
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

    def check_activation_gesture(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> bool:
        """
        Check for activation/rotation gesture.

        Args:
            gesture_data: Categorized gesture results

        Returns:
            True if activation gesture detected
        """
        # Looking for ACTIVATION type
        if GestureType.ACTIVATION in gesture_data and gesture_data[GestureType.ACTIVATION]:
            return True
        return False

    def get_head_gestures(self, gesture_data: Dict[GestureType, List[GestureResult]]) -> Dict[str, Any]:
        """
        Extract active head gestures (Tilt, Turn, Nod).

        Args:
            gesture_data: Categorized gesture results

        Returns:
            Dictionary with keys 'tilt', 'turn', 'nod' containing details if present.
        """
        head_gestures = {}

        # 1. Head Tilt
        if GestureType.HEAD_TILT in gesture_data:
            res = gesture_data[GestureType.HEAD_TILT][0]
            if res.data:
                head_gestures['tilt'] = {
                    'direction': res.data.get('direction'),
                    'angle': res.data.get('angle', 0.0)
                }

        # 2. Head Turn
        if GestureType.HEAD_TURN in gesture_data:
            res = gesture_data[GestureType.HEAD_TURN][0]
            if res.data:
                head_gestures['turn'] = {
                    'direction': res.data.get('direction'),
                    'value': res.data.get('ratio', 0.0)
                }

        # 3. Head Nod
        if GestureType.HEAD_NOD in gesture_data:
            res = gesture_data[GestureType.HEAD_NOD][0]
            if res.data:
                head_gestures['nod'] = {
                    'direction': res.data.get('direction'),
                    'value': res.data.get('offset', 0.0)
                }

        return head_gestures

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
