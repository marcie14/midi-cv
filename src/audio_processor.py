import pyaudio
import wave
import threading
from pydub import AudioSegment, effects
from pydub.playback import play
import os
import time

class AudioProcessor:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        self.effects_timeline = []  # List of (start_time, end_time, effect)
        self.current_effect = None
        self.effect_start_time = None
        self.last_removal_time = 0
        self.recording = False
        self._stop_event = threading.Event()
        self._thread = None
        self.audio = pyaudio.PyAudio()
        self.record_start_time = None

    def _record(self):
        stream = self.audio.open(format=self.format,
                                 channels=self.channels,
                                 rate=self.rate,
                                 input=True,
                                 frames_per_buffer=self.chunk)
        while not self._stop_event.is_set():
            data = stream.read(self.chunk)
            self.frames.append(data)
        stream.stop_stream()
        stream.close()

    def start_recording(self):
        self.frames = []
        self.effects_timeline = []
        self.current_effect = None
        self.effect_start_time = None
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._record)
        self._thread.start()
        self.recording = True

    def stop_recording(self, filename="output.mp3"):
        self._stop_event.set()
        self._thread.join()
        self.recording = False
        record_end_time = time.time()
        
        # Add a final segment if needed
        if self.current_effect is not None and self.effect_start_time is not None:
            self.effects_timeline.append((self.effect_start_time - self.record_start_time, record_end_time - self.record_start_time, self.current_effect))

        # get current dir
        current_dir = os.getcwd()
        # check if output.mp3 already exists
        output_path = os.path.join(current_dir, filename)
        if os.path.exists(output_path):
            print(f"{filename} already exists. Overwriting...")
            os.remove(output_path)

        # Save raw audio to a temporary WAV file
        temp_wav_path = os.path.join(current_dir, "temp_recording.wav")
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
    
        wf = wave.open(temp_wav_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Load with pydub
        raw = AudioSegment.from_wav(temp_wav_path)

        if not self.effects_timeline:
            processed = raw
        else:
            for i, (start, end, effect) in enumerate(self.effects_timeline):
                start_ms = int(start * 1000)
                end_ms = int(end * 1000)
                segment = raw[start_ms:end_ms]
                if effect == "reverb":
                    segment = effects.normalize(segment).fade_in(50).fade_out(50)
                elif effect == "synth":
                    # Placeholder: speed up and pitch shift
                    segment = segment._spawn(segment.raw_data, overrides={
                        "frame_rate": int(segment.frame_rate * 1.3)
                    }).set_frame_rate(segment.frame_rate)
                elif effect == "backing_track":
                    # Placeholder: add silence to simulate background track
                    background = AudioSegment.silent(duration=len(segment), frame_rate=self.rate) + 3
                    segment = processed.overlay(background - 30)  # quieter background
                processed += segment
        processed.export(output_path, format="mp3")
        os.remove(temp_wav_path)
        print(f"Saved: {output_path}")
        processed.export(output_path, format="mp3")
        os.remove(temp_wav_path)
        print(f"Saved: {output_path}")

    def apply_effect(self, effect_name):
        current_time = time.time()

        if effect_name == "remove-last":
            if self.effects_timeline and current_time - self.last_removal_time >= 1:
                removed = self.effects_timeline.pop()
                print(f"Removing effect: {removed[2]} from {removed[0]:.2f}s to {removed[1]:.2f}s")
                self.last_removal_time = current_time
            else:
                print("Remove-last gesture detected too soon or no effects to remove.")
            return [e[2] for e in self.effects_timeline]

        # Close previous effect segment
        if self.current_effect is not None and self.effect_start_time is not None:
            self.effects_timeline.append((self.effect_start_time - self.record_start_time, current_time - self.record_start_time, self.current_effect))

        if effect_name is None:
            print("Clearing current effect.")
            self.current_effect = None
            self.effect_start_time = None
        else:
            print(f"Activating effect: {effect_name}")
            self.current_effect = effect_name
            self.effect_start_time = current_time

        return [e[2] for e in self.effects_timeline]
    
    def terminate(self):
        self.audio.terminate()