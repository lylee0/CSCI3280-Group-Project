import noisereduce as nr
import numpy as np
import pyaudio

def noiseReductionLibrary(path, targetPath):
    with open(path,'rb') as input:
        # Here are the original information
            masterFormat = input.read(4) #"RIFF"
            chunkSize = int.from_bytes(input.read(4), byteorder='little') #little, N+36
            waveFormat = input.read(4) #"WAVE"
            if (masterFormat != b'RIFF') or (waveFormat != b'WAVE'):
                    raise ValueError('File is not in WAV format.')
            formatChunk = input.read(4) #"fmt "
            formatChunkSize = int.from_bytes(input.read(4), byteorder='little') #little, 16
            audioFormat = int.from_bytes(input.read(2), byteorder='little') #little, PCM
            if audioFormat != 1:
                    raise ValueError('File is not in PCM format.')
            channelNumber = int.from_bytes(input.read(2), byteorder='little') #little
            fsRate = int.from_bytes(input.read(4), byteorder='little') #little
            byteRate = int.from_bytes(input.read(4), byteorder='little') #little
            blockAlign = int.from_bytes(input.read(2), byteorder='little') #little
            bitPerSample = int.from_bytes(input.read(2), byteorder='little') #little
            dataChunk = input.read(4) #"LIST", "data"
            if dataChunk != b'data':
                raise ValueError('Invalid WAV file.')
            dataChunkSize = int.from_bytes(input.read(4), byteorder='little') #little
            data = input.read(dataChunkSize) #little
    audio = []
    for i in range(0, len(data), blockAlign):
        sample = []
        for j in range(channelNumber):
            sample.append(int.from_bytes(data[i+j*int(blockAlign)//2:i+(j+1)*int(blockAlign)//2], byteorder='little', signed=True))
        audio.append(sample)
    transformData = np.array(audio, dtype=np.int32)
    print(transformData)
    reduced_noise = nr.reduce_noise(transformData, 1)
    with open(targetPath,'wb') as output:
        output.write(masterFormat)
        output.write(chunkSize)
        output.write(waveFormat)
        output.write(formatChunk)
        output.write(formatChunkSize)
        output.write(audioFormat)
        output.write(channelNumber)
        output.write(fsRate)
        output.write(byteRate)
        output.write(blockAlign)
        output.write(bitPerSample)
        output.write(dataChunk)
        output.write(dataChunkSize)
        output.write(reduced_noise) 


# load data
noiseReductionLibrary('example.wav', 'targetExample.wav')