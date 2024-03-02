import speech_recognition as sr
import numpy as np
import struct

def speechToText(path):  
    r = sr.Recognizer()  
    with open(path, "rb") as recording:
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
        org_num = num_channels
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
    if bits_per_sample != 32 or num_channels != 1:
        audio = []
        for i in range(0, len(data), block_align):
            sample = []
            for j in range(num_channels):
                sample.append(int.from_bytes(data[i+j*block_align//num_channels:i+(j+1)*block_align//num_channels], byteorder='little', signed=True))
            audio.append(sample)
        working = np.array(audio, dtype=np.int32) 
        working = np.divide(working, 2**(bits_per_sample-1)-1)
        tempWork = np.empty((len(working[0]),len(working)))
        tempWork[0] = [x[0] for x in working]
        if len(working[0]) == 2:
            tempWork[1] = [x[1] for x in working] 
        
        if num_channels == 1:
            #header chunk
            chunk_size = struct.pack('<I', chunk_size + subChunkSize_2*(32//bits_per_sample-1))

            #format chunk
            subChunkSize_1 = struct.pack('<I', subChunkSize_1)
            audio_format = struct.pack('<H', audio_format)
            num_channels = struct.pack('<H', num_channels)
            sample_rate = struct.pack('<I', sample_rate)
            byte_rate = struct.pack('<I', byte_rate*32//bits_per_sample) 
            block_align = struct.pack('<H', block_align*32//bits_per_sample)

            #data chunk
            subChunkSize_2 = struct.pack('<I', subChunkSize_2*32//bits_per_sample)
            
            bits_per_sample = struct.pack('<H', 32)

            with open(path[:-4] + "_temp.wav", "wb") as recording:
                recording.write(chunk_id)
                recording.write(chunk_size)
                recording.write(format)
                recording.write(subChunkID_1)
                recording.write(subChunkSize_1)
                recording.write(audio_format)
                recording.write(num_channels)
                recording.write(sample_rate)
                recording.write(byte_rate)
                recording.write(block_align)
                recording.write(bits_per_sample)
                recording.write(subChunkID_2)
                recording.write(subChunkSize_2)
                for i in range(len(tempWork[0])):
                    for j in range(len(tempWork)):
                        block = int(tempWork[j][i] * (2**31-1))
                        block = struct.pack('<i', block)
                        recording.write(block)                                
            audio = sr.AudioFile(path[:-4] + "_temp.wav")
        else: 
            #header chunk
            chunk_size = struct.pack('<I', chunk_size + subChunkSize_2*(32//bits_per_sample-1)//2)

            #format chunk
            subChunkSize_1 = struct.pack('<I', subChunkSize_1)
            audio_format = struct.pack('<H', audio_format)
            num_channels = struct.pack('<H', num_channels//2)
            sample_rate = struct.pack('<I', sample_rate)
            byte_rate = struct.pack('<I', byte_rate*32//bits_per_sample//2) 
            block_align = struct.pack('<H', block_align*32//bits_per_sample//2)

            #data chunk
            subChunkSize_2 = struct.pack('<I', subChunkSize_2*32//bits_per_sample//2)
            
            bits_per_sample = struct.pack('<H', 32)

            with open(path[:-4] + "_temp1.wav", "wb") as recording1:
                with open(path[:-4] + "_temp2.wav", "wb") as recording2:
                    recording1.write(chunk_id)
                    recording1.write(chunk_size)
                    recording1.write(format)
                    recording1.write(subChunkID_1)
                    recording1.write(subChunkSize_1)
                    recording1.write(audio_format)
                    recording1.write(num_channels)
                    recording1.write(sample_rate)
                    recording1.write(byte_rate)
                    recording1.write(block_align)
                    recording1.write(bits_per_sample)
                    recording1.write(subChunkID_2)
                    recording1.write(subChunkSize_2)
                    recording2.write(chunk_id)
                    recording2.write(chunk_size)
                    recording2.write(format)
                    recording2.write(subChunkID_1)
                    recording2.write(subChunkSize_1)
                    recording2.write(audio_format)
                    recording2.write(num_channels)
                    recording2.write(sample_rate)
                    recording2.write(byte_rate)
                    recording2.write(block_align)
                    recording2.write(bits_per_sample)
                    recording2.write(subChunkID_2)
                    recording2.write(subChunkSize_2)
                    for i in range(len(tempWork[0])):
                        block = int(tempWork[0][i] * (2**31-1))
                        block = struct.pack('<i', block)
                        recording1.write(block)
                    for j in range(len(tempWork[1])):
                        block = int(tempWork[1][j] * (2**31-1))
                        block = struct.pack('<i', block)
                        recording2.write(block)                                  
            audio = sr.AudioFile(path[:-4] + "_temp1.wav")                     
            audio2 = sr.AudioFile(path[:-4] + "_temp2.wav")
    else:                                           
        audio = sr.AudioFile(path)
    with audio as source:
        audio = r.record(source)         
        result = r.recognize_google(audio)
    if org_num == 2:
        with audio2 as source2:
            audio2 = r.record(source2)         
            result2 = r.recognize_google(audio2)
        return "Channel 1: " + result + "; Channel 2: " + result2
    return result

if __name__ == "__main__":
    print(speechToText('Raw Test Data/16bitS.wav'))