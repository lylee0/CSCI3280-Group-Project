import numpy as np
import pyaudio
import sys
import matplotlib.pyplot as plt

def getPyAudio():
    global p
    p = pyaudio.PyAudio()

def stop():
    p.terminate()
    
def readWav(file_path):
    if file_path[-4:] == ".wav":
        with open(file_path, "rb") as recording:
            # Here are the original information
            chunk_id = recording.read(4) #"RIFF"
            chunk_size = int.from_bytes(recording.read(4), byteorder='little') #little, N+36
            format = recording.read(4) #"WAVE"
            if (chunk_id != b'RIFF') or (format != b'WAVE'):
                raise ValueError('File is not in WAV format.')
            subChunkID_1 = recording.read(4) #"fmt "
            subChunkSize_1 = int.from_bytes(recording.read(4), byteorder='little') #little, 16
            audio_format = int.from_bytes(recording.read(2), byteorder='little') #little, PCM
            if audio_format != 1:
                raise ValueError('File is not in PCM format.')
            num_channels = int.from_bytes(recording.read(2), byteorder='little') #little
            sample_rate = int.from_bytes(recording.read(4), byteorder='little') #little
            byte_rate = int.from_bytes(recording.read(4), byteorder='little') #little
            block_align = int.from_bytes(recording.read(2), byteorder='little') #little
            bits_per_sample = int.from_bytes(recording.read(2), byteorder='little') #little
            subChunkID_2 = recording.read(4) #"LIST", "data"
            if subChunkID_2 != b'data':
                raise ValueError('Invalid WAV file.')
            subChunkSize_2 = int.from_bytes(recording.read(4), byteorder='little') #little
            data = recording.read(subChunkSize_2) #little
            recording.close()      

            return {"chunk_id": chunk_id, "chunk_size": chunk_size, "format": format,
                    "subChunkID_1": subChunkID_1, "subChunkSize_1": subChunkSize_1,
                    "audio_format": audio_format, "num_channels": num_channels, "sample_rate": sample_rate,
                    "byte_rate": byte_rate, "block_align": block_align, "bits_per_sample": bits_per_sample,
                    "subChunkID_2": subChunkID_2, "subChunkSize_2": subChunkSize_2, "data": data}              
    else:
        raise ValueError('Wrong file name.')
    
def getData(file_path):
    wav = readWav(file_path)
    data = wav["data"]
    block_align = wav["block_align"]
    num_channels = wav["num_channels"]
    bits_per_sample = wav["bits_per_sample"]

    audio_normal = []
    audio_half = []
    for i in range(0, len(data), block_align):
        sample = []
        for j in range(num_channels):
            sample.append(2**(32 - bits_per_sample) * int.from_bytes(data[i+j*block_align//num_channels:i+(j+1)*block_align//num_channels], byteorder='little', signed=True))
        audio_normal.append(sample)
        audio_half.append(sample)
        audio_half.append(sample)
    wav["dataNormal"] = np.array(audio_normal, dtype=np.int32) 
    wav["dataHalf"] = np.array(audio_half, dtype=np.int32)

    audio_double = []
    for i in range(0, len(audio_normal)-1, 2):
        sample = []
        for j in range(num_channels):
            sample.append(int((audio_normal[i][j] + audio_normal[i+1][j])/2))
        audio_double.append(sample)
    wav["dataDouble"] = np.array(audio_double, dtype=np.int32)

    return wav

def getStream(wav):
    num_channels = wav["num_channels"]
    sample_rate = wav["sample_rate"]
    try:
        return p.open(format=pyaudio.paInt32,
        channels=num_channels,
        rate=sample_rate,
        output=True)
    except OSError:
        sys.exit(0)

def playSound(file_path, speed=1, volume=1, start=0):
    # or unpause
    wav = getData(file_path)
    getPyAudio()
    global stream
    stream = getStream(wav)

    sample_rate = wav["sample_rate"]
    if speed == 1:
        dataNormal = wav["dataNormal"]
        data = np.multiply(dataNormal, volume).astype(np.int32)
        data = data[int(start * sample_rate):]
    elif speed == 2:
        dataDouble = wav["dataDouble"]
        data = np.multiply(dataDouble, volume).astype(np.int32)
        data = data[int(start * int(sample_rate//2)):]
    elif speed == 0.5:
        dataHalf = wav["dataHalf"]
        data = np.multiply(dataHalf, volume).astype(np.int32)
        data = data[int(start * sample_rate * 2):]
    else:
        raise ValueError('Invalid speed.')
        
    stream.write(data.astype(np.int32).tobytes())

def pause():
    stream.stop_stream()

def stop():
    stream.stop_stream()
    stream.close()
    stop()

def visualize(file_path):
    wav = getData(file_path, speed=1)
    dataArray = wav["dataNormal"]
    sample_rate = wav["sample_rate"]
    amplitude = np.max(dataArray, axis=1)
    time = len(amplitude) // sample_rate
    plt.figure(figsize=(10,5))
    plt.plot(np.linspace(0, time, num=len(amplitude)), amplitude, color='royalblue')
    plt.axis('off')
    plt.savefig('plot.png')

if __name__ == "__main__":
    speed = 1
    volume = 2
    start = 2
    playSound("exampleMono.wav", speed, volume, start)
