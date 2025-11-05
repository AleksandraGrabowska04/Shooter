"""
Configuration system for hand control application.

This module provides a modular configuration system with separate components
for different aspects of the application (camera, gestures, UI, etc.).
"""

# Import all configuration components for backward compatibility
from .config import (
    CameraConfig,
    GestureConfig,
    UIConfig,
    LoggingConfig,
    PerformanceConfig,
    ApplicationConfig,
    ConfigLoader,
    ConfigValidator,
    load_config
)

# Default configuration instance for backward compatibility
DEFAULT_CONFIG = ApplicationConfig()

__all__ = [
    'CameraConfig',
    'GestureConfig',
    'UIConfig',
    'LoggingConfig',
    'PerformanceConfig',
    'ApplicationConfig',
    'ConfigLoader',
    'ConfigValidator',
    'load_config',
    'DEFAULT_CONFIG'
]