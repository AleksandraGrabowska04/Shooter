"""
Hand Control System

Architecture:
- core: Core interfaces, data types, and configuration
- vision: Camera handling and MediaPipe integration
- gestures: Gesture detection strategies and algorithms  
- ui: Visualization, overlays, and debug rendering
- utils: Logging, exceptions, and utility functions

Usage:
    from hand_control import HandControlSystem, ApplicationConfig
    from hand_control.constants import DEFAULT_CAMERA_WIDTH
    
    config = ApplicationConfig()
    system = HandControlSystem(config)
    
    with system:
        while True:
            control_state = system.update()
            if control_state.is_active:
                print(f"Gesture: {control_state.primary_gesture}")
"""

from .core.config import ApplicationConfig
from .core.types import ControlState, GestureResult
from .core.system import HandControlSystem
from .core.interfaces import IHandTracker, IGestureRecognizer, IGameController
from . import constants

# Main exports
__all__ = [
    # Main system
    'HandControlSystem',
    
    # Configuration
    'ApplicationConfig',
    
    # Core types
    'ControlState', 'GestureResult',
    
    # Interfaces  
    'IHandTracker', 'IGestureRecognizer', 'IGameController',
    
    # Constants
    'constants'
]