"""
Visualization renderer interface definition.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any

from ..types import CalibrationData


class IVisualizationRenderer(ABC):
    """Interface for visualization and rendering"""
    
    @abstractmethod
    def render_status(self, frame: Any, status_message: str) -> None:
        """
        Render status message on frame.
        
        Args:
            frame: Frame to render on
            status_message: Status text to display
        """
        pass
    
    @abstractmethod
    def render_debug_info(self, frame: Any, debug_info: dict) -> None:
        """
        Render debug information on frame.
        
        Args:
            frame: Frame to render on
            debug_info: Debug information dictionary
        """
        pass
    
    @abstractmethod
    def render_gesture_visualization(self, frame: Any, landmarks: Optional[dict], 
                                   calibration: CalibrationData) -> None:
        """
        Render gesture-specific visualization.
        
        Args:
            frame: Frame to render on
            landmarks: Hand landmarks dictionary
            calibration: Calibration data for reference points
        """
        pass
    
    @abstractmethod
    def render_gesture_bars(self, frame: Any, gesture_data: dict) -> None:
        """
        Render gesture strength bars.
        
        Args:
            frame: Frame to render on
            gesture_data: Gesture data for bars
        """
        pass
    
    @abstractmethod
    def render_shoot_indication(self, frame: Any, is_shooting: bool) -> None:
        """
        Render shooting indication.
        
        Args:
            frame: Frame to render on
            is_shooting: Whether shooting is active
        """
        pass