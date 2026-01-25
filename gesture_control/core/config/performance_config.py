"""
Performance monitoring configuration settings.
"""

from dataclasses import dataclass
from ...constants import FPS_AVERAGING_WINDOW


@dataclass
class PerformanceConfig:
    """Performance monitoring configuration"""
    enable_metrics: bool = False
    fps_averaging_window: int = FPS_AVERAGING_WINDOW
    gesture_timing_enabled: bool = False
    memory_monitoring: bool = False
    
    def __post_init__(self):
        """Validate performance configuration after initialization."""
        if self.fps_averaging_window <= 0:
            raise ValueError("FPS averaging window must be positive")