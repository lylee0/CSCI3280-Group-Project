import pyaudio
import numpy as np
import time
from scipy import signal
import librosa

p = pyaudio.PyAudio()

input_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, input=True, frames_per_buffer=1024)
output_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100, output=True, frames_per_buffer=1024) # alien voice: rate=54100


def main():
    while True:
        data = input_stream.read(1024, exception_on_overflow = False)

        data_in = np.frombuffer(data, dtype=np.float32)
        pitch_shifted = librosa.effects.pitch_shift(data_in, sr=44100, n_steps=12) # women: n_steps=12 | men: n_steps=-12
        #signal_shitfed = signal.resample_poly(data_in, 1, int(1 / 1.2))

        data_out = pitch_shifted.astype(np.float32).tobytes()
        #audio_data = np.resize(signal, (signal_shitfed,))
        output_stream.write(data_out, 1024)

def stop():
    input_stream.stop_stream()
    output_stream.stop_stream()
    input_stream.close()
    output_stream.close()
    p.terminate()

if __name__:
    try:
        main()
    except KeyboardInterrupt:
        stop()