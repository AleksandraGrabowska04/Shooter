"""
Frame processing component for the hand control system.
"""

import cv2
from typing import Optional
import time

from ..interfaces import IHandTracker, IGestureRecognizer, IVisualizationRenderer, ILogger
from ..config import ApplicationConfig
from ..config.performance_tuning_config import PerformanceTuningConfig
from ..config.debug_config import DebugConfig
from ...utils.math_utils import quantize_landmarks


class FrameProcessor:
    """
    Processes frames from the camera and handles gesture recognition.
    Orchestrates the flow: Capture -> Recognize -> Control -> Render.
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
        self.shoot_display_until = 0  # Timestamp until which to show shoot indicator
        self.shoot_display_duration = self.performance_config.frame_processor.shoot_display_timeout
        self.consecutive_shoots = 0   # Count consecutive shoots
        self.last_shoot_time = 0      # Time of last shoot
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

        # Set recalibrate callback for ON state if supported
        if self.game_controller and hasattr(self.game_controller, 'set_recalibrate_callback'):
            def recalibrate():
                # Try to recalibrate using current landmarks if available
                if self.hand_tracker and hasattr(self.hand_tracker, 'get_last_landmarks'):
                    landmarks = self.hand_tracker.get_last_landmarks()
                else:
                    landmarks = None
                if self.gesture_recognizer and hasattr(self.gesture_recognizer, 'calibrate') and landmarks:
                    if self.gesture_recognizer.calibrate(landmarks):
                        self.logger.info("[TOGGLE] Calibration completed (ON)")
            self.game_controller.set_recalibrate_callback(recalibrate)

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
                gesture_results = self.gesture_recognizer.detect_gestures(
                    camera_frame.landmarks)

            # Head gesture detection (Dynamic check for capabilities)
            if camera_frame.face_landmarks and hasattr(self.gesture_recognizer, 'head_detector'):
                calibration = self.gesture_recognizer.get_calibration_data() if hasattr(
                    self.gesture_recognizer, 'get_calibration_data') else None

                head_detector = getattr(
                    self.gesture_recognizer, 'head_detector', None)
                if head_detector and hasattr(head_detector, 'detect'):
                    # Convert list to dict with standard FaceMesh keys
                    facemesh_keys = [
                        "NOSE", "LEFT_EYE", "RIGHT_EYE", "LEFT_EAR", "RIGHT_EAR"
                    ]
                    # Indices for these points in Mediapipe FaceMesh (468 points)
                    # These are approximate, for demo purposes:
                    facemesh_indices = {
                        "NOSE": 1,         # Tip of nose
                        "LEFT_EYE": 33,    # Left eye outer
                        "RIGHT_EYE": 263,  # Right eye outer
                        "LEFT_EAR": 234,   # Left ear tragus
                        "RIGHT_EAR": 454   # Right ear tragus
                    }
                    face_landmarks_dict = {}
                    if isinstance(camera_frame.face_landmarks, list) and len(camera_frame.face_landmarks) >= 455:
                        for k, idx in facemesh_indices.items():
                            face_landmarks_dict[k] = camera_frame.face_landmarks[idx]
                    else:
                        face_landmarks_dict = {}  # Not enough points, skip
                    head_gestures = head_detector.detect(
                        face_landmarks_dict, calibration)
                    gesture_results.extend(head_gestures)

            # --- ADAPTED: Specific logging for Head Gestures (Tilt/Turn/Nod) ---
            for g in gesture_results:
                g_type_name = getattr(g.gesture_type, "name", str(
                    g.gesture_type)) if hasattr(g, "gesture_type") else ""

                # Check for HEAD prefix (covers HEAD_TILT, HEAD_TURN, HEAD_NOD)
                if g_type_name.startswith("HEAD"):
                    data_info = ""
                    if hasattr(g, 'data') and g.data:
                        # Extract relevant fields from our new Strategy format
                        direction = g.data.get('direction', '')
                        # Try to find a numeric value to show intensity
                        val = g.data.get('angle', g.data.get(
                            'ratio', g.data.get('offset', '')))

                        if isinstance(val, (int, float)):
                            data_info = f"{direction} ({val:.2f})"
                        else:
                            data_info = f"{direction}"

                    self.logger.info(f"[{g_type_name}] {data_info}")

            # --- ADAPTED: Check for Activation Gesture (Rotation) ---
            for g in gesture_results:
                g_type_name = getattr(g.gesture_type, "name", str(
                    g.gesture_type)) if hasattr(g, "gesture_type") else ""
                if g_type_name == "ACTIVATION":
                    self.logger.info("[ACTIVATION] Hand Rotation Detected!")
                    # Optional: You could trigger calibration here if desired
                    # if not self.gesture_recognizer.is_calibrated():
                    #     self.gesture_recognizer.calibrate(camera_frame.landmarks)

            # Track last gesture (for debug/UI)
            if gesture_results and any(g.confidence > 0.5 for g in gesture_results):
                best_gesture = max(
                    gesture_results, key=lambda g: g.confidence)
                self.last_gesture = getattr(
                    best_gesture, 'name', 'Unknown')
                # Log general gestures (debug level to avoid spam)
                self.logger.debug(f"Gesture detected: {self.last_gesture}")

            # Calibration logic: calibrate only on activation gesture
            activation_detected = False
            for result in gesture_results:
                if (hasattr(result, 'gesture_type') and
                    result.gesture_type.name == 'ACTIVATION' and
                        result.confidence > 0.5):
                    activation_detected = True
                    break

            if activation_detected and camera_frame.landmarks and not self.gesture_recognizer.is_calibrated():
                if self.gesture_recognizer.calibrate(camera_frame.landmarks):
                    self.logger.info("[ACTIVATION] Calibration completed!")

            # Process gestures with game controller if available
            if self.game_controller:
                control_state = self.game_controller.process_gestures(
                    gesture_results)

            # Render comprehensive frame with all visualization components
            if self.renderer:
                self._render_comprehensive_frame(
                    camera_frame, gesture_results, control_state)

            # Display frame
            cv2.imshow("Hand Control", camera_frame.frame)

            # Debug: Log frame display at configured frequency
            debug_frequency = self.performance_config.frame_processor.debug_frame_frequency
            if self.frame_count % debug_frequency == 0:
                self.logger.debug(
                    f"Displaying frame {self.frame_count}, window should be visible")

            return True

        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            return False

    def _render_comprehensive_frame(self, camera_frame, gesture_results, control_state):
        """Render all visual elements on the frame."""
        try:
            if not self.renderer:
                self.logger.warning(
                    "Renderer not available for frame rendering")
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
                # Show active gesture count or name
                status_message = f"Gestures: {len(gesture_results)}"

            self.renderer.render_status(frame, status_message)

            # 2. Render gesture visualization (landmarks, calibration)
            if calibration_data and landmarks:
                self.renderer.render_gesture_visualization(
                    frame, landmarks, calibration_data)

            # Draw face landmarks if available
            if camera_frame.face_landmarks and self.config.ui.show_landmarks:
                landmark_renderer = getattr(
                    self.renderer, 'landmark_renderer', None)
                if landmark_renderer and hasattr(landmark_renderer, 'draw_face_landmarks'):
                    try:
                        landmark_renderer.draw_face_landmarks(
                            frame,
                            camera_frame.face_landmarks
                        )
                    except Exception:
                        pass

            # 3. Render debug information if enabled
            if self.config.ui.show_debug_info and landmarks:
                quantized_landmarks = self._quantize_landmarks_for_debug(
                    landmarks)
                debug_info = self._collect_debug_info(
                    quantized_landmarks, gesture_results, control_state, calibration_data)
                self.renderer.render_debug_info(frame, debug_info)

            # 5. Render shoot indication with display timeout
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
                    self.logger.info(
                        f"[SHOOT] Detected - displaying for {self.shoot_display_duration:.1f}s")
                else:
                    self.logger.info(
                        f"[SHOOT] x{self.consecutive_shoots} Combo! - displaying for {self.shoot_display_duration:.1f}s")

            # Show shoot indicator if still within display time
            if current_time < self.shoot_display_until:
                self.renderer.render_shoot_indication(frame, True)

        except Exception as e:
            self.logger.error(f"Rendering error: {e}")

    def _collect_debug_info(self, landmarks, gesture_results, control_state, calibration_data):
        """Collect comprehensive debug information."""
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

            # Relative position: Prioritize Strategy Result (Correctly Clamped)
            rel_pos = None
            if (calibration_data and
                    hasattr(calibration_data, 'reference_position') and calibration_data.reference_position):

                # 1. Try to get displacement from PositionStrategy result
                # This is preferred because it handles deadzones and specific clamping
                for result in gesture_results or []:
                    if (hasattr(result, 'data') and result.data and
                            isinstance(result.data, dict) and 'displacement' in result.data):
                        # Add Z component (0) to match 3D format of debug info
                        d = result.data['displacement']
                        rel_pos = (d[0], d[1], 0)
                        break

                # 2. Fallback to manual calculation if strategy didn't return data (e.g. uncalibrated)
                if rel_pos is None:
                    ref_pos = calibration_data.reference_position
                    dx = wrist[0] - ref_pos[0]
                    dy = wrist[1] - ref_pos[1]
                    dz = wrist[2] - ref_pos[2]

                    # Manual clamping fallback
                    max_distance = self.config.strategies.position.max_distance_from_calibration
                    current_distance = (dx*dx + dy*dy)**0.5

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

            # Check for special actions
            special_actions = []
            if gesture_results:
                for gesture in gesture_results:
                    if (hasattr(gesture, 'data') and gesture.data and
                            isinstance(gesture.data, dict) and 'gesture_name' in gesture.data):
                        if gesture.data['gesture_name'] == 'SHOOT':
                            special_actions.append('SHOOT')

            debug_info['special_actions'] = special_actions
            debug_info['is_shooting'] = 'SHOOT' in special_actions

            # Shoot combo info
            current_time = time.time()
            if (self.consecutive_shoots > 0 and
                    current_time - self.last_shoot_time < self.shoot_combo_timeout):
                debug_info['shoot_combo'] = self.consecutive_shoots
            else:
                debug_info['shoot_combo'] = 0

        # Head gestures summary (for UI)
        head_gestures = []
        head_strengths = {}
        if gesture_results:
            for gesture in gesture_results:
                if hasattr(gesture, 'gesture_type') and hasattr(gesture, 'data') and gesture.data:
                    gtype = getattr(gesture.gesture_type, 'name', str(gesture.gesture_type))
                    if gtype.startswith('HEAD'):
                        direction = gesture.data.get('direction', '')
                        value = gesture.data.get('angle', gesture.data.get('ratio', gesture.data.get('offset', 0.0)))
                        # value можа быць None, таму гарантуем float
                        try:
                            value = float(value)
                        except Exception:
                            value = 0.0
                        if gtype == 'HEAD_TILT':
                            head_gestures.append(f"TILT {str(direction).upper()}")
                            head_strengths['head_tilt'] = {'direction': direction, 'value': value}
                        elif gtype == 'HEAD_TURN':
                            head_gestures.append(f"TURN {str(direction).upper()}")
                            head_strengths['head_turn'] = {'direction': direction, 'value': value}
                        elif gtype == 'HEAD_NOD':
                            head_gestures.append(f"NOD {str(direction).upper()}")
                            head_strengths['head_nod'] = {'direction': direction, 'value': value}
        if head_gestures:
            debug_info['head'] = ', '.join(head_gestures)
        if head_strengths:
            debug_info['head_strengths'] = head_strengths

        return debug_info

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
