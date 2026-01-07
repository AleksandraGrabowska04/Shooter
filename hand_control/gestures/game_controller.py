"""
Game controller for processing gesture results into control commands.
"""

from typing import List, Dict, Any

from ..core.interfaces import IGameController, ILogger
from ..core.config import ApplicationConfig
from ..core.types import (
    ControlState, GestureResult,
    HandState, PositionGesture
)
from .controllers import (
    HandStateTracker, GestureProcessor,
    StatusMessageGenerator, ControlStateSmoother
)


class GameController(IGameController):
    """
    Game controller that processes gesture results into control state.
    This controller translates raw gesture detection results into meaningful
    game control commands and state information.
    """

    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize game controller.

        Args:
            config: Application configuration
            logger: Logger instance for debugging
        """
        self.config = config
        self.logger = logger
        self._debug_mode = config.enable_debug_mode
        self._active = True

        self._reset_calibration_callback = None
        self._recalibrate_callback = None

        # Initialize specialized components
        self._hand_tracker = HandStateTracker(logger)
        self._gesture_processor = GestureProcessor(logger)
        self._status_generator = StatusMessageGenerator(logger)
        self._control_smoother = ControlStateSmoother(logger)

        # Configure components
        self._hand_tracker.set_debug_mode(self._debug_mode)
        self._gesture_processor.set_debug_mode(self._debug_mode)

        self.logger.info("Game controller initialized")

    def process_gestures(self, gesture_results: List[GestureResult]) -> ControlState:
        """
        Process gesture results and return control state.

        Args:
            gesture_results: List of detected gestures

        Returns:
            Control state with commands and status
        """
        try:
            # 1. Categorize raw results
            gesture_data = self._gesture_processor.categorize_gestures(
                gesture_results)

            # 2. Determine base hand state (Fist/Open)
            hand_state = self._gesture_processor.determine_hand_state(
                gesture_data)
            self._hand_tracker.update_hand_state(hand_state)

            # 3. Toggle activation state on activation gesture
            is_hand_activation = self._gesture_processor.check_activation_gesture(
                gesture_data)
            if is_hand_activation:
                self._active = not self._active
                self.logger.info(
                    f"[TOGGLE] Tracking state changed: {'ON' if self._active else 'OFF'}")
                # On OFF: reset calibration
                if not self._active and self._reset_calibration_callback:
                    self.logger.info("[TOGGLE] Resetting calibration (OFF)")
                    self._reset_calibration_callback()
                # On ON: recalibrate (if callback provided)
                elif self._active and self._recalibrate_callback:
                    self.logger.info("[TOGGLE] Recalibrating (ON)")
                    self._recalibrate_callback()
            is_active = self._active

            # 4. Extract Control Inputs - Use debug_info approach for consistency
            position_gesture = PositionGesture.CENTER
            special_action = None

            movement_vector = self._gesture_processor.extract_movement_vector(gesture_data)
            rotation_vector = self._gesture_processor.extract_rotation_vector(gesture_data)

            if is_active and hand_state == HandState.FIST:
                position_gesture = self._gesture_processor.determine_position_gesture(
                    gesture_data)
                special_action = "SHOOT"
            elif is_active:
                position_gesture = self._gesture_processor.determine_position_gesture(
                    gesture_data)

            primary_gesture = self._gesture_processor.find_primary_gesture(
                gesture_results)

            # 5. Generate User Feedback (Status Message)
            # Head gestures are always available for status
            status_message = self._status_generator.generate_status_message(
                hand_state,
                position_gesture,
                gesture_data,
                special_action
            )

            # Debug logging for game mode ONLY 
            if not self._debug_mode and is_active:
                self.logger.debug(f"[GAME] Movement vector: {movement_vector}")
                self.logger.debug(f"[GAME] Rotation vector: {rotation_vector}")
                self.logger.debug(f"[GAME] Hand state: {hand_state}, Special action: {special_action}")
                
            # 6. Construct Control State - ENHANCED with vectors
            # Note: ControlState needs to support extra fields if you want to pass Head Gestures
            # deeper into the game engine. For now, we attach all_gestures.
            control_state = ControlState(
                is_active=is_active,
                is_calibrated=True,  # Assuming calibrated if gestures are valid
                status_message=status_message,
                hand_state=hand_state,
                primary_gesture=primary_gesture,
                all_gestures=gesture_results,
                movement_vector=movement_vector,
                rotation_vector=rotation_vector
            )
            
            # Debug logging for game mode
            if not self._debug_mode and is_active:  # Only log in game mode
                if movement_vector:
                    self.logger.debug(f"🎮 Movement: mag={movement_vector.magnitude:.3f}, deadzone={movement_vector.in_deadzone}")
                if rotation_vector:
                    self.logger.debug(f"🎮 Rotation: tilt={rotation_vector.tilt:.2f}, turn={rotation_vector.turn:.2f}, nod={rotation_vector.nod:.2f}")
                if hand_state != HandState.NONE:
                    self.logger.debug(f"🎮 Hand: {hand_state.value}")

            # 7. Apply Smoothing (to position/state)
            smoothed_state = self._control_smoother.apply_smoothing(
                control_state)

            if self._debug_mode and self.config.ui.show_debug_info:
                # Log periodically or on change could be better
                pass

            return smoothed_state

        except Exception as e:
            self.logger.error(f"Error processing gestures: {e}")
            return ControlState(
                is_active=False,
                is_calibrated=False,
                status_message="Error processing gestures",
                hand_state=HandState.NONE,
                primary_gesture=None,
                all_gestures=[],
                movement_vector=None,
                rotation_vector=None
            )

    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = enabled
        self._hand_tracker.set_debug_mode(enabled)
        self._gesture_processor.set_debug_mode(enabled)
        self.logger.info(f"Debug mode {'enabled' if enabled else 'disabled'}")

    def is_active(self) -> bool:
        """Check if controller is currently active."""
        return self._active

    def get_gesture_summary(self, gesture_results: List[GestureResult]) -> Dict[str, Any]:
        """
        Get a summary of current gesture state for debugging.
        """
        gesture_data = self._gesture_processor.categorize_gestures(
            gesture_results)

        # Add head gestures to summary
        head_gestures = self._gesture_processor.get_head_gestures(gesture_data)

        # Activation only for hand gestures
        hand_state = self._gesture_processor.determine_hand_state(gesture_data)
        is_hand_activation = self._gesture_processor.check_activation_gesture(
            gesture_data)
        special_action = "SHOOT" if is_hand_activation and hand_state == HandState.FIST else None
        summary = {
            'total_gestures': len(gesture_results),
            'gesture_types': [t.name if hasattr(t, 'name') else str(t) for t in gesture_data.keys()],
            'hand_state': hand_state.value,
            'position': self._gesture_processor.determine_position_gesture(gesture_data).value,
            'special': special_action,
            'head': head_gestures
        }
        return summary

    def set_reset_calibration_callback(self, callback):
        """Set callback function for resetting calibration (OFF state)."""
        self._reset_calibration_callback = callback
        self._hand_tracker.set_reset_calibration_callback(callback)

    def set_recalibrate_callback(self, callback):
        """Set callback function for recalibrating (ON state)."""
        self._recalibrate_callback = callback

    def reset_state(self) -> None:
        """Reset controller state and history."""
        self._hand_tracker.reset_state()
        self._control_smoother.reset_state()
        self.logger.info("Controller state reset")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        smoother_metrics = self._control_smoother.get_performance_metrics()
        return {
            'last_update_time': smoother_metrics['last_update_time'],
            'history_size': smoother_metrics['history_size'],
            'is_active': self._active,
            'debug_mode': self._debug_mode
        }
