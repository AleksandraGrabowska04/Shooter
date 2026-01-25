"""
Frame processing component for the gesture control system.
"""

import cv2
from typing import Optional
import time

from ..interfaces import IHandTracker, IGestureRecognizer, IVisualizationRenderer, ILogger
from ..config import ApplicationConfig
from ..config.performance_tuning_config import PerformanceTuningConfig
from ..types import FrameAnalysis
from .gesture_pipeline import GesturePipeline


class FrameProcessor:
    """
    Processes frames from the camera and handles gesture recognition.
    Orchestrates the flow: Capture -> Recognize -> Control -> Render.
    Uses the shared GesturePipeline to keep analysis consistent across modes.
    """

    def __init__(self, config: ApplicationConfig, logger: ILogger):
        """
        Initialize frame processor.

        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config

        # Load performance config
        self.performance_config = PerformanceTuningConfig()

        self.logger = logger

        # Components (set externally)
        self.hand_tracker: Optional[IHandTracker] = None
        self.gesture_recognizer: Optional[IGestureRecognizer] = None
        self.renderer: Optional[IVisualizationRenderer] = None
        self.game_controller = None

        # State tracking
        self.frame_count = 0
        self.last_gesture = None
        self.last_fist_state = False  # Track if the last frame was a fist

        # Shoot display state
        self.shoot_display_until = 0  # Timestamp until which to show shoot indicator
        self.shoot_display_duration = self.performance_config.frame_processor.shoot_display_timeout

        # Shared gesture analysis pipeline
        self.pipeline = GesturePipeline(config, logger)

    def set_components(self, hand_tracker: IHandTracker,
                       gesture_recognizer: IGestureRecognizer,
                       renderer: IVisualizationRenderer,
                       game_controller=None) -> None:
        """Set component references."""
        self.hand_tracker = hand_tracker
        self.gesture_recognizer = gesture_recognizer
        self.renderer = renderer
        self.game_controller = game_controller
        self.pipeline.set_components(hand_tracker, gesture_recognizer, game_controller)

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

    def analyze_frame(self) -> Optional[FrameAnalysis]:
        """Analyze a single frame without rendering."""
        analysis = self.pipeline.analyze_frame()
        if analysis:
            self.frame_count = self.pipeline.frame_count
            self.last_gesture = self.pipeline.last_gesture
        return analysis

    def process_frame(self) -> bool:
        """
        Process a single frame from the camera.

        Returns:
            True if processing should continue, False if should stop
        """
        try:
            analysis = self.analyze_frame()
            if not analysis:
                return False

            if self.renderer:
                self._render_comprehensive_frame(analysis)

            cv2.imshow("Gesture Control", analysis.camera_frame.frame)

            debug_frequency = self.performance_config.frame_processor.debug_frame_frequency
            if self.frame_count % debug_frequency == 0:
                self.logger.debug(
                    f"Displaying frame {self.frame_count}, window should be visible")

            return True

        except Exception as e:
            self.logger.error(f"Frame processing error: {e}")
            return False

    def _render_comprehensive_frame(self, analysis: FrameAnalysis) -> None:
        """Render all visual elements on the frame."""
        try:
            if not self.renderer:
                self.logger.warning(
                    "Renderer not available for frame rendering")
                return

            camera_frame = analysis.camera_frame
            gesture_results = analysis.gesture_results
            control_state = analysis.control_state
            debug_info = analysis.debug_info or {}

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

            # 3. Render debug information and head gesture bars if enabled
            if self.config.ui.show_debug_info:
                self.renderer.render_debug_info(frame, debug_info)

                head_strengths = debug_info.get("head_strengths")
                if head_strengths:
                    self.renderer.render_gesture_bars(frame, head_strengths)

            # 5. Render shoot indication with display timeout
            current_time = time.time()

            # Check if new shoot detected
            if debug_info.get("is_shooting"):
                self.shoot_display_until = current_time + self.shoot_display_duration
                self.logger.info(
                    f"[ACTION] Detected - displaying for {self.shoot_display_duration:.1f}s")

            # Show shoot indicator if still within display time
            if current_time < self.shoot_display_until:
                self.renderer.render_shoot_indication(frame, True)

        except Exception as e:
            self.logger.error(f"Rendering error: {e}")

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
