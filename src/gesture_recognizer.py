import cv2
import mediapipe as mp

class HandLandmarks:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, 
            max_num_hands=1, 
            min_detection_confidence=0.5,  # Adjusted for more leniency
            min_tracking_confidence=0.5    # Adjusted for better tracking
        )
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        # Convert the image to RGB as MediaPipe expects RGB input
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb_frame)  # Get hand landmarks

        if result.multi_hand_landmarks:
            return result
        else:
            return None

    def draw_landmarks(self, frame, hand_landmarks):
        # Draw the hand landmarks on the frame
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def get_landmark(self, hand_landmarks, landmark):
        # Get the specific landmark from hand landmarks
        return hand_landmarks.landmark[landmark]

    def get_gesture(self, hand_landmarks):
        # Get the landmarks of the hand to determine the gesture
        thumb_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.THUMB_TIP)
        index_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_TIP)
        third_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
        ring_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.RING_FINGER_TIP)
        pinky_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.PINKY_TIP)

        # get dip landmarks
        thumb_dip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.THUMB_IP)
        index_dip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_DIP)
        third_dip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_DIP)
        ring_dip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.RING_FINGER_DIP)
        pinky_dip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.PINKY_DIP)
        
        # get mcp landmarks
        thumb_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.THUMB_MCP)
        index_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_MCP)
        third_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP)
        ring_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.RING_FINGER_MCP)
        pinky_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.PINKY_MCP)

        wrist = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.WRIST)

        # Gesture recognition based on relative positions of landmarks
        point_index = index_tip.y < index_dip.y
        point_third = third_tip.y < third_dip.y
        point_fourth = ring_tip.y < ring_dip.y
        point_pinky = pinky_tip.y < pinky_dip.y
        point_thumb = thumb_tip.y < index_dip.y

        # Gesture detection
        is_open = (point_index and point_third and point_fourth and point_pinky)
        is_peace = (point_index and point_third and not point_fourth and not point_pinky)
        pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        is_pinch = pinch_distance < 0.1
        is_fist = (not point_index and not point_third and not point_fourth and not point_pinky)

        # Gesture assignment based on the conditions
        if is_open:
            return "open"
        elif is_peace:
            return "peace"
        elif is_pinch:
            return "pinch"
        elif is_fist:
            return "fist"
        else:
            return "point"