"""
Core data types and enums for the hand control system.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any


class HandState(Enum):
    """Hand detection states"""
    NONE = "none"
    OPEN = "open"
    FIST = "fist"


class GestureType(Enum):
    """Types of gestures supported by the system"""
    HAND_STATE = auto()
    POSITION = auto()
    ACTIVATION = auto()
    HEAD_TILT = auto()
    HEAD_TURN = auto()
    HEAD_NOD = auto()


class PositionGesture(Enum):
    """Position-based gestures relative to calibrated center"""
    CENTER = "center"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class GestureResult:
    """Result of gesture detection"""
    gesture_type: GestureType
    confidence: float
    data: Optional[Dict[str, Any]] = None  # Additional gesture-specific data
    timestamp: Optional[float] = None

    @property
    def name(self) -> str:
        """Get gesture name for display"""
        return self.gesture_type.name

    def __post_init__(self):
        """Validate confidence range"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}")


@dataclass
class ControlState:
    """Complete control state information for game integration"""
    # Basic state
    is_active: bool
    is_calibrated: bool
    status_message: str

    # Detected gestures
    hand_state: HandState

    # Primary gesture (highest confidence)
    primary_gesture: Optional[GestureResult] = None

    # All detected gestures with confidence scores
    all_gestures: Optional[List[GestureResult]] = None

    # Debug information (optional)
    debug_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize default values"""
        if self.all_gestures is None:
            self.all_gestures = []

    def get_gesture_by_type(self, gesture_type: GestureType) -> Optional[GestureResult]:
        """Get the first gesture of specified type"""
        if self.all_gestures is None:
            return None
        for gesture in self.all_gestures:
            if gesture.gesture_type == gesture_type:
                return gesture
        return None

    def has_high_confidence_gesture(self, min_confidence: float = 0.8) -> bool:
        """Check if any gesture has high confidence"""
        if self.all_gestures is None:
            return False
        return any(g.confidence >= min_confidence for g in self.all_gestures)


@dataclass
class CameraFrame:
    """Camera frame with optional landmarks"""
    frame: Any  # OpenCV image array (renamed for consistency)
    landmarks: Optional[Dict[str, Tuple[float, float, float]]] = None
    timestamp: Optional[float] = None
    frame_id: Optional[int] = None
    face_landmarks: Optional[List[Tuple[float, float, float]]] = None


@dataclass
class CalibrationData:
    """Hand and head calibration data"""
    is_calibrated: bool = False
    reference_position: Optional[Tuple[float, float, float]] = None
    reference_orientation: Optional[Dict[str, Any]] = None
    calibration_timestamp: Optional[float] = None
    head_pitch_neutral: Optional[float] = None
