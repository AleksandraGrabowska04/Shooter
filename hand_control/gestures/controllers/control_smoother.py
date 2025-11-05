"""
Control state smoother for reducing jitter in control commands.
"""

import time
from typing import List, Dict, Any

from ...core.interfaces import ILogger
from ...core.config.performance_tuning_config import PerformanceTuningConfig
from ...core.types import ControlState


class ControlStateSmoother:
    """
    Applies smoothing to control state to reduce jitter and improve stability.
    """
    
    def __init__(self, logger: ILogger, history_size: int = 5):
        """
        Initialize control state smoother.
        
        Args:
            logger: Logger instance for debugging
            history_size: Number of states to keep in history for smoothing
        """
        self.logger = logger
        self._history_size = history_size
        self._control_history: List[ControlState] = []
        self._last_gesture_time = 0.0
        # Load performance config
        performance_config = PerformanceTuningConfig()
        self._gesture_cooldown = performance_config.control_smoothing.gesture_cooldown
    
    def apply_smoothing(self, control_state: ControlState) -> ControlState:
        """
        Apply smoothing to control state to reduce jitter.
        
        Args:
            control_state: Current control state
            
        Returns:
            Smoothed control state
        """
        current_time = time.time()
        
        # Apply gesture cooldown to prevent rapid state changes
        if (current_time - self._last_gesture_time) < self._gesture_cooldown:
            # Return previous state if too soon
            if self._control_history:
                return self._control_history[-1]
        
        # Add current state to history
        self._control_history.append(control_state)
        if len(self._control_history) > self._history_size:
            self._control_history.pop(0)
        
        # Update timing
        self._last_gesture_time = current_time
        
        # For now, return current state (advanced smoothing can be added later)
        return control_state
    
    def reset_state(self) -> None:
        """Reset smoother state and history."""
        self._control_history.clear()
        self._last_gesture_time = 0.0
        self.logger.info("Control state smoother reset")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for monitoring.
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'last_update_time': self._last_gesture_time,
            'history_size': len(self._control_history),
            'gesture_cooldown': self._gesture_cooldown
        }
    
    