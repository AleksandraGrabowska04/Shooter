"""
Gesture control connector for Wolfenstein.
"""

from __future__ import annotations

import time
from typing import Optional, Tuple

from gesture_control.core import ApplicationConfig, create_gesture_control_system
from gesture_control.core.types import ControlState, HandState
from gesture_control.utils.factory import DefaultLogger
from settings import (
    GESTURE_MOVE_SCALE,
    GESTURE_TURN_SCALE,
    GESTURE_MOVE_DEADZONE,
    GESTURE_ACTION_THRESHOLD,
    GESTURE_ACTION_COOLDOWN,
)


class WolfensteinGestureConnector:
    def __init__(self, engine, config: Optional[ApplicationConfig] = None) -> None:
        self.engine = engine
        self.config = config or ApplicationConfig()
        self.logger = DefaultLogger("WolfensteinGesture", self.config)
        self.system = create_gesture_control_system(self.config, self.logger)

        self._running = False
        self._last_weapon_change_time = 0.0
        self._last_shot_time = 0.0
        self._last_action_time = 0.0

        self.weapon_change_cooldown = 0.7
        self.shoot_cooldown = 0.25
        self.tilt_weapon_threshold = 0.35
        self.move_scale = GESTURE_MOVE_SCALE
        self.turn_scale = GESTURE_TURN_SCALE
        self.move_deadzone = GESTURE_MOVE_DEADZONE
        self.nod_action_threshold = GESTURE_ACTION_THRESHOLD
        self.action_cooldown = GESTURE_ACTION_COOLDOWN

    def initialize(self) -> bool:
        if not self.system.initialize():
            self.logger.error("Failed to initialize gesture control system")
            return False

        self.system.lifecycle_manager.start_system()
        if self.config.require_calibration:
            self.system.calibration_manager.run_calibration()

        self._running = True
        return True

    def shutdown(self) -> None:
        self._running = False
        if self.system:
            self.system.shutdown()

    def update(self) -> None:
        if not self._running or not self.system.frame_processor:
            return

        analysis = self.system.frame_processor.analyze_frame()
        control_state = analysis.control_state if analysis else None
        if not control_state:
            self._apply_gesture_input(active=False)
            return

        self._apply_control_state(control_state)

    def _apply_control_state(self, control_state: ControlState) -> None:
        active = bool(control_state.is_active and control_state.is_calibrated)
        move_vec = (0.0, 0.0)
        if control_state.movement_vector:
            max_distance = self.config.strategies.position.max_distance_from_calibration
            dx = float(control_state.movement_vector.displacement.x)
            dy = float(control_state.movement_vector.displacement.y)
            if max_distance > 0:
                dx = dx / max_distance
                dy = dy / max_distance
            dx *= self.move_scale
            dy *= self.move_scale
            magnitude = (dx * dx + dy * dy) ** 0.5
            if magnitude < self.move_deadzone:
                dx = 0.0
                dy = 0.0
            else:
                dx = max(-1.0, min(1.0, dx))
                dy = max(-1.0, min(1.0, dy))
            move_vec = (dx, dy)

        look_turn = 0.0
        if control_state.rotation_vector:
            look_turn = float(control_state.rotation_vector.turn) * self.turn_scale
            look_turn = max(-1.0, min(1.0, look_turn))

        shoot = False
        current_time = time.time()
        if (active and control_state.hand_state == HandState.FIST and
                current_time - self._last_shot_time >= self.shoot_cooldown):
            shoot = True
            self._last_shot_time = current_time

        weapon_change = 0
        if control_state.rotation_vector:
            tilt = float(control_state.rotation_vector.tilt)
            if (abs(tilt) >= self.tilt_weapon_threshold and
                    current_time - self._last_weapon_change_time >= self.weapon_change_cooldown):
                weapon_change = 1 if tilt > 0 else -1
                self._last_weapon_change_time = current_time

        interact = False
        if active and control_state.rotation_vector:
            nod = float(control_state.rotation_vector.nod)
            if (abs(nod) >= self.nod_action_threshold and
                    current_time - self._last_action_time >= self.action_cooldown):
                interact = True
                self._last_action_time = current_time

        self._apply_gesture_input(
            active=active,
            move=move_vec,
            turn=look_turn,
            shoot=shoot,
            weapon_change=weapon_change,
            interact=interact,
        )

    def _apply_gesture_input(
        self,
        active: bool,
        move: Tuple[float, float] = (0.0, 0.0),
        turn: float = 0.0,
        shoot: bool = False,
        weapon_change: int = 0,
        interact: bool = False,
    ) -> None:
        player = self.engine.player
        if not player:
            return

        move_x, move_y = move
        player.set_gesture_input(
            active=active,
            move=(move_x, move_y),
            turn=turn,
            shoot=shoot,
            weapon_change=weapon_change,
            interact=interact,
        )
