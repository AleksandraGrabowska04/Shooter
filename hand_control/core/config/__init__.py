"""
Configuration system components for hand control application.
"""

from .camera_config import CameraConfig
from .gesture_config import GestureConfig
from .ui_config import UIConfig
from .logging_config import LoggingConfig
from .performance_config import PerformanceConfig
from .strategies_config import StrategiesConfig
from .ui_rendering_config import UIRenderingConfig
from .performance_tuning_config import PerformanceTuningConfig
from .debug_config import DebugConfig
from .application_config import ApplicationConfig
from .config_loader import ConfigLoader, load_config
from .config_validator import ConfigValidator

# Default configuration instance
DEFAULT_CONFIG = ApplicationConfig()

__all__ = [
    'CameraConfig',
    'GestureConfig', 
    'UIConfig',
    'LoggingConfig',
    'PerformanceConfig',
    'StrategiesConfig',
    'UIRenderingConfig',
    'PerformanceTuningConfig',
    'DebugConfig',
    'ApplicationConfig',
    'ConfigLoader',
    'ConfigValidator',
    'load_config',
    'DEFAULT_CONFIG'
]