import sounddevice as sd
import numpy as np
from pydub import AudioSegment
from pydub.effects import reverb
import queue
import threading

class AudioProcessor:
    def __init__(self, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.audio_data = []
        self.current_effect = None

    def start_recording(self):
        self.is_recording = True
        threading.Thread(target=self.record_audio).start()
    
    def stop_recording(self):
        self.is_recording = False
        self.save_audio()
    
    def record_audio(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback):
            while self.is_recording:
                sd.sleep(100)
    
    def audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata.copy())
    
    def process_audio(self):
        while not self.audio_queue.empty():
            data = self.audio_queue.get()
            self.audio_data.append(data)
    
    def apply_effect(self, effect_name):
        self.current_effect = effect_name
    
    def save_audio(self, filename="output.mp3"):
        self.process_audio()
        audio_np = np.concatenate(self.audio_data, axis=0)
        audio_segment = AudioSegment(
            audio_np.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=audio_np.dtype.itemsize,
            channels=self.channels
        )
        
        if self.current_effect == "reverb":
            audio_segment = reverb(audio_segment)

        audio_segment.export(filename, format="mp3")
        print(f"Audio saved to {filename}")