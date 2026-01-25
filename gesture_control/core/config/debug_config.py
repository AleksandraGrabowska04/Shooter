"""
Configuration for debug and development settings.
"""

from dataclasses import dataclass
from ...constants import POSITION_STEP


@dataclass
class QuantizationDebugConfig:
    """Configuration for quantization debugging."""
    # Quantization settings for debug display
    position_step: float = POSITION_STEP  # Same as recognizer for consistency
    
    # Debug output control
    enable_landmark_quantization: bool = True
    enable_gesture_debug_info: bool = True
    

@dataclass
class VisualizationDebugConfig:
    """Configuration for debug visualization."""
    # Debug display toggles
    show_landmarks: bool = True
    show_connections: bool = True
    show_gesture_bars: bool = True
    show_debug_text: bool = True
    
    # Debug text formatting
    show_raw_values: bool = False      # Show unprocessed landmark values
    show_quantized_values: bool = True  # Show quantized landmark values
    show_confidence_scores: bool = True # Show gesture confidence scores


@dataclass
class LoggingDebugConfig:
    """Configuration for debug logging."""
    # Logging levels for different components
    log_gesture_detection: bool = False
    log_frame_processing: bool = False
    log_calibration_events: bool = True
    
    # Performance logging
    log_frame_rates: bool = False
    log_processing_times: bool = False


@dataclass
class DebugConfig:
    """Master configuration for debug and development settings."""
    quantization: QuantizationDebugConfig
    visualization: VisualizationDebugConfig
    logging: LoggingDebugConfig
    
    def __init__(self):
        self.quantization = QuantizationDebugConfig()
        self.visualization = VisualizationDebugConfig()
        self.logging = LoggingDebugConfig()