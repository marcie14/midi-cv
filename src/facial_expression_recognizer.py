import cv2
import mediapipe as mp

class FacialExpressionRecognizer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.face_mesh.process(rgb_frame)

    def draw_landmarks(self, frame, face_landmarks):
        self.mp_draw.draw_landmarks(frame, face_landmarks, self.mp_face_mesh.FACEMESH_TESSELATION)

    def get_expression(self, face_landmarks):
        # Define landmark indices for eyes
        LEFT_EYE_INDICES = [33, 160, 158, 133]  # Approximation for left eye
        RIGHT_EYE_INDICES = [362, 385, 387, 263]  # Approximation for right eye

        # Extract landmark positions
        left_eye = [face_landmarks.landmark[i] for i in LEFT_EYE_INDICES]
        right_eye = [face_landmarks.landmark[i] for i in RIGHT_EYE_INDICES]

        # Calculate eye aspect ratio (simple approximation)
        left_eye_ratio = abs(left_eye[1].y - left_eye[2].y) / abs(left_eye[0].x - left_eye[3].x)
        right_eye_ratio = abs(right_eye[1].y - right_eye[2].y) / abs(right_eye[0].x - right_eye[3].x)

        # Thresholds for detecting winks (these can be adjusted)
        if left_eye_ratio < 0.2 and right_eye_ratio > 0.3:
            return "wink_left"
        elif right_eye_ratio < 0.2 and left_eye_ratio > 0.3:
            return "wink_right"
        else:
            return "neutral"