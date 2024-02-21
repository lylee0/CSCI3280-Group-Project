import numpy as np
import pygame

def playRecording(file_path):
    voice = sound(file_path)
    voice.playSound(speed=1)
    pygame.quit()
    return

def doubleSpeed(file_path):
    voice = sound(file_path)
    voice.playSound(speed=2)
    pygame.quit()
    return

def halfSpeed(file_path):
    voice = sound(file_path)
    voice.playSound(speed=0.5)
    pygame.quit()
    return

def pause():
    pygame.mixer.pause()
    return

def unpause():
    pygame.mixer.unpause()
    return

def voulume(v, change):
    current = v.get_volume()
    v.set_volume(current + change)
    return

class sound():
    def __init__(self, file_path):
        self.file_path = file_path
        if file_path[-4:] == ".wav":
            with open(self.file_path, "rb") as recording:
                self.chunk_id = recording.read(4) #"RIFF"
                self.chunk_size = int.from_bytes(recording.read(4), byteorder='little') #little, N+36
                self.format = recording.read(4) #"WAVE"
                self.subChunkID_1 = recording.read(4) #"fmt "
                self.subChunkSize_1 = int.from_bytes(recording.read(4), byteorder='little') #little, 16
                self.audio_format = int.from_bytes(recording.read(2), byteorder='little') #little, PCM
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
        
    def verify(self):
        if (self.chunk_id != b'RIFF') or (self.format != b'WAVE'):
            raise ValueError('File is not in WAV format.')
        if self.audio_format != 1:
            raise ValueError('File is not in PCM format.')
        return
    
    def getData(self):
        audio = []
        for i in range(0, len(self.data), self.block_align):
            sample = []
            for j in range(self.num_channels):
                sample.append(int.from_bytes(self.data[i+j*self.block_align:i+(j+1)*self.block_align], byteorder='little', signed=True))
            audio.append(sample)
        
        return np.array(audio)

    def playSound(self, speed=1):
        self.verify()
        v = self.getMixer(speed)
        v.play()
        v.set_volume(0.5)
        while(pygame.mixer.get_busy()):
            continue
        return

    def getMixer(self, speed=1):
        # bug
        pygame.mixer.init(int(self.sample_rate*speed), -self.bits_per_sample, self.num_channels, 1024)
        return pygame.mixer.Sound(self.getData())

if __name__ == "__main__":
    playRecording("test.wav")
    doubleSpeed("test.wav")
    halfSpeed("test.wav")
