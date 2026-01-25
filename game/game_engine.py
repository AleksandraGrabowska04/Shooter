"""
Game Engine - Orchestrates gesture control system and game integration.

This module provides the main game engine that coordinates between
the gesture control system and the game, managing the connector and
running the complete integrated experience.
"""

import time
import threading
from typing import Optional

from gesture_control.core import create_gesture_control_system, ApplicationConfig
from gesture_control.core.types import ControlState
from gesture_control.utils.factory import DefaultLogger
from .connector import ControlConnector
from .orb_collector import OrbCollectorGame

class GameEngine:
    """
    Main game engine that orchestrates gesture control system and game.
    
    This class manages the complete integration between gesture recognition
    and game logic, providing a unified experience.
    """
    
    def __init__(self, config: ApplicationConfig, game_mode: str = "collector"):
        """
        Initialize the game engine.
        
        Args:
            config: Application configuration
            game_mode: Type of game to run ("collector", etc.)
        """
        self.config = config
        self.game_mode = game_mode
        
        # Initialize logger
        self.logger = DefaultLogger("GameEngine", config)
        
        # Initialize gesture control system
        self.control_system = create_gesture_control_system(config, self.logger)
        
        # Initialize connector
        self.connector = ControlConnector(self.logger)
        
        # Initialize game
        self.game: Optional[OrbCollectorGame] = None
        
        # Threading for gesture control
        self.control_thread: Optional[threading.Thread] = None
        self.running = False
        
        self.logger.info(f"Game Engine initialized with mode: {game_mode}")
    
    def initialize(self) -> bool:
        """
        Initialize all components of the game engine.
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize gesture control system
            if not self.control_system.initialize():
                self.logger.error("Failed to initialize gesture control system")
                return False
            
            # Initialize game
            if self.game_mode == "collector":
                self.game = OrbCollectorGame()
            else:
                raise ValueError(f"Unknown game mode: {self.game_mode}")
            
            # Connect game to connector
            self.connector.set_game_callback(self.game.handle_game_command)
            
            # Start connector
            self.connector.start()
            
            self.logger.info("Game engine initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize game engine: {e}")
            return False
    
    def run(self) -> None:
        """
        Run the complete integrated experience.
        
        This starts both the gesture control system and the game,
        creating a seamless experience.
        """
        if not self.game:
            self.logger.error("Game not initialized")
            return
        
        try:
            self.running = True
            
            # Start gesture control system in separate thread
            self.control_thread = threading.Thread(
                target=self._run_control_system,
                daemon=True
            )
            self.control_thread.start()
            
            self.logger.info("🚀 Starting integrated game experience")
            
            # Run game in main thread
            self._run_game_with_updates()
            
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        except Exception as e:
            self.logger.error(f"Error during execution: {e}")
        finally:
            self.shutdown()
    
    def _run_control_system(self) -> None:
        """Run gesture control system in separate thread."""
        try:
            # Custom run loop that sends updates to connector
            if not self.control_system.lifecycle_manager.is_initialized:
                self.logger.error("Gesture control system not initialized")
                return
            
            self.control_system.lifecycle_manager.start_system()
            
            # Check for calibration
            if self.config.require_calibration:
                self.control_system.calibration_manager.run_calibration()
            
            # Main processing loop
            while (self.running and 
                   self.control_system.lifecycle_manager.should_continue_running):
                
                # Process frame and get control state from shared pipeline
                control_state = self._process_control_frame()
                
                # Send control state to connector
                if control_state:
                    self.connector.update_control_state(control_state)
                
                # Small sleep to prevent CPU overload
                time.sleep(0.01)
            
            self.control_system.lifecycle_manager.stop_system()
            
        except Exception as e:
            self.logger.error(f"Error in control thread: {e}")
            self.running = False
    
    def _process_control_frame(self) -> Optional[ControlState]:
        """
        Process a single control frame and return control state.
        
        Returns:
            ControlState object or None if processing failed
        """
        try:
            if not self.control_system.frame_processor:
                return None

            # Use the same gesture pipeline as debug mode for consistent data
            analysis = self.control_system.frame_processor.analyze_frame()
            if analysis:
                return analysis.control_state

            return None
            
        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return None
    
    def _run_game_with_updates(self) -> None:
        """Run game loop with periodic updates."""
        last_status_update = time.time()
        status_update_interval = 2.0  # seconds
        
        if not self.game:
            return
        
        try:
            while self.running and self.game.running:
                # Handle game events and updates
                import pygame
                
                dt = self.game.clock.tick(60) / 1000.0
                
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        break
                    self.game.handle_pygame_event(event)
                
                # Update and draw game
                self.game.update(dt)
                self.game.draw()
                
                # Periodic status updates
                current_time = time.time()
                if current_time - last_status_update >= status_update_interval:
                    self._log_status_update()
                    last_status_update = current_time
                
        except Exception as e:
            self.logger.error(f"Error in game loop: {e}")
            self.running = False
    
    def _log_status_update(self) -> None:
        """Log periodic status update."""
        try:
            if not self.game:
                return
            
            game_stats = self.game.get_game_stats()
            connector_status = self.connector.get_status()
            
            self.logger.info(f"📊 Status - Score: {game_stats['score']}, "
                           f"Lives: {game_stats['lives']}, "
                           f"Vector Control: {'ON' if game_stats['control_active'] else 'OFF'}, "
                           f"Queue: {connector_status['queue_size']}")
                           
        except Exception as e:
            self.logger.error(f"Error logging status: {e}")
    
    def shutdown(self) -> None:
        """Shutdown all components and cleanup resources."""
        try:
            self.logger.info("🛑 Shutting down game engine")
            
            self.running = False
            
            # Stop connector
            self.connector.stop()
            
            # Stop gesture control system
            if self.control_system:
                self.control_system.shutdown()
            
            # Wait for control thread to finish
            if self.control_thread and self.control_thread.is_alive():
                self.control_thread.join(timeout=2.0)
            
            self.logger.info("Game engine shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_status(self) -> dict:
        """Get comprehensive engine status."""
        status = {
            'running': self.running,
            'game_mode': self.game_mode,
            'control_system_initialized': self.control_system.is_initialized if self.control_system else False,
            'connector_status': self.connector.get_status() if self.connector else {},
        }
        
        if self.game:
            status['game_stats'] = self.game.get_game_stats()
        
        if self.control_system:
            status['control_system_status'] = self.control_system.get_status()
        
        return status
