import pyaudio
import numpy as np

class MicrophoneManager:
    def __init__(self, rate=16000, channels=1, chunk_duration=0.25):
        self.rate = rate
        self.channels = channels
        self.chunk = int(rate * chunk_duration)
        self.stream = None
        self.p = None

    def start_microphone(self):
        """Inicia el micrófono para grabar audio."""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        print("Micrófono iniciado.")

    def stop_microphone(self):
        """Detiene el micrófono."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            print("Micrófono detenido.")

    def record_audio(self, duration=10):
        """Graba audio durante un período específico y devuelve un array numpy."""
        print(f"Grabando por {duration} segundos...")
        frames = []
        for _ in range(0, int(self.rate / self.chunk * duration)):
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            frames.append(np.frombuffer(data, dtype=np.int16))
        audio_array = np.hstack(frames).astype(np.float32) / 32768.0  # Normalización
        print("Grabación completada.")
        return audio_array
