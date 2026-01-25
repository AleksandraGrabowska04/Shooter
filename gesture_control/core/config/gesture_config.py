"""
Gesture recognition configuration settings.
"""

from dataclasses import dataclass
from ...constants import (
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    FIST_THRESHOLD
)


@dataclass
class GestureConfig:
    """Gesture recognition configuration"""
    # Fist detection
    fist_finger_threshold: float = 0.15
    fist_confidence_threshold: float = FIST_THRESHOLD
    
    # Position detection  
    position_smoothing_factor: float = 0.3
    position_threshold: float = 0.08
    
    # Motion detection
    motion_threshold: float = 0.02
    motion_history_size: int = 5
    motion_smoothing: float = 0.4
    
    # Orientation detection
    orientation_threshold: float = 15.0  # degrees
    
    # General
    calibration_frames: int = 5
    min_detection_confidence: float = MIN_DETECTION_CONFIDENCE
    min_tracking_confidence: float = MIN_TRACKING_CONFIDENCE
    
    def __post_init__(self):
        """Validate gesture configuration after initialization."""
        if not (0.0 <= self.fist_confidence_threshold <= 1.0):
            raise ValueError("Confidence thresholds must be between 0 and 1")
        if self.calibration_frames <= 0:
            raise ValueError("Calibration frames must be positive")
        if not (0.0 <= self.min_detection_confidence <= 1.0):
            raise ValueError("Detection confidence must be between 0 and 1")
        if not (0.0 <= self.min_tracking_confidence <= 1.0):
            raise ValueError("Tracking confidence must be between 0 and 1")
        if self.motion_history_size <= 0:
            raise ValueError("Motion history size must be positive")
        if self.orientation_threshold <= 0:
            raise ValueError("Orientation threshold must be positive")
