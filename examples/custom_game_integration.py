"""
Example of integrating the hand control system with a custom game.

This example uses GameControlFacade to expose a small, clear API and
hide the low-level command routing details.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

from hand_control.core.config.application_config import ApplicationConfig
from hand_control.core.types import (
    ControlState,
    HandState,
    MovementVector,
    RotationVector,
    Vector2D,
)
from hand_control.utils.factory import DefaultLogger

from game.control_facade import (
    ActionEvent,
    DeactivateEvent,
    GameControlFacade,
    GameControlHandler,
    ModeChangeEvent,
    MovementEvent,
    ReloadEvent,
    RotationEvent,
)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MOVE_SCALE_X = 220
MOVE_SCALE_Y = 160
VELOCITY_SCALE = 0.15


@dataclass(frozen=True)
class SimulationStep:
    label: str
    control_state: ControlState


class ControlStateSimulator:
    def __init__(
        self,
        facade: GameControlFacade,
        steps: Iterable[SimulationStep],
        pause_s: float = 2.0,
    ) -> None:
        self._facade = facade
        self._steps = list(steps)
        self._pause_s = pause_s

    def run(self) -> None:
        for step in self._steps:
            print(f"\nSimulating: {step.label}")
            self._facade.update_control_state(step.control_state)
            time.sleep(self._pause_s)


class MyCustomGame(GameControlHandler):
    """Example custom game that reacts to structured control events."""

    def __init__(self) -> None:
        self.running = True
        self.player_position = [SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2]
        self.score = 0
        self.actions_triggered = 0

        print("Custom Game initialized")
        print("Player starting at:", self.player_position)

    def on_movement(self, event: MovementEvent) -> None:
        if event.stop:
            print("Movement stop")
            return

        delta_x = event.vector[0] * MOVE_SCALE_X + event.velocity[0] * VELOCITY_SCALE
        delta_y = event.vector[1] * MOVE_SCALE_Y + event.velocity[1] * VELOCITY_SCALE

        self.player_position[0] = _clamp(
            self.player_position[0] + delta_x, 0, SCREEN_WIDTH
        )
        self.player_position[1] = _clamp(
            self.player_position[1] + delta_y, 0, SCREEN_HEIGHT
        )

        print(
            "Player moved to:",
            self.player_position,
            f"(vector: {event.vector}, velocity: {event.velocity})",
        )

    def on_action(self, event: ActionEvent) -> None:
        self.actions_triggered += 1
        self.score += 1

        print(
            "Action triggered from",
            self.player_position,
            f"(hand: {event.hand_state})",
            f"[actions: {self.actions_triggered}, score: {self.score}]",
        )

    def on_rotation(self, event: RotationEvent) -> None:
        print(
            "Head rotation:",
            f"tilt={event.tilt:.2f}",
            f"turn={event.turn:.2f}",
            f"nod={event.nod:.2f}",
        )

    def on_mode_change(self, event: ModeChangeEvent) -> None:
        print(f"Mode change requested: {event.direction}")

    def on_reload(self, event: ReloadEvent) -> None:
        print(f"Recharge triggered (nod: {event.nod:.2f})")

    def on_deactivate(self, event: DeactivateEvent) -> None:
        print("Hand control deactivated")

    def get_status(self) -> Dict[str, Any]:
        return {
            "position": self.player_position,
            "score": self.score,
            "actions_triggered": self.actions_triggered,
            "running": self.running,
        }

    def update(self) -> None:
        # Add your game logic here
        pass

    def stop(self) -> None:
        self.running = False
        print("Custom game stopped")


def _build_config() -> ApplicationConfig:
    config = ApplicationConfig()
    config.enable_debug_mode = True
    config.ui.show_debug_info = True
    return config


def _build_simulation_steps() -> List[SimulationStep]:
    return [
        SimulationStep(
            "Hand control activated",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Active",
                hand_state=HandState.OPEN,
            ),
        ),
        SimulationStep(
            "Move right",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Moving right",
                hand_state=HandState.OPEN,
                movement_vector=MovementVector(
                    displacement=Vector2D(0.35, 0.0),
                    velocity=Vector2D(0.18, 0.0),
                ),
            ),
        ),
        SimulationStep(
            "Rotate right",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Rotating",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.0, turn=0.6, nod=0.0),
            ),
        ),
        SimulationStep(
            "Cycle mode",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Mode change",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.45, turn=0.0, nod=0.0),
            ),
        ),
        SimulationStep(
            "Recharge",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Recharge",
                hand_state=HandState.OPEN,
                rotation_vector=RotationVector(tilt=0.0, turn=0.0, nod=0.55),
            ),
        ),
        SimulationStep(
            "Action",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Action",
                hand_state=HandState.FIST,
            ),
        ),
        SimulationStep(
            "Move up-left",
            ControlState(
                is_active=True,
                is_calibrated=True,
                status_message="Moving up-left",
                hand_state=HandState.OPEN,
                movement_vector=MovementVector(
                    displacement=Vector2D(-0.4, -0.3),
                    velocity=Vector2D(-0.2, -0.15),
                ),
            ),
        ),
    ]


def _print_intro() -> None:
    print("\n" + "=" * 50)
    print("CUSTOM GAME FACADE EXAMPLE")
    print("=" * 50)
    print("This example shows how to use GameControlFacade.")
    print("In real usage, connect your hand control system.")
    print("Press Ctrl+C to exit")
    print("=" * 50 + "\n")


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def main() -> None:
    config = _build_config()
    logger = DefaultLogger("CustomGameExample", config)
    logger.info("Starting custom game example")

    game = MyCustomGame()
    facade = GameControlFacade(logger, game)
    facade.start()

    try:
        _print_intro()

        simulator = ControlStateSimulator(facade, _build_simulation_steps())
        simulator.run()

        print(f"Simulation complete. Game status: {game.get_status()}")
        print("To integrate with real hand control, call:")
        print("  facade.update_control_state(control_state)")
        print("  where control_state comes from your gesture recognition.")

        while game.running:
            game.update()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping example...")

    finally:
        facade.stop()
        game.stop()
        logger.info("Custom game example finished")


if __name__ == "__main__":
    main()
