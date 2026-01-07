"""
Configuration for gesture detection strategies.
"""

from dataclasses import dataclass, field
from typing import Optional
from ...constants import POSITION_STEP, FIST_THRESHOLD


@dataclass
class PositionStrategyConfig:
    """Configuration for position detection strategy."""
    # Quantization settings
    position_step: float = POSITION_STEP  # Pixels for position quantization
    
    # Distance limits
    max_distance_from_calibration: float = 100.0  # Maximum allowed distance from calibration point (pixels)
    
    # Confidence calculation multipliers  
    center_confidence_multiplier: float = 0.3  # Reduces confidence when in deadzone
    edge_confidence_base: float = 0.5  # Base confidence for edge positions
    edge_confidence_multiplier: float = 2.0  # Multiplier for edge distance calculation


@dataclass
class OrientationStrategyConfig:
    """Configuration for orientation detection strategy."""
    # Quantization settings
    angle_step: float = 0.05  # Radians for angle quantization
    
    # Detection thresholds
    roll_threshold: float = 0.5  # Threshold for roll detection
    
    # Thumb detection parameters  
    thumb_fold_multiplier: float = 0.7   # Multiplier for thumb fold detection
    thumb_extend_multiplier: float = 1.2  # Multiplier for thumb extension detection
    fist_multiplier: float = 0.95  # Multiplier for fist detection


@dataclass
class ShootStrategyConfig:
    """Configuration for shoot detection strategy."""
    # Timing settings
    min_fist_duration: float = 0.25  # Minimum fist duration in seconds
    shoot_display_duration: float = 0.5  # How long to display shoot in seconds
    sequence_timeout: float = 1.0  # Timeout for shoot sequences
    
    # Confidence thresholds
    min_confidence: float = 0.7  # Minimum confidence for valid detection
    max_confidence: float = 1.0  # Maximum confidence cap


@dataclass
class MotionStrategyConfig:
    """Configuration for motion detection strategy."""
    # Detection thresholds
    motion_threshold: float = 0.5  # Threshold for motion detection
    static_threshold: float = 1.0  # Threshold for static state


@dataclass
class HeadOrientationStrategyConfig:
    """Configuration for head orientation detection."""
    tilt_threshold_deg: float = 7.0        # Minimum roll angle (degrees)
    turn_threshold_ratio: float = 0.12     # Nose offset relative to face width
    nod_threshold_ratio: float = 0.10      # Pitch ratio relative to face width
    turn_gain: float = 1.6                 # Boost yaw to reduce head turn range
    tilt_gain: float = 1.0                 # Optional tilt sensitivity scaling
    nod_gain: float = 1.0                  # Optional nod sensitivity scaling


@dataclass
class FistStrategyConfig:
    """Configuration for fist detection strategy."""
    # Detection settings
    min_confidence: float = 0.5  # Minimum confidence for fist detection
    bent_threshold: float = 0.25  # Threshold for bent finger ratio
    
    # Finger bend multipliers
    main_finger_multiplier: float = 1.0  # Multiplier for main finger bend detection
    thumb_bend_multiplier: float = 0.90  # Multiplier for thumb bend detection
    
    # Confidence calculation
    bent_confidence_boost: float = 0.3  # Added confidence for bent fingers
    open_confidence_boost: float = 0.25  # Added confidence for open hand
    neutral_confidence: float = 0.3  # Default confidence for neutral state


@dataclass
class StrategiesConfig:
    """Master configuration for all gesture detection strategies."""
    position: PositionStrategyConfig = field(default_factory=PositionStrategyConfig)
    orientation: OrientationStrategyConfig = field(default_factory=OrientationStrategyConfig)
    shoot: ShootStrategyConfig = field(default_factory=ShootStrategyConfig)
    motion: MotionStrategyConfig = field(default_factory=MotionStrategyConfig)
    head: HeadOrientationStrategyConfig = field(default_factory=HeadOrientationStrategyConfig)
    fist: FistStrategyConfig = field(default_factory=FistStrategyConfig)
