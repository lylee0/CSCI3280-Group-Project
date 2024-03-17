
import pyaudio
import asyncio
import websockets
import numpy as np
import cv2
import pyautogui
import pygetwindow as gw
import threading
import time
import datetime
import struct
import sys
from pydub import AudioSegment

# record
# pause
# stop
# share screen
# file accessible for all users
# mp4 m4a
# record screen and audio separately, combine when stop
# file name
# record voices of each users separately???then combine it 
# how about mute?????
# host address
# port number

def record(channel, fs):
    # keep get users'stream
    pass

def pause(): # can be skipped
    pass

def stop():
    # get stream through record
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"audio_{current_time}.wav"
    frames = mergeAudio(streams, channel, fs, bits_per_sample)
    fileWriting(frames, channel, fs, audio_filename)
    vidio_filename = f"video_{current_time}.mp4"
    pass

def mergeAudio(streams, channel, fs, bits_per_sample):
    # suppose streams is a list of all users'stream
    #streams_array = toNumpyArray(streams, )
    #frames = []
    #for i in range(channel):
    frames_channel = streams[len(streams)-1]
    #frames_channel = streams_array[len(streams_array)-1]
    #frames_channel = frames_channel.astype(np.int32).tobytes()
    for j in range(len(streams)-1):
        stream1_audio = AudioSegment(data=frames_channel, sample_width=bits_per_sample, frame_rate=fs, channels=channel) # to be fixed?

        stream2_audio = AudioSegment(data=streams[j], sample_width=bits_per_sample, frame_rate=fs, channels=channel)

        frames_channel = stream1_audio.overlay(stream2_audio)
        frames_channel = frames_channel.raw_data
    #frames = np.vstack(streams_array)
    #frames_channel = frames_channel.astype(np.int32).tobytes()
    #frames.append(frames_channel)

    # Save the mixed audio to a file
    #frames_channel.export("mixed_audio.wav", format="wav")
    #frames = [frame.astype(np.int32).tobytes() for frame in frames]
    return frames_channel

def toNumpyArray(streams, block_align, num_channels, bits_per_sample):
    frames = []
    for data in streams:
        audio_normal = []
        for i in range(0, len(data), block_align):
            sample = []
            for j in range(num_channels):
                sample.append(2**(32 - bits_per_sample) * int.from_bytes(data[i+j*block_align//num_channels:i+(j+1)*block_align//num_channels], byteorder='little', signed=True))
            audio_normal.append(sample)
        frames.append(np.array(audio_normal, dtype=np.int32))
    return frames

def writingData(streamObj, chunk, frames):
    while streamObj.is_active():
        data = streamObj.read(chunk)
        frames.append(data)

def stopRecording(streamObjs, pObjs):
    streamObjs.stop_stream()
    streamObjs.close()
    time.sleep(1) #allow data file to finish writing
    pObjs.terminate()

def threadWriting(streamObjs, chunks):
    frames = []
    w = threading.Thread(target=writingData, args=(streamObjs, chunks, frames))
    w.start()
    return frames

def fileWriting(frames, channel, fs, outPath):
    length = 0
    for i in range(0,len(frames)):
        length += len(frames[i])
    
    #header chunk
    masterFormat = struct.pack('>4s',"RIFF".encode('utf-8'))
    chunkSize = struct.pack('<I', length + 4 + 24 + 8)
    waveFormat = struct.pack('>4s',"WAVE".encode('utf-8'))

    #format chunk
    formatChunk = struct.pack('>4s',"fmt ".encode('utf-8'))
    formatChunkSize = struct.pack('<I', 16)
    audioFormat = struct.pack('<H', 1)
    channelNumber = struct.pack('<H', channel)
    fsRate = struct.pack('<I', fs)
    byteRate = struct.pack('<I', fs * channel * 4) #2 represent 32-bit rate
    blockAlign = struct.pack('<H', channel * 4) #2 represent 32-bit rate
    bitPerSample = struct.pack('<H', 32)

    #data chunk
    dataChunk = struct.pack('>4s', "data".encode('utf-8'))
    dataChunkSize = struct.pack('<I', length)

    with open(outPath,'wb') as output:
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
        for i in range(0,len(frames)):
            output.write(frames[i])
