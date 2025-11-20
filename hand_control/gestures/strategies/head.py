from typing import List, Optional
from ...core.types import GestureResult, GestureType, HeadGesture


class HeadGestureDetectionStrategy:
    """
    Detect basic head orientation gestures based on relative landmark positions.
    Uses normalized coordinates (0..1) so it works regardless of distance to camera.
    """

    def __init__(self):
        self.last_gesture = None
        self.stable_frames = 0
        self.pitch_neutral = None


    NOSE = 1
    LEFT_EYE = 263
    RIGHT_EYE = 33
    LEFT_EAR = 454
    RIGHT_EAR = 234


    def detect(self, face_landmarks: Optional[List[tuple]]) -> List[GestureResult]:
        if not face_landmarks:
            # Reset because no face = no gesture
            self.last_gesture = None
            self.stable_frames = 0
            return []

        gestures = []

        nose = face_landmarks[self.NOSE]
        left_eye = face_landmarks[self.LEFT_EYE]
        right_eye = face_landmarks[self.RIGHT_EYE]

        # Normalize coordinates to face size
        # This makes detection independent of distance from camera
        x_values = [p[0] for p in face_landmarks]
        y_values = [p[1] for p in face_landmarks]

        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)

        def norm(p):
            return (
                (p[0] - min_x) / (max_x - min_x + 1e-6),
                (p[1] - min_y) / (max_y - min_y + 1e-6),
                p[2]
            )

        nose = norm(nose)
        left_eye = norm(left_eye)
        right_eye = norm(right_eye)

        # Debug print normalized head geometry
        eye_center_x = (left_eye[0] + right_eye[0]) / 2
        eye_center_y = (left_eye[1] + right_eye[1]) / 2

        yaw = nose[0] - eye_center_x
        pitch = nose[1] - eye_center_y
        roll = left_eye[1] - right_eye[1]

        # Set baseline pitch when head is neutral (first stable frame)
        if self.pitch_neutral is None:
            self.pitch_neutral = pitch

        print(
            f"yaw={yaw:.3f}   pitch={pitch:.3f}   roll={roll:.3f}"
        )

        # ==== TURN (Yaw) ====
        TURN_THRESHOLD = 0.14
        NEUTRAL_ZONE = 0.05

        if yaw > TURN_THRESHOLD:
            gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.TURN_RIGHT}))
        elif yaw < -TURN_THRESHOLD:
            gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.TURN_LEFT}))
        elif abs(yaw) < NEUTRAL_ZONE:
            if self.last_gesture in (HeadGesture.TURN_LEFT, HeadGesture.TURN_RIGHT):
                self.last_gesture = None
                self.stable_frames = 0

        # ==== NOD (Pitch) with adaptive neutral baseline ====
        if self.pitch_neutral is not None:
            if pitch > self.pitch_neutral + 0.12:
                gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.NOD_DOWN}))
            elif pitch < self.pitch_neutral - 0.12:
                gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.NOD_UP}))

        # ==== TILT (Roll) ====
        if roll > 0.17:   # TILT_RIGHT
            gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.TILT_RIGHT}))
        elif roll < -0.17:  # TILT_LEFT
            gestures.append(GestureResult(GestureType.HEAD, 0.9, data={'head_gesture': HeadGesture.TILT_LEFT}))

        # Keep only one gesture
        if len(gestures) > 1:
            gestures = [gestures[0]]

        # Stabilization (gesture must persist for a few frames)
        if gestures:
            gesture = gestures[0].data['head_gesture']
            if gesture == self.last_gesture:
                self.stable_frames += 1
            else:
                self.stable_frames = 0
            self.last_gesture = gesture

            if self.stable_frames < 3:
                return []

        return gestures
