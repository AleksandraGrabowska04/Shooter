"""
Core package for hand control system.
"""

from .config.application_config import ApplicationConfig
from .config import DEFAULT_CONFIG
from .types import (
    HandState,
    GestureType,
    PositionGesture,
    ControlState,
    GestureResult,
    CameraFrame,
    CalibrationData,
    FrameAnalysis
)
from .interfaces import (
    IHandTracker, IGestureRecognizer, IGameController,
    IVisualizationRenderer, ILogger, IComponentFactory
)
from .system import HandControlSystem, create_hand_control_system
__all__ = [
    # Configuration
    'ApplicationConfig',
    'DEFAULT_CONFIG',

    # Types
    'HandState',
    'GestureType',
    'PositionGesture',
    'GestureResult',
    'CameraFrame',
    'CalibrationData',
    'FrameAnalysis',

    # Interfaces
    'IHandTracker',
    'IGestureRecognizer',
    'IGameController',
    'IVisualizationRenderer',
    'ILogger',
    'IComponentFactory',

    # System
    'HandControlSystem',
    'create_hand_control_system'
]
