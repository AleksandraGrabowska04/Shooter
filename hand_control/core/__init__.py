"""
Core package for hand control system.
"""

from .config import ApplicationConfig, DEFAULT_CONFIG, load_config
from .types import (
    HandState, GestureType, PositionGesture, OrientationGesture, 
    MotionGesture, ControlState, GestureResult, CameraFrame, CalibrationData
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
    'load_config',
    
    # Types
    'HandState',
    'GestureType',
    'PositionGesture',
    'OrientationGesture',
    'MotionGesture', 
    'ControlState',
    'GestureResult',
    'CameraFrame',
    'CalibrationData',
    
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