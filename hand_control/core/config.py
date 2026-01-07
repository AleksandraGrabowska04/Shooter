"""
Configuration system for hand control application.

This module provides a modular configuration system with separate components
for different aspects of the application (camera, gestures, UI, etc.).
"""

# Convenience re-exports for configuration components
from .config import (
    CameraConfig,
    GestureConfig,
    PerformanceConfig,
    ApplicationConfig
)

# Default configuration instance
DEFAULT_CONFIG = ApplicationConfig()

__all__ = [
    'CameraConfig',
    'GestureConfig',
    'PerformanceConfig',
    'ApplicationConfig',
    'DEFAULT_CONFIG'
]
