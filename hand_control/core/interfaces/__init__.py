"""
Core interfaces for the hand control system components.

This package contains all abstract interfaces that define the contracts
for different components of the hand control system.
"""

from .hand_tracker_interface import IHandTracker
from .gesture_recognizer_interface import IGestureRecognizer
from .game_controller_interface import IGameController
from .visualization_renderer_interface import IVisualizationRenderer
from .logger_interface import ILogger
from .component_factory_interface import IComponentFactory

__all__ = [
    'IHandTracker',
    'IGestureRecognizer',
    'IGameController',
    'IVisualizationRenderer',
    'ILogger',
    'IComponentFactory'
]