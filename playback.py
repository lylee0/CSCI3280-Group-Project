import numpy as np
import pyaudio
import sys
import matplotlib.pyplot as plt

def getPyAudio():
    global p
    p = pyaudio.PyAudio()

def stop():
    p.terminate()

def playRecording(file_path, speed=1, volume=1, start=0):
    # for testing

    # Define voice class
    voice = sound(file_path, speed, volume, start)

    # To plot waveform
    voice.visualize()

    # To play
    voice.playSound(speed, volume, start)    

    # To change speed 
    '''voice.playSound(2, volume, start)

    # To change volume
    voice.playSound(speed, 2, start)

    # To pause
    voice.pause()

    # To unpause
    voice.playSound(speed, volume, start)'''

    # To replay
    #voice.replay(1, 1)
    voice.playSound(speed, volume, 0)

    # To stop???
    voice.stop()
    
class sound():
    def __init__(self, file_path, speed=1, volume=1, start=0):
        self.file_path = file_path
        self.speed = speed
        self.volume = volume
        self.start = start
        if file_path[-4:] == ".wav":
            with open(self.file_path, "rb") as recording:
                # Here are the original information
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
                          
                self.stream = self.getStream() # define stream
                self.dataArray = self.getData(1) # original data in numpy array

                # Here are the variables for editting
                self.dataNormal = self.getData(1)
                self.dataDouble = self.getData(2)
                self.dataHalf = self.getData(0.5)
        else:
            raise ValueError('Wrong file name.')
    
    def getData(self, speed=1):
        if speed == 1:
            audio = []
            for i in range(0, len(self.data), self.block_align):
                sample = []
                for j in range(self.num_channels):
                    sample.append(2**(32 - self.bits_per_sample) * int.from_bytes(self.data[i+j*self.block_align//self.num_channels:i+(j+1)*self.block_align//self.num_channels], byteorder='little', signed=True))
                audio.append(sample)
            return np.array(audio, dtype=np.int32) 
        elif speed == 2:
            audio = []
            for i in range(0, len(self.data), self.block_align):
                sample = []
                for j in range(self.num_channels):
                    sample.append(2**(32 - self.bits_per_sample) * int.from_bytes(self.data[i+j*self.block_align//self.num_channels:i+(j+1)*self.block_align//self.num_channels], byteorder='little', signed=True))
                audio.append(sample)
            audio_resample = []
            for i in range(0, len(audio)-1, 2):
                sample = []
                for j in range(self.num_channels):
                    sample.append(int((audio[i][j] + audio[i+1][j])/2))
                audio_resample.append(sample)
            return np.array(audio_resample, dtype=np.int32)
        elif speed == 0.5:
            audio = []
            for i in range(0, len(self.data), self.block_align):
                sample = []
                for j in range(self.num_channels):
                    sample.append(2**(32 - self.bits_per_sample) * int.from_bytes(self.data[i+j*self.block_align//self.num_channels:i+(j+1)*self.block_align//self.num_channels], byteorder='little', signed=True))
                audio.append(sample)
                audio.append(sample)
            return np.array(audio, dtype=np.int32)
        else:
            raise ValueError('Invalid speed.')

    def getStream(self):
        try:
            return p.open(format=pyaudio.paInt32,
            channels=self.num_channels,
            rate=self.sample_rate,
            output=True)
        except OSError:
            sys.exit(0)

    def playSound(self, speed=1, volume=1, start=0):
        # or unpause
        self.speed = speed
        self.volume = volume
        self.start = start
        if self.stream.is_active:
            self.pause()
            self.stream = self.getStream()

        if self.speed == 1:
            data = np.multiply(self.dataNormal, volume).astype(np.int32)
            data = data[int(self.start * self.sample_rate):]
        elif self.speed == 2:
            data = np.multiply(self.dataDouble, volume).astype(np.int32)
            data = data[int(self.start * int(self.sample_rate//2)):]
        elif self.speed == 0.5:
            data = np.multiply(self.dataHalf, volume).astype(np.int32)
            data = data[int(self.start * self.sample_rate * 2):]
        else:
            raise ValueError('Invalid speed.')
        
        self.stream.write(data.astype(np.int32).tobytes())

    def pause(self):
        self.stream.stop_stream()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def visualize(self):
        amplitude = np.max(self.dataArray, axis=1)
        time = len(amplitude) // self.sample_rate
        plt.figure(figsize=(10,5))
        plt.plot(np.linspace(0, time, num=len(amplitude)), amplitude, color='royalblue')
        plt.axis('off')
        plt.savefig('plot.png')

if __name__ == "__main__":
    # call getPyAudio before play
    # press the button to select the value of speed
    # press the play button to play the audio
    # press the stop button to stop
    # can adjust sound: from 0.05-3.5 (default is 1)
    getPyAudio()
    volume = 2
    start = 2
    playRecording("exampleMono.wav", 1, volume, start)
    playRecording("newTest.wav", 2, volume, start)
    playRecording("example.wav", 0.5, volume, start)
    stop()
