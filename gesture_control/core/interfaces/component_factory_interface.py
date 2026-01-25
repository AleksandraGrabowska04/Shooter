"""
Component factory interface definition.
"""

from abc import ABC, abstractmethod

from .hand_tracker_interface import IHandTracker
from .gesture_recognizer_interface import IGestureRecognizer
from .game_controller_interface import IGameController
from .visualization_renderer_interface import IVisualizationRenderer
from .logger_interface import ILogger


class IComponentFactory(ABC):
    """Factory interface for creating system components"""
    
    @abstractmethod
    def create_hand_tracker(self) -> IHandTracker:
        """
        Create hand tracker instance.
        
        Returns:
            Hand tracker implementation
        """
        pass
    
    @abstractmethod
    def create_gesture_recognizer(self) -> IGestureRecognizer:
        """
        Create gesture recognizer instance.
        
        Returns:
            Gesture recognizer implementation
        """
        pass
    
    @abstractmethod
    def create_game_controller(self) -> IGameController:
        """
        Create game controller instance.
        
        Returns:
            Game controller implementation
        """
        pass
    
    @abstractmethod
    def create_visualization_renderer(self) -> IVisualizationRenderer:
        """
        Create visualization renderer instance.
        
        Returns:
            Visualization renderer implementation
        """
        pass
    
    @abstractmethod
    def create_logger(self, name: str) -> ILogger:
        """
        Create logger instance.
        
        Args:
            name: Logger name/identifier
            
        Returns:
            Logger implementation
        """
        pass