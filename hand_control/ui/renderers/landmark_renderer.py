"""
Landmark rendering component for hand visualization.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional

from ...core.types import CalibrationData


class LandmarkRenderer:
    """
    Handles rendering of hand landmarks and connections.
    """
    
    def __init__(self, landmark_color: Tuple[int, int, int] = (0, 255, 255),
                 connection_color: Tuple[int, int, int] = (255, 0, 0)):
        """
        Initialize landmark renderer.
        
        Args:
            landmark_color: Color for landmark points in BGR format
            connection_color: Color for connections in BGR format
        """
        self.landmark_color = landmark_color
        self.connection_color = connection_color
        
        # Define hand connections
        self.hand_connections = [
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
    
    def draw_hand_landmarks(self, frame: np.ndarray, landmarks: Dict, 
                           out_of_range: bool = False) -> None:
        """
        Draw hand landmarks and connections.
        
        Args:
            frame: OpenCV frame to draw on
            landmarks: Dictionary of landmark positions
            out_of_range: Whether hand is beyond maximum distance from calibration
        """
        if not landmarks:
            return
        
        # Don't draw detailed landmarks if hand is out of range
        if out_of_range:
            return
        
        try:
            # Draw landmark points
            for landmark_name, (x, y, z) in landmarks.items():
                cv2.circle(
                    frame,
                    (int(x), int(y)),
                    5,
                    self.landmark_color,
                    -1
                )
            
            # Draw hand connections
            self._draw_hand_connections(frame, landmarks)
            
        except Exception:
            pass
    
    def _draw_hand_connections(self, frame: np.ndarray, landmarks: Dict) -> None:
        """
        Draw connections between hand landmarks.
        
        Args:
            frame: OpenCV frame to draw on
            landmarks: Dictionary of landmark positions
        """
        # Draw connections
        for start_landmark, end_landmark in self.hand_connections:
            if start_landmark in landmarks and end_landmark in landmarks:
                start_pos = landmarks[start_landmark]
                end_pos = landmarks[end_landmark]
                
                cv2.line(
                    frame,
                    (int(start_pos[0]), int(start_pos[1])),
                    (int(end_pos[0]), int(end_pos[1])),
                    self.connection_color,
                    2
                )
    
    def draw_calibration_visualization(self, frame: np.ndarray, landmarks: Dict,
                                     calibration: CalibrationData,
                                     text_renderer, max_distance: float = 300.0) -> None:
        """
        Draw calibration reference points and current position.
        
        Args:
            frame: OpenCV frame to draw on
            landmarks: Dictionary of landmark positions
            calibration: Calibration data with reference points
            text_renderer: Text renderer for distance labels
            max_distance: Maximum allowed distance from calibration point
        """
        # Always draw when landmarks available - show calibration point even if not calibrated
        # This helps user see where to position their hand for calibration
        
        if "WRIST" not in landmarks:
            return
        
        try:
            # Get current position
            current_wrist = landmarks["WRIST"]
            
            # If we have calibration reference, calculate and limit position
            if calibration.is_calibrated and calibration.reference_position:
                reference_pos = calibration.reference_position
                reference_screen = (int(reference_pos[0]), int(reference_pos[1]))
                
                # Calculate distance from reference
                dx = current_wrist[0] - reference_pos[0]
                dy = current_wrist[1] - reference_pos[1]
                distance = (dx*dx + dy*dy)**0.5
                
                # Limit position to maximum distance
                if distance > max_distance:
                    # Normalize direction vector and scale to max distance
                    scale = max_distance / distance
                    limited_x = reference_pos[0] + dx * scale
                    limited_y = reference_pos[1] + dy * scale
                    current_screen = (int(limited_x), int(limited_y))
                    
                    # Use different color to indicate clamped position
                    marker_color = (0, 165, 255)  # Orange
                else:
                    current_screen = (int(current_wrist[0]), int(current_wrist[1]))
                    marker_color = (0, 0, 255)  # Red
                
                # Draw current position with appropriate color
                cv2.circle(frame, current_screen, 8, marker_color, -1)    # Filled  
                cv2.circle(frame, current_screen, 12, marker_color, 2)    # Outline
                
                # Draw reference point (larger, green)
                cv2.circle(frame, reference_screen, 10, (0, 255, 0), -1)  # Green filled
                cv2.circle(frame, reference_screen, 15, (0, 255, 0), 3)   # Green outline
                
                # Draw max distance circle (faint white)
                cv2.circle(frame, reference_screen, int(max_distance), (100, 100, 100), 1)
                
                # Draw line connecting positions
                cv2.line(frame, reference_screen, current_screen, (0, 255, 255), 3)  # Cyan line
                
                # Draw distance text using clamped position
                actual_distance = ((current_wrist[0] - reference_pos[0])**2 + 
                                 (current_wrist[1] - reference_pos[1])**2)**0.5
                
                if actual_distance > max_distance:
                    distance_text = f"{max_distance:.0f}px (LIMIT)"
                else:
                    distance_text = f"{actual_distance:.0f}px"
                
                mid_point = (
                    (current_screen[0] + reference_screen[0]) // 2,
                    (current_screen[1] + reference_screen[1]) // 2 - 15
                )
                
                text_renderer.draw_text_with_outline(
                    frame, 
                    distance_text, 
                    mid_point, 
                    (255, 255, 255)
                )
            else:
                # Not calibrated yet - show current position and calibration prompt
                current_screen = (int(current_wrist[0]), int(current_wrist[1]))
                
                # Draw current position (red)
                cv2.circle(frame, current_screen, 8, (0, 0, 255), -1)    # Red filled  
                cv2.circle(frame, current_screen, 12, (0, 0, 255), 2)    # Red outline
                
                # Show calibration prompt
                text_renderer.draw_text_with_outline(
                    frame, 
                    "Make FIST to calibrate", 
                    (current_screen[0] + 20, current_screen[1] - 20), 
                    (255, 255, 0)  # Yellow text
                )
            
        except Exception:
            pass

    def draw_face_landmarks(self, frame: np.ndarray, face_landmarks) -> None:
        """
        Draw face landmarks as small points.
        
        Args:
            frame: OpenCV frame to draw on
            face_landmarks: List of (x, y, z) tuples from face mesh
        """
        if not face_landmarks:
            return
        
        try:
            for (x, y, z) in face_landmarks:
                cv2.circle(
                    frame,
                    (int(x), int(y)),
                    2,                   # smaller point than hand
                    (0, 255, 0),         # green
                    -1
                )
        except Exception:
            pass
