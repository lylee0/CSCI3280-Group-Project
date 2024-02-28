import pyaudio
import threading
import time
import struct

def startRecording(fs, chunk, channels, deviceIndex):
    sample_format = pyaudio.paInt32

    p = pyaudio.PyAudio()

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input_device_index = deviceIndex,
                    input=True)
    
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

    return stream, p

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

if __name__ == "__main__":
    # Set 1 when press play button
    streamObj, pObj = startRecording(44100, 1024, 2, 1) #initiate, para = fs, chunk, channel
    frames = threadWriting(streamObj, 1024) #keep writing, para = stream object, chunk
    # End of set 1
    time.sleep(5)
    # Set 2 when press stop button
    stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
    fileWriting(frames, 2, 44100, 'Test Case/BASIC - Test for sound recording/32bitS.wav') #rewrite the data file to wav-capable, para = raw audio data, channel, fs, output path
    # End of Set 2
