"""
Game controller interface definition.
"""

from abc import ABC, abstractmethod
from typing import List

from ..types import ControlState, GestureResult


class IGameController(ABC):
    """Interface for game control logic"""
    
    @abstractmethod
    def process_gestures(self, gesture_results: List[GestureResult]) -> ControlState:
        """
        Process gesture results and return control state.
        
        Args:
            gesture_results: List of detected gestures
            
        Returns:
            Control state with commands and status
        """
        pass
    
    @abstractmethod
    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode"""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Check if controller is currently active"""
        pass
    
    @abstractmethod
    def set_reset_calibration_callback(self, callback) -> None:
        """Set callback for resetting calibration"""
        pass