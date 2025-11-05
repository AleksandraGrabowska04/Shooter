"""
Main system module for the hand control system.
This module provides the main HandControlSystem class for managing the entire application.
"""

from .interfaces import ILogger
from .config import ApplicationConfig
from .system_components import HandControlSystem


def create_hand_control_system(config: ApplicationConfig, logger: ILogger) -> HandControlSystem:
    """
    Factory function to create and configure a hand control system.
    
    Args:
        config: Application configuration
        logger: Logger instance
        
    Returns:
        Configured HandControlSystem instance
    """
    return HandControlSystem(config, logger)


