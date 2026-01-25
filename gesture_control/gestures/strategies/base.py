from typing import Dict, Tuple, List
from ...core.config import ApplicationConfig
from ...core.types import CalibrationData, GestureResult


class GestureDetectionStrategy:
    """Base class for gesture detection strategies."""
    
    def __init__(self, config: ApplicationConfig):
        self.config = config
    
    def detect(self, landmarks: Dict[str, Tuple[float, float, float]], 
              calibration: CalibrationData) -> List[GestureResult]:
        """Detect gestures from landmarks."""
        raise NotImplementedError
