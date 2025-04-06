import cv2
import mediapipe as mp

class HandLandmarks:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb_frame)

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def get_landmark(self, hand_landmarks, landmark):
        return hand_landmarks.landmark[landmark]

    def get_gesture(self, hand_landmarks):
        thumb_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.THUMB_TIP)
        index_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_TIP)
        third_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP)
        ring_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.RING_FINGER_TIP)
        pinky_tip = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.PINKY_TIP)
        
        thumb_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.THUMB_MCP)
        index_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.INDEX_FINGER_MCP)
        third_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.MIDDLE_FINGER_MCP)
        ring_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.RING_FINGER_MCP)
        pinky_mcp = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.PINKY_MCP)
        
        wrist = self.get_landmark(hand_landmarks, self.mp_hands.HandLandmark.WRIST)
        
        point_index = index_tip.y < index_mcp.y
        point_third = third_tip.y < third_mcp.y
        point_fourth = ring_tip.y < ring_mcp.y
        point_pinky = pinky_tip.y < pinky_mcp.y
        point_thumb = thumb_tip.y < index_mcp.y
        print(point_third)

        # check point
        is_point = (point_index > 0 and point_third < 1 and point_fourth < 1 and point_pinky < 1)
        
        # check peace
        is_peace = (point_index > 0 and point_third > 0 and point_fourth < 1 and point_pinky < 1)
        
        # check pinch
        pinch_distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5
        is_pinch = pinch_distance < 0.1
        
        # check fist
        is_fist = (point_index < 1 and point_third < 1 and point_fourth < 1 and point_pinky < 1)
        
        

        if is_point:
            return "point"
        elif is_peace:
            return "peace"
        elif is_pinch:
            return "pinch"
        elif is_fist:
            return "fist"
        else:
            return "open"