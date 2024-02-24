import numpy as np
import pyaudio
import sys
import matplotlib.pyplot as plt

def getPyAudio():
    global p
    p = pyaudio.PyAudio()

def stop():
    p.terminate()

def playRecording(file_path, speed=1, volume=1):
    # for testing

    # Define voice class
    voice = sound(file_path, speed, volume)

    # To plot waveform
    voice.visualize()

    # To play
    voice.playSound(speed, volume)    

    # To change speed 
    '''voice.playSound(2, volume)

    # To change volume
    voice.playSound(speed, 2)

    # To pause
    voice.pause()

    # To unpause
    voice.playSound(speed, volume)'''

    # To replay
    #voice.replay(1, 1)
    voice.replay(speed, volume)

    # To stop???
    voice.stop()
    
class sound():
    def __init__(self, file_path, speed=1, volume=1):
        self.file_path = file_path
        self.speed = speed
        self.volume = volume
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
                '''if self.sample_rate != 44100:
                    raise ValueError('Sampling Rate is not Supported.')'''
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
                    sample.append(int.from_bytes(self.data[i+j*self.block_align:i+(j+1)*self.block_align], byteorder='little', signed=True))
                audio.append(sample)
            return np.array(audio, dtype=np.int32) 
        elif speed == 2:
            audio = []
            for i in range(0, len(self.data), self.block_align):
                sample = []
                for j in range(self.num_channels):
                    sample.append(int.from_bytes(self.data[i+j*self.block_align:i+(j+1)*self.block_align], byteorder='little', signed=True))
                audio.append(sample)
            audio_resample = []
            for i in range(0, len(audio)-1, 2):
                audio_resample.append([int((audio[i][0] + audio[i+1][0])/2), int((audio[i][1] + audio[i+1][1])/2)])
            return np.array(audio_resample, dtype=np.int32)
        elif speed == 0.5:
            audio = []
            for i in range(0, len(self.data), self.block_align):
                sample = []
                for j in range(self.num_channels):
                    sample.append(int.from_bytes(self.data[i+j*self.block_align:i+(j+1)*self.block_align], byteorder='little', signed=True))
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

    def playSound(self, speed=1, volume=1):
        # or unpause
        self.speed = speed
        self.volume = volume
        if self.speed == 1:
            self.normalSpeed(self.volume)
        elif self.speed == 2:
            self.doubleSpeed(self.volume)
        elif self.speed == 0.5:
            self.halfSpeed(self.volume)
        else:
            raise ValueError('Invalid speed.')

    def normalSpeed(self, volume=1):
        if self.stream.is_active:
            self.pause()
            self.stream = self.getStream()
        CHUNK = 2
        data = np.multiply(self.dataNormal, volume).astype(np.int32)
        while data.size != 0:
            self.stream.write(data[:CHUNK].astype(np.int32).tobytes())
            data = data[CHUNK:]
            self.dataNormal = self.dataNormal[CHUNK:]
            self.dataDouble = self.dataDouble[int(CHUNK/2):]
            self.dataHalf = self.dataHalf[(CHUNK*2):]

    def doubleSpeed(self, volume=1):
        if self.stream.is_active:
            self.pause()
            self.stream = self.getStream()
        CHUNK = 2
        data = np.multiply(self.dataDouble, volume).astype(np.int32)
        while data.size != 0:
            self.stream.write(data[:int(CHUNK/2)].astype(np.int32).tobytes())
            data = data[int(CHUNK/2):]
            self.dataNormal = self.dataNormal[CHUNK:]
            self.dataDouble = self.dataDouble[int(CHUNK/2):]
            self.dataHalf = self.dataHalf[(CHUNK*2):]

    def halfSpeed(self, volume=1):
        if self.stream.is_active:
            self.pause()
            self.stream = self.getStream()
        CHUNK = 2
        data = np.multiply(self.dataHalf, volume).astype(np.int32)
        while data.size != 0:
            self.stream.write(data[:(CHUNK*2)].astype(np.int32).tobytes())
            data = data[(CHUNK*2):]
            self.dataNormal = self.dataNormal[CHUNK:]
            self.dataDouble = self.dataDouble[int(CHUNK/2):]
            self.dataHalf = self.dataHalf[(CHUNK*2):]

    def pause(self):
        self.stream.stop_stream()

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()

    def replay(self, speed=1, volume=1):
        self.speed = speed
        self.volume = volume
        self.stream.stop_stream()
        self.stream.close()
        self.stream = self.getStream()
        self.dataNormal = self.getData(1)
        self.dataDouble = self.getData(2)
        self.dataHalf = self.getData(0.5)
        self.playSound(self.speed, self.volume)

    def visualize(self):
        amplitude = np.max(self.dataArray, axis=1)
        time = len(amplitude) // self.sample_rate
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
    playRecording("example.wav", 1, volume)
    playRecording("example.wav", 2, volume)
    playRecording("example.wav", 0.5, volume)
    stop()
