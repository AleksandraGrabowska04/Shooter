"""
Configuration for performance tuning and timing parameters.
"""

from dataclasses import dataclass
from ...constants import (
    GESTURE_COOLDOWN,
    HISTORY_SIZE,
    CALIBRATION_REQUIRED_FRAMES,
    CALIBRATION_STABILITY_TIMEOUT,
    SHOOT_DISPLAY_TIMEOUT,
    DEBUG_DISPLAY_TIMEOUT,
    DEBUG_FRAME_FREQUENCY
)


@dataclass
class FrameProcessorConfig:
    """Configuration for frame processing timing."""
    # Shoot display timing
    shoot_display_timeout: float = SHOOT_DISPLAY_TIMEOUT  
    
    # Debug timing
    debug_display_timeout: float = DEBUG_DISPLAY_TIMEOUT
    debug_frame_frequency: int = DEBUG_FRAME_FREQUENCY


@dataclass
class ControlSmoothingConfig:
    """Configuration for control state smoothing."""
    # Gesture timing
    gesture_cooldown: float = GESTURE_COOLDOWN
    
    # History settings
    history_size: int = HISTORY_SIZE


@dataclass
class CalibrationConfig:
    """Configuration for calibration timing."""
    # Calibration requirements
    required_frames: int = CALIBRATION_REQUIRED_FRAMES     
    stability_timeout: float = CALIBRATION_STABILITY_TIMEOUT


@dataclass
class PerformanceTuningConfig:
    """Master configuration for performance and timing parameters."""
    frame_processor: FrameProcessorConfig
    control_smoothing: ControlSmoothingConfig  
    calibration: CalibrationConfig
    
    def __init__(self):
        self.frame_processor = FrameProcessorConfig()
        self.control_smoothing = ControlSmoothingConfig()
        self.calibration = CalibrationConfig()