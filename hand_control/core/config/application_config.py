"""
Main application configuration class.
"""

from dataclasses import dataclass, field
from typing import List

from .camera_config import CameraConfig
from .gesture_config import GestureConfig
from .ui_config import UIConfig
from .logging_config import LoggingConfig
from .performance_config import PerformanceConfig


@dataclass
class ApplicationConfig:
    """Main application configuration"""
    camera: CameraConfig = field(default_factory=CameraConfig)
    gestures: GestureConfig = field(default_factory=GestureConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
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
        
        try:
            # Validate each config component by calling their __post_init__ methods
            self.camera.__post_init__()
        except ValueError as e:
            errors.append(f"Camera config: {e}")
        
        try:
            self.gestures.__post_init__()
        except ValueError as e:
            errors.append(f"Gesture config: {e}")
        
        try:
            self.ui.__post_init__()
        except ValueError as e:
            errors.append(f"UI config: {e}")
        
        try:
            self.logging.__post_init__()
        except ValueError as e:
            errors.append(f"Logging config: {e}")
        
        try:
            self.performance.__post_init__()
        except ValueError as e:
            errors.append(f"Performance config: {e}")
        
        return errors
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary format.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'camera': {
                'width': self.camera.width,
                'height': self.camera.height,
                'fps': self.camera.fps,
                'camera_index': self.camera.camera_index,
                'flip_horizontal': self.camera.flip_horizontal
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
                'min_tracking_confidence': self.gestures.min_tracking_confidence
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
                'window_resizable': self.ui.window_resizable
            },
            'logging': {
                'level': self.logging.level,
                'enable_file_logging': self.logging.enable_file_logging,
                'log_file_path': self.logging.log_file_path,
                'enable_performance_logging': self.logging.enable_performance_logging,
                'log_format': self.logging.log_format
            },
            'performance': {
                'enable_metrics': self.performance.enable_metrics,
                'fps_averaging_window': self.performance.fps_averaging_window,
                'gesture_timing_enabled': self.performance.gesture_timing_enabled,
                'memory_monitoring': self.performance.memory_monitoring
            },
            'application': {
                'enable_debug_mode': self.enable_debug_mode,
                'auto_calibrate': self.auto_calibrate,
                'exit_key': self.exit_key
            }
        }