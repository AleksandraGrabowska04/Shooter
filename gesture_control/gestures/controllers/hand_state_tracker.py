"""
Hand state tracker for monitoring hand presence and state changes.
"""

from typing import Optional, Callable

from ...core.interfaces import ILogger
from ...core.types import HandState


class HandStateTracker:
    """
    Tracks hand state changes and manages recalibration logic.
    """

    def __init__(self, logger: ILogger):
        """
        Initialize hand state tracker.

        Args:
            logger: Logger instance for debugging
        """
        self.logger = logger
        self._last_hand_state = HandState.NONE
        self._hand_was_lost = True
        self._reset_calibration_callback: Optional[Callable] = None
        self._debug_mode = False

        # Fist state buffering for stability
        self._fist_buffer = []  # Buffer to track recent fist states
        # Require 7 consistent frames before changing state (increased for maximum rotation stability)
        self._fist_buffer_size = 7
        self._confirmed_fist_state = HandState.OPEN  # Last confirmed stable state

    def update_hand_state(self, current_state: HandState) -> bool:
        """
        Update hand state and check if recalibration is needed.

        Args:
            current_state: Current detected hand state

        Returns:
            True if recalibration should be triggered
        """
        # Handle hand loss
        if current_state == HandState.NONE:
            if not self._hand_was_lost:
                self.logger.info(f"� Hand lost - setting recalibration flag")
            self._hand_was_lost = True
            self._fist_buffer.clear()  # Clear buffer when hand is lost
            return False

        # Add current state to buffer (only for fist/open states)
        if current_state in [HandState.FIST, HandState.OPEN]:
            self._fist_buffer.append(current_state)

            # Keep buffer at fixed size
            if len(self._fist_buffer) > self._fist_buffer_size:
                self._fist_buffer.pop(0)

        # Determine stable state from buffer with bias towards fist retention
        buffered_state = current_state  # Default to current state
        if len(self._fist_buffer) >= self._fist_buffer_size:
            # Count fist vs open states in buffer
            fist_count = sum(
                1 for state in self._fist_buffer if state == HandState.FIST)
            open_count = sum(
                1 for state in self._fist_buffer if state == HandState.OPEN)

            # For stability during rotation, require strong evidence to change from fist to open
            if self._confirmed_fist_state == HandState.FIST:
                # If we're in fist state, require overwhelming evidence (80%) to switch to open
                # 80% threshold for maximum stability
                if open_count > (self._fist_buffer_size * 0.8):
                    buffered_state = HandState.OPEN
                else:
                    buffered_state = HandState.FIST  # Stay in fist state
            else:
                # If we're in open state, switch to fist with lower threshold (30%)
                # 30% threshold for switching to fist
                if fist_count >= (self._fist_buffer_size * 0.3):
                    buffered_state = HandState.FIST
                else:
                    buffered_state = HandState.OPEN
        else:
            # Not enough data - use confirmed state for stability
            buffered_state = self._confirmed_fist_state

        # Log state transitions
        if self._debug_mode and buffered_state != self._last_hand_state:
            self.logger.info(
                f"[TRANSITION] HAND STATE: {self._last_hand_state.value if self._last_hand_state else 'None'} -> {buffered_state.value} (buffer: {[s.value for s in self._fist_buffer]})")

        # Reset hand_was_lost flag when fist is detected
        if buffered_state == HandState.FIST:
            self._hand_was_lost = False

        # Update states
        self._last_hand_state = buffered_state
        self._confirmed_fist_state = buffered_state

        # Calibration is now handled directly in FrameProcessor on every fist detection
        return False  # No longer return recalibration flag

    def set_reset_calibration_callback(self, callback: Optional[Callable]) -> None:
        """Set callback function for resetting calibration."""
        self._reset_calibration_callback = callback
        self.logger.info(
            f"Reset calibration callback set: {callback is not None}")

    def set_debug_mode(self, enabled: bool) -> None:
        """Enable or disable debug mode."""
        self._debug_mode = enabled

    def reset_state(self) -> None:
        """Reset tracker state."""
        self._last_hand_state = HandState.NONE
        self._hand_was_lost = True
        self._fist_buffer.clear()
        self._confirmed_fist_state = HandState.OPEN
        self.logger.info("Hand state tracker reset")

    @property
    def last_hand_state(self) -> HandState:
        """Get last detected hand state."""
        return self._last_hand_state

    @property
    def hand_was_lost(self) -> bool:
        """Check if hand was lost."""
        return self._hand_was_lost
