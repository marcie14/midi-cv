import mido
from mido import Message

class MIDIController:
    def __init__(self, port_name):
        self.midi_output = mido.open_output(port_name)

    def send_control_change(self, control_number, value):
        msg = Message('control_change', control=control_number, value=value)
        self.midi_output.send(msg)
        print(f"Sent MIDI Control Change: Control Number = {control_number}, Value = {value}")

    def close(self):
        self.midi_output.close()