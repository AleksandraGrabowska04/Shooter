"""
Hand tracker interface definition.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..types import CameraFrame


class IHandTracker(ABC):
    """Interface for hand tracking components"""
    
    @abstractmethod
    def read_frame(self) -> Optional[CameraFrame]:
        """
        Read and process a frame from the camera.
        
        Returns:
            CameraFrame with image and landmarks, or None if failed
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if camera is available and working"""
        pass
    
    @abstractmethod
    def release(self) -> None:
        """Release camera resources"""
        pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()