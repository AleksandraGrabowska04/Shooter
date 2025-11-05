"""
Frame processing component for the hand control system.
"""

import cv2
import math
from typing import Optional

from ..interfaces import IHandTracker, IGestureRecognizer, IVisualizationRenderer, ILogger
from ..config import ApplicationConfig
from ..config.performance_tuning_config import PerformanceTuningConfig
from ..config.debug_config import DebugConfig
from ..types import GestureType
from ...utils.math_utils import quantize_landmarks


class FrameProcessor:
    """
    Processes frames from the camera and handles gesture recognition.
    """
    
    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize frame processor.
        
        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        # Load performance and debug configs
        self.performance_config = PerformanceTuningConfig()
        self.debug_config = DebugConfig()
        self.logger = logger
        
        # Components (will be set externally)
        self.hand_tracker: Optional[IHandTracker] = None
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.renderer: Optional[IVisualizationRenderer] = None
        self.game_controller = None
        
        # State tracking
        self.frame_count = 0
        self.last_gesture = None
        self.last_fist_state = False  # Track if we were in fist state last frame
        
        # Shoot display state
        import time
        self.shoot_display_until = 0  # Timestamp until which to show shoot indicator
        self.shoot_display_duration = self.performance_config.frame_processor.shoot_display_timeout
        self.consecutive_shoots = 0  # Count consecutive shoots
        self.last_shoot_time = 0  # Time of last shoot
        self.shoot_combo_timeout = self.performance_config.frame_processor.debug_display_timeout
    
    def set_components(self, hand_tracker: IHandTracker, 
                      gesture_recognizer: IGestureRecognizer,
                      renderer: IVisualizationRenderer,
                      game_controller=None) -> None:
        """Set component references."""
        self.hand_tracker = hand_tracker
        self.gesture_recognizer = gesture_recognizer
        self.renderer = renderer
        self.game_controller = game_controller
        
    def process_frame(self) -> bool:
        """
        Process a single frame from the camera.
        
        Returns:
            True if processing should continue, False if should stop
        """
        try:
            if not self.hand_tracker:
                self.logger.error("Hand tracker not set")
                return False
            if not self.gesture_recognizer:
                self.logger.error("Gesture recognizer not set") 
                return False
            
            # Read frame from camera
            camera_frame = self.hand_tracker.read_frame()
            if camera_frame is None:
                return False
            
            self.frame_count += 1
            gesture_results = []
            control_state = None
            
            # Process gestures if landmarks available
            if camera_frame.landmarks:
                gesture_results = self.gesture_recognizer.detect_gestures(camera_frame.landmarks)
                
                # Track last gesture
                if gesture_results and any(g.confidence > 0.5 for g in gesture_results):
                    best_gesture = max(gesture_results, key=lambda g: g.confidence)
                    self.last_gesture = getattr(best_gesture, 'name', 'Unknown')
                    self.logger.debug(f"Gesture detected: {self.last_gesture}")
                
                # Smart calibration logic: calibrate only on transition to fist
                # Check if any gesture result indicates a fist
                current_fist_state = False
                for result in gesture_results:
                    if (hasattr(result, 'gesture_type') and 
                        result.gesture_type.name == 'HAND_STATE' and
                        hasattr(result, 'data') and
                        result.data and
                        result.data.get('hand_state') and
                        result.data['hand_state'].name == 'FIST'):
                        current_fist_state = True
                        break
                
                # Try to calibrate while fist is held (not just on transition)
                if current_fist_state and camera_frame.landmarks and not self.gesture_recognizer.is_calibrated():
                    if self.gesture_recognizer.calibrate(camera_frame.landmarks):
                        self.logger.info("[FIST] Calibration completed!")
                    # Don't show failure message every frame - only on transition
                    elif not self.last_fist_state:
                        self.logger.info("[FIST] Calibrating... (hold steady)")
                
                # Update state for next frame
                self.last_fist_state = current_fist_state
                
                # Process gestures with game controller if available
                if self.game_controller:
                    control_state = self.game_controller.process_gestures(gesture_results)
            
            # Render comprehensive frame with all visualization components
            if self.renderer:
                self._render_comprehensive_frame(camera_frame, gesture_results, control_state)
            
            # Display frame
            cv2.imshow("Hand Control", camera_frame.frame)
            
            # Debug: Log frame display at configured frequency
            debug_frequency = self.performance_config.frame_processor.debug_frame_frequency
            if self.frame_count % debug_frequency == 0:
                self.logger.debug(f"Displaying frame {self.frame_count}, window should be visible")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            return False
    
    def _render_comprehensive_frame(self, camera_frame, gesture_results, control_state):
        """Render all visual elements on the frame."""
        try:
            if not self.renderer:
                self.logger.warning("Renderer not available for frame rendering")
                return
                
            frame = camera_frame.frame
            landmarks = camera_frame.landmarks
            
            # Get calibration data
            calibration_data = None
            if self.gesture_recognizer and hasattr(self.gesture_recognizer, 'get_calibration_data'):
                calibration_data = self.gesture_recognizer.get_calibration_data()
            
            # 1. Render status message
            status_message = "No hand detected"
            if control_state and hasattr(control_state, 'status_message'):
                status_message = control_state.status_message
            elif gesture_results:
                status_message = f"Gestures detected: {len(gesture_results)}"
            
            self.renderer.render_status(frame, status_message)
            
            # 2. Render gesture visualization (landmarks, calibration)
            if calibration_data and landmarks:
                self.renderer.render_gesture_visualization(frame, landmarks, calibration_data)
            
            # 3. Render debug information if enabled
            if self.config.ui.show_debug_info and landmarks:
                quantized_landmarks = self._quantize_landmarks_for_debug(landmarks)
                debug_info = self._collect_debug_info(quantized_landmarks, gesture_results, control_state, calibration_data)
                self.renderer.render_debug_info(frame, debug_info)
            
            # 4. Render gesture bars if we have gesture data
            if self.config.enable_debug_mode and gesture_results:
                gesture_data = self._extract_gesture_data_from_results(gesture_results)
                self.renderer.render_gesture_bars(frame, gesture_data)
            
            # 5. Render shoot indication with display timeout
            import time
            current_time = time.time()
            
            # Check if new shoot detected
            if self._check_shooting_state(gesture_results):
                # Reset combo if too much time passed since last shoot
                if current_time - self.last_shoot_time > self.shoot_combo_timeout:
                    self.consecutive_shoots = 0
                
                # Increment shoot count
                self.consecutive_shoots += 1
                self.last_shoot_time = current_time
                self.shoot_display_until = current_time + self.shoot_display_duration
                
                # Log with combo count
                if self.consecutive_shoots == 1:
                    self.logger.info(f"[SHOOT] Detected - displaying for {self.shoot_display_duration:.1f}s")
                else:
                    self.logger.info(f"[SHOOT] x{self.consecutive_shoots} Combo! - displaying for {self.shoot_display_duration:.1f}s")
            
            # Show shoot indicator if still within display time
            if current_time < self.shoot_display_until:
                self.renderer.render_shoot_indication(frame, True)
                
        except Exception as e:
            self.logger.error(f"Rendering error: {e}")
    
    def _collect_debug_info(self, landmarks, gesture_results, control_state, calibration_data):
        """Collect comprehensive debug information."""
        import time
        
        debug_info = {}
        
        if landmarks and "WRIST" in landmarks:
            wrist = landmarks["WRIST"]
            debug_info['current_position'] = wrist
            
            # Calibration time info
            if (calibration_data and 
                hasattr(calibration_data, 'is_calibrated') and calibration_data.is_calibrated and 
                hasattr(calibration_data, 'calibration_timestamp') and calibration_data.calibration_timestamp):
                time_since_cal = time.time() - calibration_data.calibration_timestamp
                debug_info['calibration_time'] = time_since_cal
            
            # Relative position from calibration (use data from position gesture results if available)
            if (calibration_data and 
                hasattr(calibration_data, 'reference_position') and calibration_data.reference_position):
                
                # Try to get quantized displacement from gesture results first
                rel_pos = None
                for result in gesture_results or []:
                    if (hasattr(result, 'data') and result.data and 
                        isinstance(result.data, dict) and 'displacement' in result.data):
                        rel_pos = result.data['displacement'] + (0,)  # Add Z component
                        break
                
                # Fallback to manual calculation if not found
                if rel_pos is None:
                    ref_pos = calibration_data.reference_position
                    dx = wrist[0] - ref_pos[0]
                    dy = wrist[1] - ref_pos[1]
                    dz = wrist[2] - ref_pos[2]
                    
                    # Limit relative position to maximum distance (from config)
                    max_distance = self.config.strategies.position.max_distance_from_calibration
                    current_distance = (dx*dx + dy*dy)**0.5  # 2D distance for consistency
                    
                    if current_distance > max_distance:
                        scale = max_distance / current_distance
                        dx *= scale
                        dy *= scale
                    
                    rel_pos = (dx, dy, dz)
                
                debug_info['relative_position'] = rel_pos
            
            # Hand state from gestures
            hand_state = "NONE"
            hand_confidence = 0.0
            
            if gesture_results:
                for gesture in gesture_results:
                    if (hasattr(gesture, 'data') and gesture.data and 
                        isinstance(gesture.data, dict) and 'hand_state' in gesture.data):
                        hand_state_value = gesture.data['hand_state']
                        hand_state = (hand_state_value.value if hasattr(hand_state_value, 'value') 
                                    else str(hand_state_value))
                        hand_confidence = getattr(gesture, 'confidence', 0.0)
                        break
            
            debug_info['hand_state'] = hand_state
            debug_info['hand_confidence'] = hand_confidence
            
            # Extract gesture information
            position_gesture = "CENTER"
            orientation_gestures = []
            motion_gesture = "STATIC"
            special_actions = []
            
            if control_state:
                if hasattr(control_state, 'position_gesture') and control_state.position_gesture:
                    pos_gesture = control_state.position_gesture
                    position_gesture = (pos_gesture.value if hasattr(pos_gesture, 'value') 
                                      else str(pos_gesture))
                if hasattr(control_state, 'orientation_gesture') and control_state.orientation_gesture:
                    ori_gesture = control_state.orientation_gesture
                    orientation_gestures = [ori_gesture.value if hasattr(ori_gesture, 'value') 
                                          else str(ori_gesture)]
                if hasattr(control_state, 'motion_gesture') and control_state.motion_gesture:
                    mot_gesture = control_state.motion_gesture
                    motion_gesture = (mot_gesture.value if hasattr(mot_gesture, 'value') 
                                    else str(mot_gesture))
            
            # Check for special actions in gesture results
            if gesture_results:
                for gesture in gesture_results:
                    if (hasattr(gesture, 'data') and gesture.data and 
                        isinstance(gesture.data, dict) and 'gesture_name' in gesture.data):
                        if gesture.data['gesture_name'] == 'SHOOT':
                            # Check for consecutive shots data
                            consecutive_shots = gesture.data.get('consecutive_shots', 1)
                            if consecutive_shots > 1:
                                shoot_text = f'SHOOT x{consecutive_shots}'
                                self.logger.info(f"[SEQUENCE] {shoot_text} - Sequential shots detected!")
                            else:
                                self.logger.info("[SHOOT] Single shot detected!")
                            special_actions.append('SHOOT')
            
            debug_info['position_gesture'] = position_gesture
            debug_info['orientation_gestures'] = orientation_gestures
            debug_info['motion_gesture'] = motion_gesture
            debug_info['special_actions'] = special_actions
            debug_info['is_shooting'] = 'SHOOT' in special_actions
            
            # Add consecutive shoots info for debug display
            import time
            current_time = time.time()
            if (self.consecutive_shoots > 0 and 
                current_time - self.last_shoot_time < self.shoot_combo_timeout):
                debug_info['shoot_combo'] = self.consecutive_shoots
            else:
                debug_info['shoot_combo'] = 0
            
            # Extract angle data for debug display from existing gesture results
            gesture_data = self._extract_gesture_data_from_results(gesture_results)
            debug_info['thumb_angle_rad'] = gesture_data.get('thumb_angle_rad', 0.0)
            debug_info['roll_angle_rad'] = gesture_data.get('roll_angle_rad', 0.0)
            
        return debug_info
    
    def _extract_gesture_data_from_results(self, gesture_results):
        """Extract gesture data from existing gesture results for visualization bars."""
        gesture_data = {
            'thumb_angle_rad': 0.0,
            'roll_angle_rad': 0.0
        }
        
        try:
            # Extract orientation data from results (no need to re-detect gestures)
            if gesture_results:
                for result in gesture_results:
                    if result.gesture_type == GestureType.ORIENTATION and result.data:
                        # Get roll angle from orientation data (already quantized in recognizer)
                        if 'roll_angle' in result.data:
                            gesture_data['roll_angle_rad'] = result.data['roll_angle']
                        
                        # Calculate thumb angle based on thumb state (normalize to ±1.0 for bar display)
                        thumb_state = result.data.get('thumb_state')
                        if thumb_state:
                            if hasattr(thumb_state, 'value'):
                                thumb_val = thumb_state.value
                            else:
                                thumb_val = str(thumb_state)
                            
                            # Convert enum values to string for comparison
                            thumb_str = str(thumb_val).upper()
                            
                            if 'THUMB_UP' in thumb_str or 'UP' in thumb_str:
                                gesture_data['thumb_angle_rad'] = 0.8  # Positive for up (80% of max)
                            elif 'THUMB_DOWN' in thumb_str or 'DOWN' in thumb_str:
                                gesture_data['thumb_angle_rad'] = -0.8  # Negative for down (80% of max)
                            else:
                                gesture_data['thumb_angle_rad'] = 0.0  # Neutral
                        
                        # Limit roll angle for bar display (±1.0 range)
                        if 'roll_angle_rad' in gesture_data:
                            max_roll = math.pi / 6  # 30 degrees
                            current_roll = gesture_data['roll_angle_rad']
                            # Normalize to ±1.0 range for bar display
                            gesture_data['roll_angle_rad'] = max(-1.0, min(1.0, current_roll / max_roll))
        except Exception:
            # If error occurs, return default values
            pass
        
        return gesture_data
    
    def _quantize_landmarks_for_debug(self, landmarks):
        """Quantize landmarks for debug display to reduce jittering."""
        position_step = self.debug_config.quantization.position_step
        return quantize_landmarks(landmarks, position_step)
    
    def _check_shooting_state(self, gesture_results):
        """Check if shooting gesture is active."""
        if not gesture_results:
            return False
            
        for gesture in gesture_results:
            if (hasattr(gesture, 'data') and gesture.data and 
                isinstance(gesture.data, dict) and 'gesture_name' in gesture.data and 
                gesture.data['gesture_name'] == 'SHOOT'):
                return True
        return False
    
    def check_exit_condition(self) -> bool:
        """
        Check if user wants to exit based on key press.
        
        Returns:
            True if exit condition met
        """
        key = cv2.waitKey(1) & 0xFF
        if key == self.config.exit_key or key == 27:  # ESC key
            self.logger.info("ESC pressed - exiting")
            return True
        return False