"""
Temporary stub implementations for testing.
These will be replaced by actual implementations in future iterations.
"""

from typing import Optional, List, Any
import cv2
from ..core.interfaces import IHandTracker, IGestureRecognizer, IGameController, IVisualizationRenderer
from ..core.config import ApplicationConfig
from ..core.types import (
    CameraFrame, GestureResult, ControlState, CalibrationData, 
    GestureType, HandState, PositionGesture, OrientationGesture, MotionGesture
)


class StubHandTracker(IHandTracker):
    """Stub hand tracker for testing"""
    
    def __init__(self, config: ApplicationConfig):
        self._config = config
        self._cap = None
        self._is_available = False
        
    def read_frame(self) -> Optional[CameraFrame]:
        if self._cap is None:
            self._cap = cv2.VideoCapture(self._config.camera.camera_index)
            self._is_available = self._cap.isOpened()
            
        if not self._is_available:
            return None
            
        ret, frame = self._cap.read()
        if not ret:
            return None
            
        if self._config.camera.flip_horizontal:
            frame = cv2.flip(frame, 1)
            
        # Stub landmarks (center of frame)
        h, w = frame.shape[:2]
        stub_landmarks = {
            "landmark_0": (w//2, h//2, 0.0)  # Center point
        }
        
        return CameraFrame(frame=frame, landmarks=stub_landmarks)
    
    def is_available(self) -> bool:
        return self._is_available
    
    def release(self) -> None:
        if self._cap:
            self._cap.release()


class StubGestureRecognizer(IGestureRecognizer):
    """Stub gesture recognizer for testing"""
    
    def __init__(self, config: ApplicationConfig):
        self._config = config
        self._is_calibrated = False
        
    def detect_gestures(self, landmarks: Optional[dict]) -> List[GestureResult]:
        if not landmarks:
            return []
        return [GestureResult(GestureType.HAND_STATE, confidence=0.8)]
    
    def calibrate(self, landmarks: dict) -> bool:
        self._is_calibrated = True
        return True
    
    def is_calibrated(self) -> bool:
        return self._is_calibrated
    
    def reset_calibration(self) -> None:
        self._is_calibrated = False
    
    def get_calibration_data(self) -> CalibrationData:
        return CalibrationData(is_calibrated=self._is_calibrated)


class StubGameController(IGameController):
    """Stub game controller for testing"""
    
    def __init__(self, config: ApplicationConfig, logger):
        self._config = config
        self._logger = logger
        self._debug_mode = False
        self._active = True
        
    def process_gestures(self, gesture_results: List[GestureResult]) -> ControlState:
        primary_gesture = gesture_results[0] if gesture_results else None
        return ControlState(
            is_active=len(gesture_results) > 0,
            is_calibrated=True,
            status_message="Ready",
            hand_state=HandState.OPEN if gesture_results else HandState.NONE,
            position_gesture=PositionGesture.CENTER,
            orientation_gesture=OrientationGesture.NEUTRAL,
            motion_gesture=MotionGesture.STATIC,
            primary_gesture=primary_gesture,
            all_gestures=gesture_results
        )
    
    def set_debug_mode(self, enabled: bool) -> None:
        self._debug_mode = enabled
    
    def is_active(self) -> bool:
        return self._active
    
    def set_reset_calibration_callback(self, callback) -> None:
        """Set callback for resetting calibration"""
        pass  # Stub implementation - no action needed


class StubVisualizationRenderer(IVisualizationRenderer):
    """Stub visualization renderer for testing"""
    
    def __init__(self, config: ApplicationConfig):
        self._config = config
        
    def render_status(self, frame: Any, status_message: str) -> None:
        cv2.putText(
            frame, status_message, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 
            self._config.ui.font_scale,
            self._config.ui.text_color,
            self._config.ui.text_thickness
        )
    
    def render_debug_info(self, frame: Any, debug_info: dict) -> None:
        y_offset = 60
        for key, value in debug_info.items():
            text = f"{key}: {value}"
            cv2.putText(
                frame, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, self._config.ui.debug_color, 1
            )
            y_offset += 20
    
    def render_gesture_visualization(self, frame: Any, landmarks: Optional[dict], 
                                   calibration: CalibrationData) -> None:
        if landmarks:
            for name, (x, y, z) in landmarks.items():
                cv2.circle(frame, (int(x), int(y)), 5, self._config.ui.landmark_color, -1)