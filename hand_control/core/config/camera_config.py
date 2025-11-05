"""
Camera configuration settings.
"""

from dataclasses import dataclass


@dataclass
class CameraConfig:
    """Camera configuration settings"""
    width: int = 640
    height: int = 480
    fps: int = 30
    camera_index: int = 0
    flip_horizontal: bool = True
    
    def __post_init__(self):
        """Validate camera configuration after initialization."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Camera dimensions must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.camera_index < 0:
            raise ValueError("Camera index must be non-negative")