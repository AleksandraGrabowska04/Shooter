"""
Lifecycle management component for the hand control system.
"""

import time
import cv2
from typing import Dict, Any, Optional

from ..interfaces import IHandTracker, ILogger
from ..config import ApplicationConfig


class LifecycleManager:
    """
    Manages the lifecycle of the hand control system including startup, shutdown, and status tracking.
    """
    
    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize lifecycle manager.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # System state
        self.is_running = False
        self.is_initialized = False
        self.start_time: Optional[float] = None
        
        # Components (will be set externally)
        self.hand_tracker: Optional[IHandTracker] = None
    
    def start_system(self) -> None:
        """Start the system lifecycle."""
        if not self.is_initialized:
            raise Exception("System not initialized. Call set_initialized() first.")
        
        self.logger.info("Starting hand control system...")
        self.is_running = True
        self.start_time = time.time()
    
    def stop_system(self) -> None:
        """Stop the system and cleanup resources."""
        if self.is_running:
            self.logger.info("Stopping hand control system...")
            self.is_running = False
            
            # Cleanup components
            if self.is_initialized and self.hand_tracker:
                self.hand_tracker.release()
            
            cv2.destroyAllWindows()
            
            # Session completed
            if self.start_time:
                session_duration = time.time() - self.start_time
                self.logger.info(f"Session completed after {session_duration:.1f}s")
    
    def set_initialized(self, initialized: bool = True) -> None:
        """Set system initialization status."""
        self.is_initialized = initialized
    
    def set_hand_tracker(self, hand_tracker: IHandTracker) -> None:
        """Set hand tracker for cleanup purposes."""
        self.hand_tracker = hand_tracker
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status information.
        
        Returns:
            Dictionary with system status information
        """
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'start_time': self.start_time,
            'uptime': time.time() - self.start_time if self.start_time else None,
            'camera_available': (
                self.is_initialized and self.hand_tracker and 
                self.hand_tracker.is_available()
            )
        }
    
    def handle_interrupt(self) -> None:
        """Handle system interrupt (Ctrl+C)."""
        self.logger.info("System interrupted by user")
        self.stop_system()
    
    def handle_error(self, error: Exception, should_stop: bool = True) -> None:
        """
        Handle system error.
        
        Args:
            error: The exception that occurred
            should_stop: Whether to stop the system
        """
        self.logger.error(f"System error: {error}")
        if should_stop and not self.config.enable_debug_mode:
            self.stop_system()
    
    @property
    def should_continue_running(self) -> bool:
        """Check if system should continue running."""
        return self.is_running and self.is_initialized