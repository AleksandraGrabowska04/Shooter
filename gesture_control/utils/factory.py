"""
Component factory for creating system components.
"""

import logging

from ..core.interfaces import (
    IComponentFactory, IHandTracker, IGestureRecognizer, 
    IGameController, IVisualizationRenderer, ILogger
)
from ..core.config import ApplicationConfig


class DefaultLogger(ILogger):
    """Default logger implementation using Python logging"""
    
    def __init__(self, name: str, config: ApplicationConfig):
        self._logger = logging.getLogger(name)
        self._config = config
        
        # Configure logger
        level = getattr(logging, config.logging.level.upper())
        self._logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(config.logging.log_format)
        
        # Add console handler
        if not self._logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)
            
            # Add file handler if enabled
            if config.logging.enable_file_logging:
                file_handler = logging.FileHandler(config.logging.log_file_path)
                file_handler.setFormatter(formatter)
                self._logger.addHandler(file_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, **kwargs)


class DefaultComponentFactory(IComponentFactory):
    """Default factory for creating system components"""
    
    def __init__(self, config: ApplicationConfig):
        self._config = config
        self._logger = self.create_logger("ComponentFactory")
    
    def create_hand_tracker(self) -> IHandTracker:
        """Create hand tracker instance"""
        from ..vision.mediapipe_tracker import MediaPipeHandTracker
        return MediaPipeHandTracker(self._config)
    
    def create_gesture_recognizer(self) -> IGestureRecognizer:
        """Create gesture recognizer instance"""
        from ..gestures.recognizer import GestureRecognizer
        return GestureRecognizer(self._config)
    
    def create_game_controller(self) -> IGameController:
        """Create game controller instance"""
        from ..gestures.game_controller import GameController
        return GameController(self._config, self.create_logger("GameController"))
    
    def create_visualization_renderer(self) -> IVisualizationRenderer:
        """Create visualization renderer instance"""
        from ..ui.opencv_renderer import OpenCVRenderer
        return OpenCVRenderer(self._config)
    
    def create_logger(self, name: str) -> ILogger:
        """Create logger instance"""
        return DefaultLogger(name, self._config)