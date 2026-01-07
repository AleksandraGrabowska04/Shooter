"""
Example of using the Hand Control Connector with a custom game.

This example shows how to integrate the hand control system
with your own game logic using the provided connector.
"""

import time
from typing import Dict, Any
from hand_control.core.config.application_config import ApplicationConfig
from hand_control.utils.factory import DefaultLogger
from game.connector import ControlConnector, GameCommand


class MyCustomGame:
    """Example custom game that uses hand control connector."""
    
    def __init__(self):
        """Initialize the custom game."""
        self.running = True
        self.player_position = [400, 300]  # Center of 800x600 screen
        self.score = 0
        self.actions_triggered = 0
        
        print("🎮 Custom Game initialized")
        print("Player starting at:", self.player_position)
    
    def handle_game_command(self, command: GameCommand) -> None:
        """
        Handle game commands from hand control connector.
        
        Args:
            command: Game command from hand control system
        """
        print(f"🎯 Received command: {command}")
        
        if command.command_type == "MOVEMENT":
            self._handle_movement(command.data)
        elif command.command_type == "SHOOT":
            self._handle_action(command.data)
        elif command.command_type == "MODE_CHANGE":
            self._handle_mode_change(command.data)
        elif command.command_type == "RELOAD":
            self._handle_reload(command.data)
        elif command.command_type == "DEACTIVATE":
            print("❌ Hand control deactivated")
        elif command.command_type == "ROTATION":
            self._handle_head_rotation(command.data)
    
    def _handle_movement(self, data: Dict[str, Any]) -> None:
        """Handle movement commands."""
        if data.get("stop"):
            print("🛑 Movement stop")
            return

        vector = data.get('vector', (0.0, 0.0))
        velocity = data.get('velocity', (0.0, 0.0))
        if isinstance(vector, (list, tuple)) and len(vector) >= 2:
            if not (isinstance(velocity, (list, tuple)) and len(velocity) >= 2):
                velocity = (0.0, 0.0)

            scale_x, scale_y = 220, 160
            vel_scale = 0.15
            delta_x = float(vector[0]) * scale_x + float(velocity[0]) * vel_scale
            delta_y = float(vector[1]) * scale_y + float(velocity[1]) * vel_scale

            self.player_position[0] = max(0, min(800, self.player_position[0] + delta_x))
            self.player_position[1] = max(0, min(600, self.player_position[1] + delta_y))

            print(f"🏃 Player moved to: {self.player_position} "
                  f"(vector: {vector}, velocity: {velocity})")
    
    def _handle_action(self, data: Dict[str, Any]) -> None:
        """Handle action commands."""
        self.actions_triggered += 1
        self.score += 1  # Simple scoring
        
        hand_state = data.get('hand_state', 'unknown')
        print(f"💥 ACTION! Triggered from {self.player_position} "
              f"(hand: {hand_state}) "
              f"[Total actions: {self.actions_triggered}, Score: {self.score}]")
    
    def _handle_head_rotation(self, data: Dict[str, Any]) -> None:
        """Handle head rotation commands."""
        tilt = data.get('tilt', 0.0)
        turn = data.get('turn', 0.0)
        nod = data.get('nod', 0.0)
        print(f"🧭 Head rotation: tilt={tilt:.2f} turn={turn:.2f} nod={nod:.2f}")

    def _handle_mode_change(self, data: Dict[str, Any]) -> None:
        """Handle mode change commands."""
        direction = data.get('change_direction', 'next')
        print(f"🧩 Mode change requested: {direction}")

    def _handle_reload(self, data: Dict[str, Any]) -> None:
        """Handle reload commands."""
        nod = data.get('nod', 0.0)
        print(f"🔋 Recharge triggered (nod: {nod:.2f})")
    
    def get_status(self) -> Dict[str, Any]:
        """Get game status."""
        return {
            'position': self.player_position,
            'score': self.score,
            'actions_triggered': self.actions_triggered,
            'running': self.running
        }
    
    def update(self) -> None:
        """Update game state (called in main loop)."""
        # Add your game logic here
        pass
    
    def stop(self) -> None:
        """Stop the game."""
        self.running = False
        print("🛑 Custom game stopped")


def main():
    """Example of integrating hand control with custom game."""
    
    # Setup configuration
    config = ApplicationConfig()
    config.enable_debug_mode = True
    config.ui.show_debug_info = True
    
    # Create logger
    logger = DefaultLogger("CustomGameExample", config)
    logger.info("🚀 Starting custom game example")
    
    # Create game
    game = MyCustomGame()
    
    # Create connector  
    connector = ControlConnector(logger)
    connector.set_game_callback(game.handle_game_command)
    connector.start()
    
    try:
        # Simulate hand control system sending commands
        # In real usage, your hand control system would call:
        # connector.update_control_state(control_state)
        
        print("\n" + "="*50)
        print("🎮 CUSTOM GAME CONNECTOR EXAMPLE")
        print("="*50)
        print("This example shows how to use the connector.")
        print("In real usage, connect your hand control system!")
        print("Press Ctrl+C to exit")
        print("="*50 + "\n")
        
        # Simulate some commands for demonstration
        from hand_control.core.types import (
            ControlState,
            HandState,
            MovementVector,
            RotationVector,
            Vector2D
        )
        
        simulation_commands = [
            # Activation
            ("Hand control activated", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Active",
                hand_state=HandState.OPEN,
                all_gestures=[]
            )),
            
            # Movement
            ("Move right", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Moving right",
                hand_state=HandState.OPEN,
                movement_vector=MovementVector(
                    displacement=Vector2D(0.35, 0.0),
                    velocity=Vector2D(0.18, 0.0)
                )
            )),
            
            # Rotation without tilt/nod
            ("Rotate right", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Rotating",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.0, turn=0.6, nod=0.0)
            )),

            # Mode change (head tilt)
            ("Cycle mode", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Mode change",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.45, turn=0.0, nod=0.0)
            )),

            # Recharge (head nod)
            ("Recharge", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Recharge",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.0, turn=0.0, nod=0.55)
            )),
            
            # Action
            ("Action!", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Action",
                hand_state=HandState.FIST
            )),
            
            # Movement with displacement
            ("Move up-left", ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Moving up-left",
                hand_state=HandState.OPEN,
                movement_vector=MovementVector(
                    displacement=Vector2D(-0.4, -0.3),
                    velocity=Vector2D(-0.2, -0.15)
                )
            )),
        ]
        
        # Run simulation
        for description, control_state in simulation_commands:
            print(f"\n🔄 Simulating: {description}")
            connector.update_control_state(control_state)
            time.sleep(2)
        
        # Keep running for manual testing
        print(f"\n✅ Simulation complete. Game status: {game.get_status()}")
        print("💡 To integrate with real hand control, use the HandControlSystem and call:")
        print("   connector.update_control_state(control_state)")
        print("   where control_state comes from your gesture recognition.")
        
        # Wait for user to stop
        while game.running:
            game.update()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping example...")
    finally:
        connector.stop()
        game.stop()
        logger.info("🏁 Custom game example finished")


if __name__ == "__main__":
    main()
