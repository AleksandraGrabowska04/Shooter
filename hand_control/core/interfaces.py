"""
Core interfaces for the hand control system components.

This module provides all abstract interfaces that define the contracts
for different components of the hand control system in a modular way.
"""

# Import all interfaces for backward compatibility
from .interfaces import (
    IHandTracker,
    IGestureRecognizer,
    IGameController,
    IVisualizationRenderer,
    ILogger,
    IComponentFactory
)

__all__ = [
    'IHandTracker',
    'IGestureRecognizer',
    'IGameController',
    'IVisualizationRenderer',
    'ILogger',
    'IComponentFactory'
]