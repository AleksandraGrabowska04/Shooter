"""
MediaPipe-based hand tracker implementation.
"""

import cv2
import numpy as np
import time
from typing import Optional, Dict, Tuple

try:
    import mediapipe as mp
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False
    mp = None

from ..core.interfaces import IHandTracker
from ..core.config import ApplicationConfig
from ..core.types import CameraFrame


# MediaPipe landmark names mapping
LANDMARK_NAMES = [
    "WRIST", "THUMB_CMC", "THUMB_MCP", "THUMB_IP", "THUMB_TIP",
    "INDEX_FINGER_MCP", "INDEX_FINGER_PIP", "INDEX_FINGER_DIP", "INDEX_FINGER_TIP",
    "MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP",
    "RING_FINGER_MCP", "RING_FINGER_PIP", "RING_FINGER_DIP", "RING_FINGER_TIP",
    "PINKY_MCP", "PINKY_PIP", "PINKY_DIP", "PINKY_TIP"
]


class MediaPipeHandTracker(IHandTracker):
    """
    This class provides computer vision hand tracking using Google's MediaPipe library.
    """
    
    def __init__(self, config: ApplicationConfig):
        """
        Initialize MediaPipe hand tracker.
        
        Args:
            config: Application configuration containing camera and gesture settings
            
        Raises:
            Exception: If camera cannot be opened
        """
        self._config = config
        self._cap: Optional[cv2.VideoCapture] = None
        self._is_available = False
        
        # Check MediaPipe availability
        if not MP_AVAILABLE or mp is None:
            raise Exception("MediaPipe is not available. Please install: pip install mediapipe")
        
        # Initialize MediaPipe
        try:
            self.mp_hands = mp.solutions.hands  # type: ignore
            self.mp_draw = mp.solutions.drawing_utils  # type: ignore
            
            # Create MediaPipe hands processor
            self.hands = self.mp_hands.Hands(
                max_num_hands=1,  # Track single hand for better performance
                min_detection_confidence=config.gestures.min_detection_confidence,
                min_tracking_confidence=config.gestures.min_tracking_confidence
            )
            # Initialize MediaPipe FaceMesh (head landmark model)
            self.mp_face = mp.solutions.face_mesh
            self.face_mesh = self.mp_face.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

        except Exception as e:
            raise Exception(f"Failed to initialize MediaPipe: {e}")
        
        # Initialize camera
        self._initialize_camera()
    
    def _initialize_camera(self) -> None:
        """Initialize camera with configuration settings."""
        try:
            self._cap = cv2.VideoCapture(self._config.camera.camera_index)
            
            if not self._cap.isOpened():
                raise Exception(f"Cannot open camera {self._config.camera.camera_index}")

            # Configure camera settings
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._config.camera.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._config.camera.height)
            self._cap.set(cv2.CAP_PROP_FPS, self._config.camera.fps)
            
            self._is_available = True
            
        except Exception as e:
            self._is_available = False
            raise Exception(f"Failed to initialize camera: {e}")
    
    def read_frame(self) -> Optional[CameraFrame]:
        """
        Read and process a frame from the camera.
        
        Returns:
            CameraFrame with image and landmarks, or None if failed
        """
        if not self._is_available or not self._cap:
            return None
        
        try:
            # Read frame from camera
            success, frame = self._cap.read()
            if not success or frame is None:
                return None
            
            # Flip frame horizontally for natural mirrored control
            if self._config.camera.flip_horizontal:
                frame = cv2.flip(frame, 1)
            
            # Process frame for hand landmarks
            hand_landmarks = self._extract_landmarks(frame)

            # Process face landmarks
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_results = self.face_mesh.process(rgb_frame)
            
            face_landmarks = None
            if face_results.multi_face_landmarks:
                face = face_results.multi_face_landmarks[0]
                h, w = frame.shape[:2]
                face_landmarks = [(lm.x * w, lm.y * h, lm.z) for lm in face.landmark]

            return CameraFrame(
                frame=frame,
                landmarks=hand_landmarks,
                face_landmarks=face_landmarks,  
                timestamp=time.time()
            )
            
        except Exception as e:
            # Log error but don't crash - return None to indicate failure
            return None
    
    def _extract_landmarks(self, frame: np.ndarray) -> Optional[Dict[str, Tuple[float, float, float]]]:
        """
        Extract hand landmarks from frame using MediaPipe.
        
        Args:
            frame: Input frame from camera
            
        Returns:
            Dictionary mapping landmark names to (x, y, z) coordinates, or None
        """
        try:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process frame with MediaPipe
            result = self.hands.process(rgb_frame)
            
            if not result.multi_hand_landmarks:
                return None
            
            # Take first detected hand
            hand_landmarks = result.multi_hand_landmarks[0]
            
            # Convert landmarks to dictionary with named keys
            h, w = frame.shape[:2]
            landmarks = {}
            
            for i, landmark_name in enumerate(LANDMARK_NAMES):
                if i < len(hand_landmarks.landmark):
                    lm = hand_landmarks.landmark[i]
                    landmarks[landmark_name] = (
                        lm.x * w,  # Convert normalized x to pixel coordinates
                        lm.y * h,  # Convert normalized y to pixel coordinates
                        lm.z       # Keep z as relative depth
                    )
            
            return landmarks
            
        except Exception as e:
            # Return None on any processing error
            return None
    
    def is_available(self) -> bool:
        """
        Check if camera is available and working.
        
        Returns:
            True if camera is available
        """
        return self._is_available and self._cap is not None and self._cap.isOpened()
    
    def release(self) -> None:
        """Release camera resources and cleanup."""
        if self._cap:
            self._cap.release()
            self._cap = None
        
        self._is_available = False
    
    def _draw_hand_connections(self, frame: np.ndarray, landmarks: Dict[str, Tuple[float, float, float]]) -> None:
        """Draw connections between hand landmarks."""
        # Define hand connections (simplified version)
        connections = [
            # Thumb
            ("WRIST", "THUMB_CMC"),
            ("THUMB_CMC", "THUMB_MCP"),
            ("THUMB_MCP", "THUMB_IP"),
            ("THUMB_IP", "THUMB_TIP"),
            
            # Index finger
            ("WRIST", "INDEX_FINGER_MCP"),
            ("INDEX_FINGER_MCP", "INDEX_FINGER_PIP"),
            ("INDEX_FINGER_PIP", "INDEX_FINGER_DIP"),
            ("INDEX_FINGER_DIP", "INDEX_FINGER_TIP"),
            
            # Middle finger
            ("WRIST", "MIDDLE_FINGER_MCP"),
            ("MIDDLE_FINGER_MCP", "MIDDLE_FINGER_PIP"),
            ("MIDDLE_FINGER_PIP", "MIDDLE_FINGER_DIP"),
            ("MIDDLE_FINGER_DIP", "MIDDLE_FINGER_TIP"),
            
            # Ring finger
            ("WRIST", "RING_FINGER_MCP"),
            ("RING_FINGER_MCP", "RING_FINGER_PIP"),
            ("RING_FINGER_PIP", "RING_FINGER_DIP"),
            ("RING_FINGER_DIP", "RING_FINGER_TIP"),
            
            # Pinky
            ("WRIST", "PINKY_MCP"),
            ("PINKY_MCP", "PINKY_PIP"),
            ("PINKY_PIP", "PINKY_DIP"),
            ("PINKY_DIP", "PINKY_TIP"),
        ]
        
        for start_landmark, end_landmark in connections:
            if start_landmark in landmarks and end_landmark in landmarks:
                start_pos = landmarks[start_landmark]
                end_pos = landmarks[end_landmark]
                
                cv2.line(
                    frame,
                    (int(start_pos[0]), int(start_pos[1])),
                    (int(end_pos[0]), int(end_pos[1])),
                    self._config.ui.connection_color,
                    2
                )
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()