"""
Shared gesture and pose detection pipeline used by both debug and game modes.
"""

import time
from typing import Optional, Dict, Any, List

from ..interfaces import IHandTracker, IGestureRecognizer, IGameController, ILogger
from ..config import ApplicationConfig
from ..config.performance_tuning_config import PerformanceTuningConfig
from ..config.debug_config import DebugConfig
from ..types import FrameAnalysis, GestureResult, GestureType, RotationVector, HandState
from ...utils.math_utils import quantize_landmarks


class GesturePipeline:
    """
    Analyzes camera frames and produces gesture results, control state, and debug info.

    This is the shared data source for both debug visualization and game integration.
    """

    def __init__(self, config: ApplicationConfig, logger: ILogger) -> None:
        self.config = config
        self.logger = logger

        self.performance_config = PerformanceTuningConfig()
        self.debug_config = DebugConfig()

        self.hand_tracker: Optional[IHandTracker] = None
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.game_controller: Optional[IGameController] = None

        self.frame_count = 0
        self.last_gesture: Optional[str] = None

    def set_components(
        self,
        hand_tracker: IHandTracker,
        gesture_recognizer: IGestureRecognizer,
        game_controller: Optional[IGameController] = None
    ) -> None:
        """Attach system components used for frame analysis."""
        self.hand_tracker = hand_tracker
        self.gesture_recognizer = gesture_recognizer
        self.game_controller = game_controller

    def analyze_frame(self) -> Optional[FrameAnalysis]:
        """
        Process a single frame from the camera and return analysis results.

        Returns:
            FrameAnalysis or None if frame processing failed
        """
        if not self.hand_tracker:
            self.logger.error("Hand tracker not set")
            return None
        if not self.gesture_recognizer:
            self.logger.error("Gesture recognizer not set")
            return None

        try:
            camera_frame = self.hand_tracker.read_frame()
            if camera_frame is None:
                return None

            self.frame_count += 1

            gesture_results: List[GestureResult] = self.gesture_recognizer.detect_gestures(
                camera_frame.landmarks,
                camera_frame.face_landmarks
            )

            if gesture_results and any(g.confidence > 0.5 for g in gesture_results):
                best_gesture = max(gesture_results, key=lambda g: g.confidence)
                self.last_gesture = getattr(best_gesture, "name", "Unknown")
                self.logger.debug(f"Gesture detected: {self.last_gesture}")

            self._handle_calibration(
                gesture_results,
                camera_frame.landmarks,
                camera_frame.face_landmarks
            )

            control_state = None
            if self.game_controller:
                control_state = self.game_controller.process_gestures(gesture_results)

            calibration_data = None
            if self.gesture_recognizer and hasattr(self.gesture_recognizer, "get_calibration_data"):
                calibration_data = self.gesture_recognizer.get_calibration_data()

            quantized_landmarks = (
                self._quantize_landmarks_for_debug(camera_frame.landmarks)
                if camera_frame.landmarks
                else None
            )

            debug_info = self._collect_debug_info(
                quantized_landmarks,
                camera_frame.face_landmarks,
                gesture_results,
                control_state,
                calibration_data
            )

            if control_state:
                control_state.debug_info = debug_info
                if control_state.rotation_vector is None and debug_info:
                    rotation_vector = debug_info.get("rotation_vector")
                    if rotation_vector:
                        control_state.rotation_vector = rotation_vector

            return FrameAnalysis(
                camera_frame=camera_frame,
                gesture_results=gesture_results,
                control_state=control_state,
                debug_info=debug_info
            )

        except Exception as e:
            self.logger.error(f"Frame analysis error: {e}")
            return None

    def _handle_calibration(self, gesture_results, landmarks, face_landmarks) -> None:
        """Handle activation-based calibration."""
        if not gesture_results or not landmarks or not self.gesture_recognizer:
            return

        activation_detected = any(
            result.gesture_type == GestureType.ACTIVATION and result.confidence > 0.5
            for result in gesture_results
        )

        if activation_detected and not self.gesture_recognizer.is_calibrated():
            if self.gesture_recognizer.calibrate(landmarks, face_landmarks):
                self.logger.info("[ACTIVATION] Calibration completed!")

    def _quantize_landmarks_for_debug(self, landmarks):
        """Quantize landmarks for debug display to reduce jittering."""
        position_step = self.debug_config.quantization.position_step
        return quantize_landmarks(landmarks, position_step)

    def _collect_debug_info(
        self,
        landmarks,
        face_landmarks,
        gesture_results,
        control_state,
        calibration_data
    ) -> Dict[str, Any]:
        """Collect comprehensive debug information."""
        debug_info: Dict[str, Any] = {}

        if landmarks and "WRIST" in landmarks:
            wrist = landmarks["WRIST"]
            debug_info["current_position"] = wrist

            if (calibration_data and
                getattr(calibration_data, "is_calibrated", False) and
                    getattr(calibration_data, "calibration_timestamp", None)):
                time_since_cal = time.time() - calibration_data.calibration_timestamp
                debug_info["calibration_time"] = time_since_cal

            rel_pos = None
            if calibration_data and getattr(calibration_data, "reference_position", None):
                for result in gesture_results or []:
                    if (hasattr(result, "data") and result.data and
                            isinstance(result.data, dict) and "displacement" in result.data):
                        d = result.data["displacement"]
                        rel_pos = (d[0], d[1], 0)
                        break

                if rel_pos is None:
                    ref_pos = calibration_data.reference_position
                    dx = wrist[0] - ref_pos[0]
                    dy = wrist[1] - ref_pos[1]
                    dz = wrist[2] - ref_pos[2]

                    max_distance = self.config.strategies.position.max_distance_from_calibration
                    current_distance = (dx * dx + dy * dy) ** 0.5

                    if current_distance > max_distance:
                        scale = max_distance / current_distance
                        dx *= scale
                        dy *= scale

                    rel_pos = (dx, dy, dz)

                debug_info["relative_position"] = rel_pos

            hand_state = "NONE"
            hand_confidence = 0.0

            if control_state and control_state.hand_state:
                hand_state = control_state.hand_state.value

            if gesture_results:
                for gesture in gesture_results:
                    if (hasattr(gesture, "data") and gesture.data and
                            isinstance(gesture.data, dict) and "hand_state" in gesture.data):
                        hand_state_value = gesture.data["hand_state"]
                        hand_state = (
                            hand_state_value.value
                            if hasattr(hand_state_value, "value")
                            else str(hand_state_value)
                        )
                        hand_confidence = getattr(gesture, "confidence", 0.0)
                        break

            debug_info["hand_state"] = hand_state
            debug_info["hand_confidence"] = hand_confidence

            special_actions = []
            if gesture_results:
                for gesture in gesture_results:
                    if (hasattr(gesture, "data") and gesture.data and
                            isinstance(gesture.data, dict) and "gesture_name" in gesture.data):
                        if gesture.data["gesture_name"] == "SHOOT":
                            special_actions.append("SHOOT")

            if control_state and control_state.hand_state == HandState.FIST:
                if "SHOOT" not in special_actions:
                    special_actions.append("SHOOT")

            debug_info["special_actions"] = special_actions
            debug_info["is_shooting"] = "SHOOT" in special_actions

        head_gestures = []
        head_strengths = {}
        head_config = self.config.strategies.head
        tilt_scale = max(head_config.tilt_threshold_deg * 3.0, 12.0)
        turn_scale = max(head_config.turn_threshold_ratio * 3.0, 0.18)
        nod_scale = max(head_config.nod_threshold_ratio * 3.0, 0.15)
        if gesture_results:
            for gesture in gesture_results:
                if hasattr(gesture, "gesture_type") and hasattr(gesture, "data") and gesture.data:
                    gtype = getattr(gesture.gesture_type, "name", str(gesture.gesture_type))
                    if gtype.startswith("HEAD"):
                        direction = gesture.data.get("direction", "")
                        if gtype == "HEAD_TILT":
                            raw = gesture.data.get("value", 0.0)
                            try:
                                raw = float(raw)
                            except Exception:
                                raw = 0.0
                            value = max(-1.0, min(1.0, raw / tilt_scale))
                            head_gestures.append(f"TILT {str(direction).upper()}")
                            head_strengths["head_tilt"] = {"direction": direction, "value": value, "debug": raw}
                        elif gtype == "HEAD_TURN":
                            raw = gesture.data.get("value", 0.0)
                            try:
                                raw = float(raw)
                            except Exception:
                                raw = 0.0
                            value = max(-1.0, min(1.0, raw / turn_scale))
                            head_gestures.append(f"TURN {str(direction).upper()}")
                            head_strengths["head_turn"] = {"direction": direction, "value": value, "debug": raw}
                        elif gtype == "HEAD_NOD":
                            raw = gesture.data.get("value", 0.0)
                            try:
                                raw = float(raw)
                            except Exception:
                                raw = 0.0
                            value = max(-1.0, min(1.0, raw / nod_scale))
                            head_gestures.append(f"NOD {str(direction).upper()}")
                            head_strengths["head_nod"] = {"direction": direction, "value": value, "debug": raw}

        debug_info["head"] = ", ".join(head_gestures)
        debug_info["head_strengths"] = head_strengths
        if self.gesture_recognizer and hasattr(self.gesture_recognizer, "get_head_neutral_status"):
            debug_info["head_neutral"] = self.gesture_recognizer.get_head_neutral_status(face_landmarks)

        rotation_vector = None
        if control_state and control_state.rotation_vector:
            rotation_vector = control_state.rotation_vector
        elif head_strengths:
            tilt = head_strengths.get("head_tilt", {}).get("value", 0.0)
            turn = head_strengths.get("head_turn", {}).get("value", 0.0)
            nod = head_strengths.get("head_nod", {}).get("value", 0.0)
            if abs(tilt) > 0 or abs(turn) > 0 or abs(nod) > 0:
                rotation_vector = RotationVector(tilt=tilt, turn=turn, nod=nod)

        debug_info["rotation_vector"] = rotation_vector

        if control_state and control_state.movement_vector:
            debug_info["movement_vector"] = control_state.movement_vector

        return debug_info
