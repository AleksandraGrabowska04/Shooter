"""
Control Connector for game integration.

This module translates gesture-derived control state into
game commands with deadzone filtering and cooldowns.
"""

import time
from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from threading import Thread, Lock
import queue

from gesture_control.core.types import ControlState, HandState
from gesture_control.core.interfaces import ILogger


@dataclass(frozen=True)
class InputDeadzoneConfig:
    """Deadzone and activation thresholds for gesture-driven input."""
    movement_deadzone: float = 0.2
    movement_min_magnitude: float = 0.02
    rotation_deadzone: float = 0.08
    tilt_deadzone: float = 0.18
    nod_deadzone: float = 0.18


class GameCommand:
    """Represents a game command derived from gesture input."""
    
    def __init__(self, command_type: str, data: Optional[Dict[str, Any]] = None):
        self.command_type = command_type
        self.data = data or {}
        self.timestamp = time.time()
    
    def __str__(self):
        return f"GameCommand({self.command_type}, {self.data})"


class ControlConnector:
    """
    Connector that bridges control system with game logic.
    
    This class receives ControlState updates from the control system
    and translates them into game commands that can be consumed by any game.
    """
    
    def __init__(self, logger: ILogger, deadzones: Optional[InputDeadzoneConfig] = None):
        """
        Initialize the connector.
        
        Args:
            logger: Logger instance for debugging
            deadzones: Optional deadzone configuration for gesture thresholds
        """
        self.logger = logger
        self.deadzones = deadzones or InputDeadzoneConfig()
        self._command_queue = queue.Queue()
        self._game_callback: Optional[Callable[[GameCommand], None]] = None
        self._last_movement_time = 0.0
        self._last_rotation_time = 0.0
        self._last_shoot_time = 0.0
        self._last_mode_change_time = 0.0
        self._last_reload_time = 0.0
        self._last_control_state: Optional[ControlState] = None
        self._movement_active = False
        self._turn_armed = True
        self._nod_armed = True
        
        self._running = False
        self._thread: Optional[Thread] = None
        self._lock = Lock()
        
        # Timing thresholds
        self._movement_update_interval = 0.03  # 30ms for smooth movement
        self._rotation_update_interval = 0.02  # 20ms for smooth rotation
        self._shoot_cooldown = 0.3           # 300ms between shots
        self._mode_change_cooldown = 0.8     # 800ms between mode changes
        self._reload_cooldown = 1.5          # 1.5s between reload attempts
        
        self.logger.info("Control Connector initialized")
    
    def set_game_callback(self, callback: Callable[[GameCommand], None]) -> None:
        """
        Set callback function that will receive game commands.
        
        Args:
            callback: Function to call with GameCommand objects
        """
        with self._lock:
            self._game_callback = callback
        self.logger.info("Game callback registered")
    
    def start(self) -> None:
        """Start the connector thread for processing commands."""
        if self._running:
            return
        
        self._running = True
        self._thread = Thread(target=self._process_commands, daemon=True)
        self._thread.start()
        self.logger.info("Control Connector started")
    
    def stop(self) -> None:
        """Stop the connector and cleanup resources."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None
        self.logger.info("Control Connector stopped")
    
    def update_control_state(self, control_state: ControlState) -> None:
        """
        Update with new control state from control system.
        
        Args:
            control_state: Current control state with gesture information
        """
        self._last_control_state = control_state
        if not control_state.is_active:
            # Send deactivation command
            self._add_command("DEACTIVATE", {"reason": "control_off"})
            self._movement_active = False
            self._turn_armed = True
            self._nod_armed = True
            return
        
        try:
            current_time = time.time()
            
            # Process different types of input
            self._process_movement(control_state, current_time)
            self._process_rotation(control_state, current_time)
            self._process_shooting(control_state, current_time)
            self._process_mode_changes(control_state, current_time)
            self._process_reload(control_state, current_time)
            
        except Exception as e:
            self.logger.error(f"Error processing control state: {e}")
    
    def _process_movement(self, control_state: ControlState, current_time: float) -> None:
        """Process movement commands from hand position vectors."""
        if current_time - self._last_movement_time < self._movement_update_interval:
            return
        
        movement = control_state.movement_vector
        if not movement:
            if self._movement_active:
                self._add_command("MOVEMENT", {
                    'vector': (0, 0),
                    'velocity': (0, 0),
                    'magnitude': 0,
                    'stop': True
                })
                self._movement_active = False
                self._last_movement_time = current_time
            return

        in_deadzone = movement.in_deadzone(self.deadzones.movement_deadzone)
        if in_deadzone or movement.magnitude < self.deadzones.movement_min_magnitude:
            if self._movement_active:
                self._add_command("MOVEMENT", {
                    'vector': (0, 0),
                    'velocity': (0, 0),
                    'magnitude': 0,
                    'stop': True
                })
                self._movement_active = False
                self._last_movement_time = current_time
            return

        movement_data = {
            'vector': movement.displacement.to_tuple(),
            'velocity': movement.velocity.to_tuple() if movement.velocity else (0, 0),
            'magnitude': movement.magnitude,
            'acceleration': True
        }

        self._add_command("MOVEMENT", movement_data)
        self._movement_active = True
        self._last_movement_time = current_time
    
    def _process_rotation(self, control_state: ControlState, current_time: float) -> None:
        """Process rotation commands from head tilt."""
        if current_time - self._last_rotation_time < self._rotation_update_interval:
            return
        
        rotation = control_state.rotation_vector
        if not rotation:
            return

        if abs(rotation.tilt) < self.deadzones.tilt_deadzone:
            return

        rotation_data = {
            'tilt': rotation.tilt,
            'turn': rotation.turn,
            'nod': rotation.nod,
            'magnitude': rotation.magnitude
        }

        self._add_command("ROTATION", rotation_data)
        self._last_rotation_time = current_time
    
    def _process_shooting(self, control_state: ControlState, current_time: float) -> None:
        """Process shooting commands from hand state."""
        if current_time - self._last_shoot_time < self._shoot_cooldown:
            return
        
        if (control_state.is_calibrated and
                control_state.hand_state == HandState.FIST):
            shoot_data = {
                'hand_state': control_state.hand_state.value
            }
            
            self._add_command("SHOOT", shoot_data)
            self._last_shoot_time = current_time
    
    def _process_mode_changes(self, control_state: ControlState, current_time: float) -> None:
        """Process mode change commands from head turn."""
        if current_time - self._last_mode_change_time < self._mode_change_cooldown:
            return
        
        rotation = control_state.rotation_vector
        if not rotation:
            self._turn_armed = True
            return

        if abs(rotation.turn) < self.deadzones.rotation_deadzone:
            self._turn_armed = True
            return

        if not self._turn_armed:
            return

        mode_change = "next" if rotation.turn > 0 else "previous"
        mode_data = {
            'change_direction': mode_change,
            'turn': rotation.turn
        }

        self._add_command("MODE_CHANGE", mode_data)
        self._turn_armed = False
        self._last_mode_change_time = current_time
    
    def _process_reload(self, control_state: ControlState, current_time: float) -> None:
        """Process reload commands from head pitch."""
        if current_time - self._last_reload_time < self._reload_cooldown:
            return
        
        rotation = control_state.rotation_vector
        if not rotation:
            self._nod_armed = True
            return

        if abs(rotation.nod) < self.deadzones.nod_deadzone:
            self._nod_armed = True
            return

        if not self._nod_armed:
            return

        reload_data = {
            'nod': rotation.nod
        }

        self._add_command("RELOAD", reload_data)
        self._nod_armed = False
        self._last_reload_time = current_time
    
    def _add_command(self, command_type: str, data: Dict[str, Any]) -> None:
        """Add a command to the processing queue."""
        try:
            command = GameCommand(command_type, data)
            self._command_queue.put(command, block=False)
        except queue.Full:
            self.logger.warning("Command queue full, dropping command")
    
    def _process_commands(self) -> None:
        """Process commands in separate thread and send to game."""
        while self._running:
            try:
                # Get command with timeout
                command = self._command_queue.get(timeout=0.1)
                
                # Send to game if callback is set
                with self._lock:
                    if self._game_callback:
                        self._game_callback(command)
                
                # Mark task as done
                self._command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing command: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connector status information."""
        last_state = self._last_control_state
        return {
            'running': self._running,
            'has_game_callback': self._game_callback is not None,
            'queue_size': self._command_queue.qsize(),
            'last_movement_time': self._last_movement_time,
            'last_rotation_time': self._last_rotation_time,
            'last_shoot_time': self._last_shoot_time,
            'deadzones': self.deadzones.__dict__,
            'last_hand_state': getattr(last_state.hand_state, "value", None) if last_state else None,
            'last_rotation_vector': getattr(last_state.rotation_vector, "__dict__", None) if last_state else None,
            'last_movement_vector': getattr(last_state.movement_vector, "__dict__", None) if last_state else None
        }
    
    def flush_commands(self) -> None:
        """Clear all pending commands from queue."""
        while not self._command_queue.empty():
            try:
                self._command_queue.get_nowait()
                self._command_queue.task_done()
            except queue.Empty:
                break
        self.logger.info("Command queue flushed")
