import numpy as np
import pyaudio
import sys

def getPyAudio():
    global p
    p = pyaudio.PyAudio()

def playRecording(file_path, speed=1):
    voice = sound(file_path, speed)
    voice.playSound()
    
def stop():
    p.terminate()

class sound():
    def __init__(self, file_path, speed=1):
        self.file_path = file_path
        self.speed = speed
        if file_path[-4:] == ".wav":
            with open(self.file_path, "rb") as recording:
                self.chunk_id = recording.read(4) #"RIFF"
                self.chunk_size = int.from_bytes(recording.read(4), byteorder='little') #little, N+36
                self.format = recording.read(4) #"WAVE"
                if (self.chunk_id != b'RIFF') or (self.format != b'WAVE'):
                    raise ValueError('File is not in WAV format.')
                self.subChunkID_1 = recording.read(4) #"fmt "
                self.subChunkSize_1 = int.from_bytes(recording.read(4), byteorder='little') #little, 16
                self.audio_format = int.from_bytes(recording.read(2), byteorder='little') #little, PCM
                if self.audio_format != 1:
                    raise ValueError('File is not in PCM format.')
                self.num_channels = int.from_bytes(recording.read(2), byteorder='little') #little
                self.sample_rate = int.from_bytes(recording.read(4), byteorder='little') #little
                self.byte_rate = int.from_bytes(recording.read(4), byteorder='little') #little
                self.block_align = int.from_bytes(recording.read(2), byteorder='little') #little
                self.bits_per_sample = int.from_bytes(recording.read(2), byteorder='little') #little
                self.subChunkID_2 = recording.read(4) #"LIST", "data"
                if self.subChunkID_2 != b'data':
                    raise ValueError('Invalid WAV file.')
                self.subChunkSize_2 = int.from_bytes(recording.read(4), byteorder='little') #little
                self.data = recording.read(self.subChunkSize_2) #little
                recording.close()
        else:
            raise ValueError('Wrong file name.')
    
    def getData(self):
        audio = []
        for i in range(0, len(self.data), self.block_align):
            sample = []
            for j in range(self.num_channels):
                sample.append(int.from_bytes(self.data[i+j*self.block_align:i+(j+1)*self.block_align], byteorder='little', signed=True))
            audio.append(sample)
        
        return np.array(audio, dtype=np.int32) 

    def playSound(self):
        try:
            self.stream = p.open(format=pyaudio.paInt32,
                    channels=self.num_channels,
                    rate=int(self.sample_rate * self.speed),
                    output=True)
        except OSError:
            sys.exit(0)

        self.stream.write(self.data)
        self.stream.stop_stream()
        self.stream.close()

if __name__ == "__main__":
    # call getPyAudio before play
    # press the button to select the value of speed
    # press the play button to play the audio
    # press the stop button to stop
    getPyAudio()
    playRecording("test.wav", 1)
    playRecording("test.wav", 2)
    playRecording("test.wav", 0.5)
    stop()
