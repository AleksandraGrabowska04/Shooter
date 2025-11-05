"""
Gesture detection strategies package.

This module contains separate strategy implementations for different types of gesture detection:
- Base strategy interface
- Fist detection strategy
- Shoot detection strategy  
- Position detection strategy
- Orientation detection strategy
- Motion detection strategy
"""

from .base import GestureDetectionStrategy
from .fist import FistDetectionStrategy
from .shoot import ShootDetectionStrategy
from .position import PositionDetectionStrategy
from .orientation import OrientationDetectionStrategy
from .motion import MotionDetectionStrategy

__all__ = [
    'GestureDetectionStrategy',
    'FistDetectionStrategy', 
    'ShootDetectionStrategy',
    'PositionDetectionStrategy',
    'OrientationDetectionStrategy',
    'MotionDetectionStrategy'
]