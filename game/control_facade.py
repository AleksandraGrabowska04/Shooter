"""
Facade for integrating hand control with custom games.

This module converts connector commands into typed events and
exposes a small API that hides the low-level routing details.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from hand_control.core.interfaces import ILogger
from hand_control.core.types import ControlState

from .connector import ControlConnector, GameCommand, InputDeadzoneConfig


@dataclass(frozen=True)
class MovementEvent:
    """Movement input derived from gesture data."""
    vector: Tuple[float, float]
    velocity: Tuple[float, float]
    magnitude: float
    stop: bool


@dataclass(frozen=True)
class RotationEvent:
    """Rotation input derived from head movement."""
    tilt: float
    turn: float
    nod: float
    magnitude: float


@dataclass(frozen=True)
class ActionEvent:
    """Action input such as shooting or triggering a pulse."""
    hand_state: str


@dataclass(frozen=True)
class ModeChangeEvent:
    """Mode change input derived from head tilt."""
    direction: str
    tilt: float


@dataclass(frozen=True)
class ReloadEvent:
    """Reload input derived from head nod."""
    nod: float


@dataclass(frozen=True)
class DeactivateEvent:
    """Deactivation input when control is inactive."""
    reason: str


class GameControlHandler:
    """Override the callbacks you care about in your game logic."""

    def on_movement(self, event: MovementEvent) -> None:
        pass

    def on_rotation(self, event: RotationEvent) -> None:
        pass

    def on_action(self, event: ActionEvent) -> None:
        pass

    def on_mode_change(self, event: ModeChangeEvent) -> None:
        pass

    def on_reload(self, event: ReloadEvent) -> None:
        pass

    def on_deactivate(self, event: DeactivateEvent) -> None:
        pass


class GameControlFacade:
    """
    Facade that connects hand control updates with a game handler.

    It hides the command queue and threading details from callers.
    """

    def __init__(
        self,
        logger: ILogger,
        handler: GameControlHandler,
        deadzones: Optional[InputDeadzoneConfig] = None,
    ) -> None:
        self._logger = logger
        self._handler = handler
        self._connector = ControlConnector(logger, deadzones)
        self._connector.set_game_callback(self._dispatch_command)

    def start(self) -> None:
        """Start processing commands."""
        self._connector.start()

    def stop(self) -> None:
        """Stop processing commands and clean up resources."""
        self._connector.stop()

    def update_control_state(self, control_state: ControlState) -> None:
        """Send a control state update to the connector."""
        self._connector.update_control_state(control_state)

    def get_status(self) -> Dict[str, object]:
        """Expose connector status for diagnostics."""
        return self._connector.get_status()

    def flush_commands(self) -> None:
        """Clear all pending commands."""
        self._connector.flush_commands()

    def _dispatch_command(self, command: GameCommand) -> None:
        data = command.data or {}
        command_type = command.command_type

        if command_type == "MOVEMENT":
            vector = _to_vector2(data.get("vector"), (0.0, 0.0))
            velocity = _to_vector2(data.get("velocity"), (0.0, 0.0))
            magnitude = _to_float(data.get("magnitude"), _vector_magnitude(vector))
            stop = bool(data.get("stop", False))
            self._handler.on_movement(
                MovementEvent(
                    vector=vector,
                    velocity=velocity,
                    magnitude=magnitude,
                    stop=stop,
                )
            )
            return

        if command_type == "ROTATION":
            tilt = _to_float(data.get("tilt"), 0.0)
            turn = _to_float(data.get("turn"), 0.0)
            nod = _to_float(data.get("nod"), 0.0)
            magnitude = _to_float(
                data.get("magnitude"),
                math.sqrt(tilt * tilt + turn * turn + nod * nod),
            )
            self._handler.on_rotation(
                RotationEvent(
                    tilt=tilt,
                    turn=turn,
                    nod=nod,
                    magnitude=magnitude,
                )
            )
            return

        if command_type == "SHOOT":
            hand_state = str(data.get("hand_state", "unknown"))
            self._handler.on_action(ActionEvent(hand_state=hand_state))
            return

        if command_type == "MODE_CHANGE":
            direction = str(data.get("change_direction", "next"))
            tilt = _to_float(data.get("tilt"), 0.0)
            self._handler.on_mode_change(
                ModeChangeEvent(direction=direction, tilt=tilt)
            )
            return

        if command_type == "RELOAD":
            nod = _to_float(data.get("nod"), 0.0)
            self._handler.on_reload(ReloadEvent(nod=nod))
            return

        if command_type == "DEACTIVATE":
            reason = str(data.get("reason", "control_off"))
            self._handler.on_deactivate(DeactivateEvent(reason=reason))
            return

        self._logger.warning(f"Unknown command type: {command_type}")


def _to_vector2(value: object, default: Tuple[float, float]) -> Tuple[float, float]:
    if isinstance(value, (list, tuple)) and len(value) >= 2:
        try:
            return (float(value[0]), float(value[1]))
        except (TypeError, ValueError):
            return default
    return default


def _to_float(value: object, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _vector_magnitude(vector: Tuple[float, float]) -> float:
    return math.hypot(vector[0], vector[1])
