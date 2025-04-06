import cv2
import mediapipe as mp
import mido
from mido import Message

# OpenCV Setup
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

print(mido.get_output_names())
# MIDI Setup
midi_output = mido.open_output('GestureControlBus Bus 1')  # Adjust this if you named your bus differently

# Function to send MIDI message
def send_midi_control_change(control_number, value):
    msg = Message('control_change', control=control_number, value=value)
    midi_output.send(msg)
    print(f"Sent MIDI Control Change: Control Number = {control_number}, Value = {value}")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame for natural interaction
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame for hand detection
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmark coordinates for specific points (e.g., index finger tip and thumb tip)
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Calculate the distance between thumb and index tip
            distance = ((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2) ** 0.5

            # If distance is small, assume gesture is a "pinch"
            if distance < 0.05:
                send_midi_control_change(1, 127)  # Send a control change message with max value
            else:
                send_midi_control_change(1, 0)    # Send a control change message with min value

    cv2.imshow("Gesture Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
midi_output.close()