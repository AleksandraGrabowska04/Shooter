"""
Main hand control system coordinator.
"""

import cv2
from typing import Optional, Dict, Any

from ..interfaces import IHandTracker, IGestureRecognizer, IVisualizationRenderer, ILogger
from ..config import ApplicationConfig
from .frame_processor import FrameProcessor
from .calibration_manager import CalibrationManager
from .system_initializer import SystemInitializer
from .lifecycle_manager import LifecycleManager


class HandControlSystem:
    """
    Main hand control system that coordinates all components.
    """
    
    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize the hand control system.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger
        
        # Create factory
        from ...utils.factory import DefaultComponentFactory
        factory = DefaultComponentFactory(config)
        
        # Initialize sub-managers
        self.initializer = SystemInitializer(factory, config, logger)
        self.frame_processor = FrameProcessor(config, logger)
        self.calibration_manager = CalibrationManager(config, logger)
        self.lifecycle_manager = LifecycleManager(config, logger)
        
        # Components (initialized by initializer)
        self.hand_tracker: Optional[IHandTracker] = None
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.renderer: Optional[IVisualizationRenderer] = None
    
    def initialize(self) -> bool:
        """
        Initialize the system components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize components
            success, components = self.initializer.initialize_components()
            if not success:
                return False
            
            # Extract components
            self.hand_tracker = components['hand_tracker']
            self.gesture_recognizer = components['gesture_recognizer']  
            self.renderer = components['renderer']
            self.game_controller = components.get('game_controller')
            
            # Setup component references with validation
            if self.hand_tracker and self.gesture_recognizer and self.renderer:
                self.frame_processor.set_components(
                    self.hand_tracker,
                    self.gesture_recognizer,
                    self.renderer,
                    self.game_controller
                )
            
            if self.gesture_recognizer:
                self.calibration_manager.set_gesture_recognizer(self.gesture_recognizer)
            if self.hand_tracker:
                self.lifecycle_manager.set_hand_tracker(self.hand_tracker)
            self.lifecycle_manager.set_initialized(True)
            
            # Setup simple reset calibration callback 
            if self.gesture_recognizer and self.game_controller:
                def reset_calibration_callback():
                    self.logger.info("🔄 Reset calibration - clearing current calibration state")
                    if self.gesture_recognizer and hasattr(self.gesture_recognizer, 'reset_calibration'):
                        self.gesture_recognizer.reset_calibration()
                        return True
                    return False
                        
                self.game_controller.set_reset_calibration_callback(reset_calibration_callback)
            
            self.logger.info("Hand control system initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            return False
    
    def run(self) -> None:
        """Run the main system loop."""
        if not self.lifecycle_manager.is_initialized:
            self.logger.error("System not initialized")
            return
        
        try:
            self.lifecycle_manager.start_system()
            
            # Check for calibration
            if self.config.require_calibration:
                self.calibration_manager.run_calibration()
            
            # Main processing loop
            while self.lifecycle_manager.should_continue_running:
                key = cv2.waitKey(1) & 0xFF
                
                # Handle exit
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                
                # Handle recalibration
                if key == ord('r'):
                    self.calibration_manager.run_calibration()
                    continue
                
                # Process frame
                should_continue = self.frame_processor.process_frame()
                if not should_continue:
                    break
            
            self.lifecycle_manager.stop_system()
            
        except KeyboardInterrupt:
            self.lifecycle_manager.handle_interrupt()
        except Exception as e:
            self.lifecycle_manager.handle_error(e)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.
        
        Returns:
            Dictionary with system status information
        """
        status = self.lifecycle_manager.get_system_status()
        
        # Add component status
        if self.lifecycle_manager.is_initialized:
            status.update({
                'calibration_completed': self.calibration_manager.is_calibrated,
                'frame_count': self.frame_processor.frame_count,
                'last_gesture': (
                    self.frame_processor.last_gesture if 
                    hasattr(self.frame_processor, 'last_gesture') else None
                )
            })
        
        return status
    
    def shutdown(self) -> None:
        """Shutdown the system and cleanup resources."""
        self.lifecycle_manager.stop_system()
        self.logger.info("System shutdown completed")
    
    @property
    def is_running(self) -> bool:
        """Check if system is currently running."""
        return self.lifecycle_manager.is_running
    
    @property
    def is_initialized(self) -> bool:
        """Check if system is initialized."""
        return self.lifecycle_manager.is_initialized