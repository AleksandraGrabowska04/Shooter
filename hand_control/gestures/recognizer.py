"""
Enhanced gesture recognition system with comprehensive gesture support.
"""

import time
from typing import Dict, List, Optional, Tuple

from ..core.interfaces import IGestureRecognizer
from ..core.config import ApplicationConfig
from ..core.config.debug_config import DebugConfig
from ..core.types import (
    GestureResult, CalibrationData
)
from ..utils.math_utils import quantize_landmarks

from .strategies.hand import HandFistStrategy, HandPositionStrategy, HandActivationStrategy
from .strategies.head import HeadOrientationStrategy


class GestureRecognizer(IGestureRecognizer):
    """
    Gesture recognition system with comprehensive gesture support.

    Uses multiple detection strategies for different gesture types:
    - Fist detection for hand state
    - Position detection for spatial gestures
    - Orientation detection for roll/thumb gestures  
    - Motion detection for punch gestures
    """

    def __init__(self, config: ApplicationConfig):
        """Initialize gesture recognizer."""
        self.config = config
        self.calibration_data = CalibrationData()
        # Load debug config
        self.debug_config = DebugConfig()

        # Initialize detection strategies
        self.fist_detector = HandFistStrategy(config)
        self.position_detector = HandPositionStrategy(config)
        self.activation_detector = HandActivationStrategy(config)
        self.head_detector = HeadOrientationStrategy(config)

        self.calibration_frame_count = 0

    def detect_gestures(self, landmarks: Optional[dict]) -> List[GestureResult]:
        """
        Detect gestures from hand landmarks.

        Args:
            landmarks: Hand landmarks dictionary or None

        Returns:
            List of detected gestures with confidence scores
        """
        if not landmarks:
            return []

        try:
            # Convert landmarks format if needed
            processed_landmarks = self._process_landmarks(landmarks)

            # Collect all gesture results
            all_gestures = []

            # Run each detection strategy
            fist_gestures = self.fist_detector.detect(
                processed_landmarks, self.calibration_data)
            all_gestures.extend(fist_gestures)

            all_gestures.extend(self.position_detector.detect(
                processed_landmarks, self.calibration_data))
            all_gestures.extend(self.activation_detector.detect(
                processed_landmarks, self.calibration_data))

            # Head gesture detection (if head landmarks present)
            # If you want to support separate head landmarks, pass them as a separate argument
            head_gestures = self.head_detector.detect(
                processed_landmarks, self.calibration_data)
            all_gestures.extend(head_gestures)

            # Filter by confidence threshold
            filtered_gestures = [
                gesture for gesture in all_gestures
                if gesture.confidence >= self.config.gestures.min_detection_confidence
            ]
            return filtered_gestures

        except Exception as e:
            raise Exception(f"Gesture detection failed: {e}")

    def _process_landmarks(self, landmarks: dict) -> Dict[str, Tuple[float, float, float]]:
        """Process landmarks into expected format with quantization."""
        # Handle different landmark formats
        if isinstance(landmarks, dict):
            # Apply quantization to reduce jittering using shared utility
            position_step = self.debug_config.quantization.position_step
            return quantize_landmarks(landmarks, position_step)
        else:
            # Convert other formats as needed
            return landmarks

    def calibrate(self, landmarks: dict) -> bool:
        """
        Calibrate the recognizer with initial hand position.

        Args:
            landmarks: Initial hand landmarks for calibration

        Returns:
            True if calibration successful
        """
        try:
            processed_landmarks = self._process_landmarks(landmarks)
            
            if "WRIST" not in processed_landmarks:
                return False

            # Store reference position
            wrist = processed_landmarks["WRIST"]
            self.calibration_data.reference_position = (
                wrist[0], wrist[1], wrist[2])

            # Store reference orientation data
            if ("INDEX_FINGER_MCP" in processed_landmarks and
                    "PINKY_MCP" in processed_landmarks):

                index_mcp = processed_landmarks["INDEX_FINGER_MCP"]
                pinky_mcp = processed_landmarks["PINKY_MCP"]

                # Calculate side vector for roll detection
                side_vector = (
                    index_mcp[0] - pinky_mcp[0],
                    index_mcp[1] - pinky_mcp[1],
                    index_mcp[2] - pinky_mcp[2]
                )

                self.calibration_data.reference_orientation = {
                    'side_vector': side_vector
                }

            # Mark as calibrated
            self.calibration_data.is_calibrated = True
            self.calibration_data.calibration_timestamp = time.time()
            return True

        except Exception as e:
            return False

    def is_calibrated(self) -> bool:
        """Check if recognizer is calibrated."""
        return self.calibration_data.is_calibrated

    def reset_calibration(self) -> None:
        """Reset calibration data."""
        self.calibration_data = CalibrationData()
        self.calibration_frame_count = 0

    def get_calibration_data(self) -> CalibrationData:
        """Get current calibration data."""
        return self.calibration_data
