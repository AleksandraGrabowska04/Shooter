"""
Simplified application configuration with embedded UI and logging settings.
"""

from dataclasses import dataclass, field
from typing import List, Tuple
from ...constants import (
    COLOR_GREEN, COLOR_RED, COLOR_WHITE, COLOR_CYAN,
    FONT_SCALE, TEXT_THICKNESS, LINE_SPACING
)

from .camera_config import CameraConfig
from .gesture_config import GestureConfig
from .performance_config import PerformanceConfig
from .strategies_config import StrategiesConfig
from .debug_config import DebugConfig
from .performance_tuning_config import PerformanceTuningConfig


@dataclass 
class UISettings:
    """UI configuration embedded in ApplicationConfig"""
    # Display settings
    show_landmarks: bool = True
    show_debug_info: bool = False
    
    # Colors (BGR format for OpenCV) - using constants
    landmark_color: Tuple[int, int, int] = COLOR_GREEN
    connection_color: Tuple[int, int, int] = COLOR_RED
    text_color: Tuple[int, int, int] = COLOR_WHITE
    debug_color: Tuple[int, int, int] = COLOR_CYAN
    
    # Text settings - using constants
    font_scale: float = FONT_SCALE
    text_thickness: int = TEXT_THICKNESS
    line_spacing: int = LINE_SPACING
    
    # Window settings
    window_name: str = "Gesture Control"
    window_resizable: bool = True


@dataclass 
class LoggingSettings:
    """Logging configuration embedded in ApplicationConfig"""
    level: str = "INFO"
    enable_file_logging: bool = False
    log_file_path: str = "gesture_control.log"
    enable_performance_logging: bool = False
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class ApplicationConfig:
    """Unified application configuration with embedded UI and logging settings"""
    # Core configurations
    camera: CameraConfig = field(default_factory=CameraConfig)
    gestures: GestureConfig = field(default_factory=GestureConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    strategies: StrategiesConfig = field(default_factory=StrategiesConfig)
    debug: DebugConfig = field(default_factory=DebugConfig)
    performance_tuning: PerformanceTuningConfig = field(default_factory=PerformanceTuningConfig)
    
    # Embedded configurations (simplified)
    ui: UISettings = field(default_factory=UISettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    
    # Application settings
    enable_debug_mode: bool = False
    auto_calibrate: bool = True
    require_calibration: bool = True
    exit_key: int = 27  # ESC key
    
    def validate(self) -> List[str]:
        """
        Validate all configuration settings.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate camera config
        try:
            self.camera.__post_init__()
        except ValueError as e:
            errors.append(f"Camera config: {e}")
        
        # Validate gestures config
        try:
            self.gestures.__post_init__()
        except ValueError as e:
            errors.append(f"Gesture config: {e}")
        
        # Validate performance config
        try:
            self.performance.__post_init__()
        except ValueError as e:
            errors.append(f"Performance config: {e}")
        
        # Validate UI settings
        if self.ui.font_scale <= 0:
            errors.append("UI: Font scale must be positive")
        if self.ui.text_thickness <= 0:
            errors.append("UI: Text thickness must be positive")
        if self.ui.line_spacing <= 0:
            errors.append("UI: Line spacing must be positive")
        
        # Validate colors are within RGB range
        for color_name, color in [
            ('landmark_color', self.ui.landmark_color),
            ('connection_color', self.ui.connection_color),
            ('text_color', self.ui.text_color),
            ('debug_color', self.ui.debug_color)
        ]:
            if not all(0 <= c <= 255 for c in color):
                errors.append(f"UI: {color_name} values must be between 0 and 255")
        
        # Validate logging settings
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.logging.level.upper() not in valid_levels:
            errors.append(f"Logging: Level must be one of {valid_levels}")
        
        if self.logging.enable_file_logging and not self.logging.log_file_path:
            errors.append("Logging: File path must be specified when file logging is enabled")
        
        # Validate application settings
        if self.exit_key < 0 or self.exit_key > 255:
            errors.append("Exit key code must be between 0 and 255")
        
        return errors
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary for serialization."""
        return {
            'application': {
                'enable_debug_mode': self.enable_debug_mode,
                'auto_calibrate': self.auto_calibrate,
                'require_calibration': self.require_calibration,
                'exit_key': self.exit_key
            },
            'camera': {
                'width': self.camera.width,
                'height': self.camera.height,
                'fps': self.camera.fps,
                'camera_index': self.camera.camera_index,
                'flip_horizontal': self.camera.flip_horizontal,
            },
            'gestures': {
                'fist_finger_threshold': self.gestures.fist_finger_threshold,
                'fist_confidence_threshold': self.gestures.fist_confidence_threshold,
                'position_smoothing_factor': self.gestures.position_smoothing_factor,
                'position_threshold': self.gestures.position_threshold,
                'motion_threshold': self.gestures.motion_threshold,
                'motion_history_size': self.gestures.motion_history_size,
                'motion_smoothing': self.gestures.motion_smoothing,
                'orientation_threshold': self.gestures.orientation_threshold,
                'calibration_frames': self.gestures.calibration_frames,
                'min_detection_confidence': self.gestures.min_detection_confidence,
                'min_tracking_confidence': self.gestures.min_tracking_confidence,
            },
            'ui': {
                'show_landmarks': self.ui.show_landmarks,
                'show_debug_info': self.ui.show_debug_info,
                'landmark_color': self.ui.landmark_color,
                'connection_color': self.ui.connection_color,
                'text_color': self.ui.text_color,
                'debug_color': self.ui.debug_color,
                'font_scale': self.ui.font_scale,
                'text_thickness': self.ui.text_thickness,
                'line_spacing': self.ui.line_spacing,
                'window_name': self.ui.window_name,
                'window_resizable': self.ui.window_resizable,
            },
            'logging': {
                'level': self.logging.level,
                'enable_file_logging': self.logging.enable_file_logging,
                'log_file_path': self.logging.log_file_path,
                'enable_performance_logging': self.logging.enable_performance_logging,
                'log_format': self.logging.log_format,
            },
            'performance': {
                'enable_metrics': self.performance.enable_metrics,
                'fps_averaging_window': self.performance.fps_averaging_window,
                'gesture_timing_enabled': self.performance.gesture_timing_enabled,
                'memory_monitoring': self.performance.memory_monitoring,
            }
        }
