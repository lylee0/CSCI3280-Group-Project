import struct
import numpy as np
from scipy.signal import butter, filtfilt

def musicEqualizer(wavfile):
    """
    Audio Effects: Low Pass Filter
    """
    with open(wavfile, "rb") as file_in:
        # Extract relevant information from the header
        chunk_id = file_in.read(4) #"RIFF"
        chunk_size = int.from_bytes(file_in.read(4), byteorder='little') #little, N+36
        format = file_in.read(4) #"WAVE"
        if (chunk_id != b'RIFF') or (format != b'WAVE'):
            raise ValueError('File is not in WAV format.')
        subChunkID_1 = file_in.read(4) #"fmt "
        subChunkSize_1 = int.from_bytes(file_in.read(4), byteorder='little') #little, 16
        audio_format = int.from_bytes(file_in.read(2), byteorder='little') #little, PCM
        if audio_format != 1:
            raise ValueError('File is not in PCM format.')
        num_channels = int.from_bytes(file_in.read(2), byteorder='little') #little
        sample_rate = int.from_bytes(file_in.read(4), byteorder='little') #little

        byte_rate = int.from_bytes(file_in.read(4), byteorder='little') #little
        block_align = int.from_bytes(file_in.read(2), byteorder='little') #little
        bits_per_sample = int.from_bytes(file_in.read(2), byteorder='little') #little
        subChunkID_2 = file_in.read(4) #"LIST", "data"
        if subChunkID_2 != b'data':
            raise ValueError('Invalid WAV file.')
        subChunkSize_2 = int.from_bytes(file_in.read(4), byteorder='little') #little
        data = file_in.read(subChunkSize_2) #little
        
        file_in.close()

    wav_audio = []
    for i in range(0, len(data), block_align):
        sample = []
        for j in range(num_channels):
            sample.append(int.from_bytes(data[i+j*block_align//2:i+(j+1)*block_align//2], byteorder='little', signed=True))
        wav_audio.append(sample)

    working = np.array(wav_audio, dtype=np.int32)
    working = np.divide(working, 2**(bits_per_sample-1)-1)

    tmp = np.empty((len(working[0]),len(working)))
    tmp[0] = [x[0] for x in working]

    if len(working[0]) == 2:
        tmp[1] = [x[1] for x in working]
    working = tmp

    # Low Pass Filter
    cutoff_freq = 40
    nyquist_freq = 0.5 * 1000 
    order = 10
    b, a = butter(order, cutoff_freq/nyquist_freq, btype='low')
    filtered_signal = filtfilt(b, a, working)

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

    with open('lptest.wav', "wb") as file_out:
        file_out.write(chunk_id)
        file_out.write(chunk_size)
        file_out.write(format)
        file_out.write(subChunkID_1)
        file_out.write(subChunkSize_1)
        file_out.write(audio_format)
        file_out.write(num_channels)
        file_out.write(sample_rate)
        file_out.write(byte_rate)
        file_out.write(block_align)
        file_out.write(bits_per_sample)
        file_out.write(subChunkID_2)
        file_out.write(subChunkSize_2)
        for i in range(len(filtered_signal[0])):
            for j in range(len(filtered_signal)):
                block = int(filtered_signal[j][i] * (2**31-1))
                block = struct.pack('<i', block)
                file_out.write(block)
        file_out.close()
    
musicEqualizer('Test Case/exampleMono.wav')