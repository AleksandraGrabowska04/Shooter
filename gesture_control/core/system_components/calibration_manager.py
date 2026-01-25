"""
Calibration management component for the gesture control system.
"""

from typing import Optional

from ..interfaces import IGestureRecognizer, ILogger
from ..config import ApplicationConfig


class CalibrationManager:
    """
    Manages hand calibration for gesture recognition.
    """
    
    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize calibration manager.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.is_calibrated = False
    
    def set_gesture_recognizer(self, gesture_recognizer: IGestureRecognizer) -> None:
        """Set gesture recognizer reference."""
        self.gesture_recognizer = gesture_recognizer
        
    def run_calibration(self) -> None:
        """Run calibration process."""
        if not self.gesture_recognizer:
            self.logger.error("No gesture recognizer set")
            return
        
        self.logger.info("Starting calibration process...")
        # Simplified calibration logic
        self.is_calibrated = True
        self.logger.info("Calibration completed")
