"""
Gesture recognizer interface definition.
"""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..types import GestureResult, CalibrationData


class IGestureRecognizer(ABC):
    """Interface for gesture recognition components"""
    
    @abstractmethod
    def detect_gestures(self, landmarks: Optional[dict]) -> List[GestureResult]:
        """
        Detect gestures from hand landmarks.
        
        Args:
            landmarks: Hand landmarks dictionary or None
            
        Returns:
            List of detected gestures with confidence scores
        """
        pass
    
    @abstractmethod
    def calibrate(self, landmarks: dict) -> bool:
        """
        Calibrate the recognizer with initial hand position.
        
        Args:
            landmarks: Initial hand landmarks for calibration
            
        Returns:
            True if calibration successful
        """
        pass
    
    @abstractmethod
    def is_calibrated(self) -> bool:
        """Check if recognizer is calibrated"""
        pass
    
    @abstractmethod
    def reset_calibration(self) -> None:
        """Reset calibration data"""
        pass
    
    @abstractmethod
    def get_calibration_data(self) -> CalibrationData:
        """Get current calibration data"""
        pass