"""
System initialization component for the gesture control system.
"""

from typing import Optional

from ..interfaces import IComponentFactory, ILogger, IHandTracker, IGestureRecognizer, IGameController, IVisualizationRenderer
from ..config import ApplicationConfig


class SystemInitializer:
    """
    Handles initialization of all system components.
    """
    
    def __init__(self, factory: Optional[IComponentFactory], config: ApplicationConfig, logger: ILogger):
        """
        Initialize system initializer.
        
        Args:
            factory: Component factory for creating components
            config: Application configuration
            logger: Logger instance
        """
        self.factory = factory
        self.config = config
        self.logger = logger
        
        # Components (will be created during initialization)
        self.hand_tracker: Optional[IHandTracker] = None
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.game_controller: Optional[IGameController] = None
        self.visualization_renderer: Optional[IVisualizationRenderer] = None
    
    def initialize_components(self) -> tuple[bool, dict]:
        """
        Initialize all system components.
        
        Returns:
            Tuple of (success, components_dict)
            
        Raises:
            Exception: If initialization fails
        """
        try:
            self.logger.info("Initializing gesture control system components...")
            
            if not self.factory:
                self.logger.error("No factory provided for component initialization")
                return False, {}
            
            # Create components
            self.hand_tracker = self.factory.create_hand_tracker()
            self.gesture_recognizer = self.factory.create_gesture_recognizer()
            self.game_controller = self.factory.create_game_controller()
            self.visualization_renderer = self.factory.create_visualization_renderer()
            
            # Validate components
            if not self.hand_tracker.is_available():
                raise Exception("Camera is not available")
            
            # Configure components
            self.game_controller.set_debug_mode(self.config.enable_debug_mode)
            
            self.logger.info("All system components initialized successfully")
            
            components = {
                'hand_tracker': self.hand_tracker,
                'gesture_recognizer': self.gesture_recognizer,
                'game_controller': self.game_controller,
                'renderer': self.visualization_renderer
            }
            
            return True, components
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False, {}
    
    def setup_callbacks(self, recalibration_callback) -> None:
        """
        Set up callbacks between components.
        
        Args:
            recalibration_callback: Callback function for recalibration requests
        """
        if self.game_controller:
            self.game_controller.set_recalibration_callback(recalibration_callback)
            self.logger.info("Recalibration callback set up for automatic FIST transitions")
    
    def get_components(self) -> tuple:
        """
        Get all initialized components.
        
        Returns:
            Tuple of (hand_tracker, gesture_recognizer, game_controller, visualization_renderer)
        """
        return (
            self.hand_tracker,
            self.gesture_recognizer,
            self.game_controller,
            self.visualization_renderer
        )
