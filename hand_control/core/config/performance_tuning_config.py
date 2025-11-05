"""
Configuration for performance tuning and timing parameters.
"""

from dataclasses import dataclass


@dataclass
class FrameProcessorConfig:
    """Configuration for frame processing timing."""
    # Shoot display timing
    shoot_display_timeout: float = 0.5  # Seconds to display shoot indication
    
    # Debug timing
    debug_display_timeout: float = 1.0  # Seconds to display debug info
    debug_frame_frequency: int = 30     # Process debug info every N frames


@dataclass
class ControlSmoothingConfig:
    """Configuration for control state smoothing."""
    # Gesture timing
    gesture_cooldown: float = 0.1  # Minimum time between gesture updates (seconds)
    
    # History settings
    history_size: int = 5  # Number of states to keep for smoothing


@dataclass
class CalibrationConfig:
    """Configuration for calibration timing."""
    # Calibration requirements
    required_frames: int = 30      # Frames needed for stable calibration
    stability_timeout: float = 3.0  # Seconds to wait for hand stability


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