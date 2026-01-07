"""
System management components for the hand control system.

This package contains modular components that manage different aspects of the system lifecycle.
"""

from .frame_processor import FrameProcessor
from .gesture_pipeline import GesturePipeline
from .calibration_manager import CalibrationManager
from .system_initializer import SystemInitializer
from .lifecycle_manager import LifecycleManager
from .hand_control_system import HandControlSystem

__all__ = [
    'FrameProcessor',
    'GesturePipeline',
    'CalibrationManager', 
    'SystemInitializer',
    'LifecycleManager',
    'HandControlSystem'
]
