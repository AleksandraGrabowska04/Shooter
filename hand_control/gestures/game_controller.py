"""
Game controller for processing gesture results into control commands.
"""

from typing import List, Dict, Any

from ..core.interfaces import IGameController, ILogger
from ..core.config import ApplicationConfig
from ..core.types import (
    ControlState, GestureResult,
    HandState, PositionGesture, OrientationGesture, MotionGesture
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
            # Extract gesture information by type
            gesture_data = self._gesture_processor.categorize_gestures(
                gesture_results)

            # Determine hand state and handle recalibration
            hand_state = self._gesture_processor.determine_hand_state(
                gesture_data)
            recalibration_triggered = self._hand_tracker.update_hand_state(
                hand_state)

            # System is active only when fist is detected
            is_active = hand_state == HandState.FIST

            # Process other gestures only when system is active (fist detected)
            if is_active:
                position_gesture = self._gesture_processor.determine_position_gesture(
                    gesture_data)
                orientation_gesture = self._gesture_processor.determine_orientation_gesture(
                    gesture_data)
                motion_gesture = self._gesture_processor.determine_motion_gesture(
                    gesture_data)
                special_action = self._gesture_processor.check_special_gestures(
                    gesture_data)
                primary_gesture = self._gesture_processor.find_primary_gesture(
                    gesture_results)
            else:
                position_gesture = PositionGesture.CENTER
                orientation_gesture = OrientationGesture.NEUTRAL
                motion_gesture = MotionGesture.STATIC
                special_action = None
                primary_gesture = None

            # Generate status message
            status_message = self._status_generator.generate_status_message(
                hand_state, position_gesture, orientation_gesture, motion_gesture, gesture_data, special_action
            )

            # Create control state
            control_state = ControlState(
                is_active=is_active,
                is_calibrated=True,  # Assume calibrated if we have gestures
                status_message=status_message,
                hand_state=hand_state,
                position_gesture=position_gesture,
                orientation_gesture=orientation_gesture,
                motion_gesture=motion_gesture,
                primary_gesture=primary_gesture,
                all_gestures=gesture_results
            )

            # Apply smoothing
            smoothed_state = self._control_smoother.apply_smoothing(
                control_state)

            if self._debug_mode:
                self.logger.debug(f"Control state: {status_message}")

            return smoothed_state

        except Exception as e:
            self.logger.error(f"Error processing gestures: {e}")

            # Return safe default state on error
            return ControlState(
                is_active=False,
                is_calibrated=False,
                status_message="Error processing gestures",
                hand_state=HandState.NONE,
                position_gesture=PositionGesture.CENTER,
                orientation_gesture=OrientationGesture.NEUTRAL,
                motion_gesture=MotionGesture.STATIC,
                primary_gesture=None,
                all_gestures=[]
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

        Args:
            gesture_results: List of current gesture results

        Returns:
            Dictionary with gesture summary information
        """
        gesture_data = self._gesture_processor.categorize_gestures(
            gesture_results)

        summary = {
            'total_gestures': len(gesture_results),
            'gesture_types': list(gesture_data.keys()),
            'confidence_scores': {
                str(gtype): [g.confidence for g in gestures]
                for gtype, gestures in gesture_data.items()
            },
            'hand_state': self._gesture_processor.determine_hand_state(gesture_data).value,
            'position': self._gesture_processor.determine_position_gesture(gesture_data).value,
            'orientation': self._gesture_processor.determine_orientation_gesture(gesture_data).value,
            'motion': self._gesture_processor.determine_motion_gesture(gesture_data).value
        }

        return summary

    def set_reset_calibration_callback(self, callback):
        """Set callback function for resetting calibration."""
        self._hand_tracker.set_reset_calibration_callback(callback)
        self.logger.info(f"Reset calibration callback set: {callback is not None}")

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
