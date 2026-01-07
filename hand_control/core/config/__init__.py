"""
Configuration system components for hand control application.
"""

from .camera_config import CameraConfig
from .gesture_config import GestureConfig
from .performance_config import PerformanceConfig
from .strategies_config import StrategiesConfig
from .performance_tuning_config import PerformanceTuningConfig
from .debug_config import DebugConfig
from .application_config import ApplicationConfig

# Default configuration instance
DEFAULT_CONFIG = ApplicationConfig()

__all__ = [
    'CameraConfig',
    'GestureConfig', 
    'PerformanceConfig',
    'StrategiesConfig',
    'PerformanceTuningConfig',
    'DebugConfig',
    'ApplicationConfig',
    'DEFAULT_CONFIG'
]