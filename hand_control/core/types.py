"""
Core data types and enums for the hand control system.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class Vector2D:
    """2D vector for movement and displacement."""
    x: float = 0.0
    y: float = 0.0
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple format."""
        return (self.x, self.y)
    
    @classmethod
    def from_tuple(cls, data: Tuple[float, float]) -> 'Vector2D':
        """Create from tuple."""
        return cls(data[0], data[1])


@dataclass
class MovementVector:
    """Vector-based movement data."""
    displacement: Vector2D
    velocity: Optional[Vector2D] = None
    
    @property
    def magnitude(self) -> float:
        """Get displacement magnitude."""
        return (self.displacement.x**2 + self.displacement.y**2)**0.5
    
    def in_deadzone(self, deadzone_threshold: float = 0.1) -> bool:
        """Check if movement is within deadzone."""
        return self.magnitude < deadzone_threshold
    
    def is_significant(self, min_threshold: float = 0.05) -> bool:
        """Check if movement is significant enough to process."""
        return self.magnitude >= min_threshold


@dataclass
class RotationVector:
    """Head rotation data with strength values."""
    tilt: float = 0.0    # -1.0 to 1.0 (left to right)
    turn: float = 0.0    # -1.0 to 1.0 (left to right)  
    nod: float = 0.0     # -1.0 to 1.0 (down to up)
    
    @property
    def magnitude(self) -> float:
        """Get overall rotation magnitude."""
        return (self.tilt**2 + self.turn**2 + self.nod**2)**0.5


class HandState(Enum):
    """Hand detection states"""
    NONE = "none"
    OPEN = "open"
    FIST = "fist"


class GestureType(Enum):
    """Types of gestures supported by the system"""
    HAND_STATE = auto()
    POSITION_VECTOR = auto()
    ACTIVATION = auto()
    HEAD_TILT = auto()
    HEAD_TURN = auto()
    HEAD_NOD = auto()
    HEAD_ORIENTATION = auto()


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

    # NEW: Vector-based movement data
    movement_vector: Optional[MovementVector] = None
    rotation_vector: Optional[RotationVector] = None

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
class FrameAnalysis:
    """Analysis output for a processed camera frame."""
    camera_frame: CameraFrame
    gesture_results: List[GestureResult]
    control_state: Optional[ControlState] = None
    debug_info: Optional[Dict[str, Any]] = None


@dataclass
class CalibrationData:
    """Hand and head calibration data"""
    is_calibrated: bool = False
    reference_position: Optional[Tuple[float, float, float]] = None
    reference_orientation: Optional[Dict[str, Any]] = None
    calibration_timestamp: Optional[float] = None
    head_pitch_neutral: Optional[float] = None
