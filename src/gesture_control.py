import mido
from mido import Message

class GestureControl:
    def __init__(self, midi_port_name):
        self.midi_output = mido.open_output(midi_port_name)
        self.previous_command = None

    def send_midi_control_change(self, control_number, value):
        msg = Message('control_change', control=control_number, value=value)
        self.midi_output.send(msg)
        print(f"Sent MIDI Control Change: Control Number = {control_number}, Value = {value}")

    def process_gesture(self, gesture_name):
        commands = {
            "open_hand": (1, 0),
            "point": (2, 127),
            "peace": (3, 127),
            "pinch": (4, 127),
            "fist": (5, 0)  # Undo last command
        }

        if gesture_name in commands:
            control_number, value = commands[gesture_name]
            self.send_midi_control_change(control_number, value)

            if gesture_name != "fist":
                self.previous_command = (control_number, value)
            elif gesture_name == "fist" and self.previous_command:
                # Undo last command
                self.send_midi_control_change(self.previous_command[0], 0)
                self.previous_command = None

    def close(self):
        self.midi_output.close()