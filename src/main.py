import cv2
from gesture_recognizer import HandLandmarks
from facial_expression_recognizer import FacialExpressionRecognizer
from midi_controller import MIDIController
from audio_processor import AudioProcessor  # Import the new AudioProcessor class

# OpenCV Setup
cap = cv2.VideoCapture(0)
gesture_recognizer = HandLandmarks()
expression_recognizer = FacialExpressionRecognizer()

# MIDI Setup
midi_controller = MIDIController('GestureControlBus Bus 1')

# Audio Processor Setup
audio_processor = AudioProcessor()
recording = False

# Gesture to Effect Mapping
GESTURE_EFFECTS = {
    "open": None,            # Remove all effects
    "point": "synth",
    "peace": "backing_track",
    "pinch": "reverb",
    "fist": "undo"
}

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Hand Gesture Detection
    result = gesture_recognizer.detect(frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            gesture_recognizer.draw_landmarks(frame, hand_landmarks)
            gesture = gesture_recognizer.get_gesture(hand_landmarks)
            print(gesture)

            if gesture in GESTURE_EFFECTS:
                effect = GESTURE_EFFECTS[gesture]
                if effect == "reverb":
                    audio_processor.apply_effect("reverb")
                    print("Applied Reverb Effect")
                elif effect == "synth":
                    print("Synth Effect Triggered (to be implemented)")
                elif effect == "backing_track":
                    print("Backing Track Triggered (to be implemented)")
                elif effect == "undo":
                    audio_processor.apply_effect(None)
                    print("Removed All Effects")
                elif effect is None:
                    audio_processor.apply_effect(None)
                    print("No Effect Applied")

            # Send MIDI signals (optional, adjust if needed)
            if gesture == "open":
                midi_controller.send_control_change(1, 127)
            elif gesture == "point":
                midi_controller.send_control_change(2, 127)
            elif gesture == "peace":
                midi_controller.send_control_change(3, 127)
            elif gesture == "pinch":
                midi_controller.send_control_change(4, 127)
            elif gesture == "fist":
                midi_controller.send_control_change(5, 127)
            else:  # default open
                midi_controller.send_control_change(1, 0)

    cv2.imshow("Gesture & Expression Control", frame)
    k = cv2.waitKey(1) & 0xFF

    if k == ord('r'):
        if not recording:
            audio_processor.start_recording()
            recording = True
            print("Recording Started")
        else:
            audio_processor.stop_recording()
            recording = False
            print("Recording Stopped and Saved to output.mp3")

    if k == ord('q'):
        cv2.destroyAllWindows()
        break

cap.release()
cv2.destroyAllWindows()
midi_controller.close()