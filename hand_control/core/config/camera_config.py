"""
Camera configuration settings.
"""

from dataclasses import dataclass
from ...constants import (
    DEFAULT_CAMERA_WIDTH,
    DEFAULT_CAMERA_HEIGHT,
    DEFAULT_FPS,
    DEFAULT_CAMERA_INDEX
)


@dataclass
class CameraConfig:
    """Camera configuration settings"""
    width: int = DEFAULT_CAMERA_WIDTH
    height: int = DEFAULT_CAMERA_HEIGHT
    fps: int = DEFAULT_FPS
    camera_index: int = DEFAULT_CAMERA_INDEX
    flip_horizontal: bool = True
    
    def __post_init__(self):
        """Validate camera configuration after initialization."""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Camera dimensions must be positive")
        if self.fps <= 0:
            raise ValueError("FPS must be positive")
        if self.camera_index < 0:
            raise ValueError("Camera index must be non-negative")