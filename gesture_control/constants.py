"""
Centralized constants for the gesture control system.

This module contains all configuration constants used across
the gesture control system to avoid duplication and make changes easier.
"""

# Camera and MediaPipe constants
DEFAULT_CAMERA_WIDTH = 640
DEFAULT_CAMERA_HEIGHT = 480
DEFAULT_FPS = 30
DEFAULT_CAMERA_INDEX = 0

# Hand tracking constants
MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.5
MAX_NUM_HANDS = 1

# Gesture detection thresholds
FIST_THRESHOLD = 0.7
POSITION_STEP = 5.0
GESTURE_COOLDOWN = 0.1

# UI and rendering constants
LANDMARK_RADIUS = 3
CONNECTION_THICKNESS = 1
FONT_SCALE = 0.7
TEXT_THICKNESS = 2
LINE_SPACING = 30

# Colors (BGR format for OpenCV)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_BLACK = (0, 0, 0)

# Performance settings
FPS_AVERAGING_WINDOW = 30
HISTORY_SIZE = 5
CALIBRATION_REQUIRED_FRAMES = 30
CALIBRATION_STABILITY_TIMEOUT = 3.0

# Timing settings
SHOOT_DISPLAY_TIMEOUT = 0.5
DEBUG_DISPLAY_TIMEOUT = 1.0
DEBUG_FRAME_FREQUENCY = 30
