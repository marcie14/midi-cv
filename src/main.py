import cv2
from gesture_recognizer import HandLandmarks
from midi_controller import MIDIController
from audio_processor import AudioProcessor  # Import the new AudioProcessor class

# OpenCV Setup
cap = cv2.VideoCapture(0)
gesture_recognizer = HandLandmarks()

# MIDI Setup
midi_controller = MIDIController('GestureControlBus Bus 1')

# Audio Processor Setup
audio_processor = AudioProcessor()
recording_video = False
recording_audio = False

# Video saving setup
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None  # We won't initialize the VideoWriter until we start recording

# Gesture to Effect Mapping
GESTURE_EFFECTS = {
    "open": None,            # Remove all effects
    "point": "synth",
    "peace": "backing_track",
    "pinch": "reverb",
    "fist": "undo"
}
applied_effects = []
# Fixed font parameters
font_scale = 2  # Fixed font size
font_thickness = 4  # Thickness of the text
font_color = (180, 105, 255)  # Hot pink color for text (B, G, R)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Hand Gesture Detection
    result = gesture_recognizer.detect(frame)
    if result:
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                gesture_recognizer.draw_landmarks(frame, hand_landmarks)
                gesture = gesture_recognizer.get_gesture(hand_landmarks)
                print(gesture)

                if gesture in GESTURE_EFFECTS:
                    effect = GESTURE_EFFECTS[gesture]
                    if effect == "reverb":
                        applied_effects = audio_processor.apply_effect("reverb")
                        print("Applied Reverb Effect")
                    elif effect == "synth":
                        applied_effects = audio_processor.apply_effect("synth")
                        print("Synth Effect Triggered (to be implemented)")
                    elif effect == "backing_track":
                        applied_effects = audio_processor.apply_effect("backing_track")
                        print("Backing Track Triggered (to be implemented)")
                    elif effect == "undo":
                        applied_effects = audio_processor.apply_effect("remove-last")
                        print("Removed last effect")
                    elif effect is None:
                        applied_effects = audio_processor.apply_effect(None)
                        print("No Effect Applied")
    cv2.putText(frame, f"{applied_effects}", (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, font_thickness)

    # Display the frame
    cv2.imshow("Gesture & Expression Control", frame)

    k = cv2.waitKey(1) & 0xFF

    if k == ord('r'):  # Toggle video recording when 'r' is pressed
        if not recording_video:
            # Start recording video
            out = cv2.VideoWriter('output_video.avi', fourcc, 20.0, (frame_width, frame_height))
            recording_video = True
            audio_processor.start_recording()  # Start audio recording
            recording_audio = True
            print("Recording Started (Video & Audio)")
            cv2.putText(frame, "Recording...", (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, font_thickness)
        else:
            # Stop recording video
            out.release()
            recording_video = False
            audio_processor.stop_recording()  # Stop audio recording
            recording_audio = False
            print("Recording Stopped")
            cv2.putText(frame, "Recording Stopped", (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), font_thickness)

    if k == ord('q'):  # Quit the program
        break

    # Write the frame to the video file if recording
    if recording_video:
        out.write(frame)

cap.release()
cv2.destroyAllWindows()
midi_controller.close()

# After exiting the loop, stop recording if necessary
if recording_audio:
    audio_processor.stop_recording()  # Make sure to stop audio recording