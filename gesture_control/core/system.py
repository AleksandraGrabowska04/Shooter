"""
Main system module for the gesture control system.
This module provides the main GestureControlSystem class for managing the entire application.
"""

from .interfaces import ILogger
from .config import ApplicationConfig
from .system_components import GestureControlSystem


def create_gesture_control_system(config: ApplicationConfig, logger: ILogger) -> GestureControlSystem:
    """
    Factory function to create and configure a gesture control system.
    
    Args:
        config: Application configuration
        logger: Logger instance
        
    Returns:
        Configured GestureControlSystem instance
    """
    return GestureControlSystem(config, logger)

