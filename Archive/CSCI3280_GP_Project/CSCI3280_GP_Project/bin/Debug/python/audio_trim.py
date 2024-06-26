import playback
import soundRecording
import numpy as np
import time

def edit(wav, start, end, speed, volume):
    # return frames to write
    sample_rate = wav["sample_rate"]
    if speed == 1:
        dataNormal = wav["dataNormal"]
        dataNormal = dataNormal[int(start * sample_rate):int(end * sample_rate)]
        dataNormal = np.multiply(dataNormal, volume).astype(np.int32)
        return [dataNormal.astype(np.int32).tobytes()]
    elif speed == 2:
        dataDouble = wav["dataDouble"]
        dataDouble = dataDouble[int(start * int(sample_rate//2)):int(end * int(sample_rate//2))]
        dataDouble = np.multiply(dataDouble, volume).astype(np.int32)
        return [dataDouble.astype(np.int32).tobytes()]
    elif speed == 0.5:
        dataHalf = wav["dataHalf"]
        dataHalf = dataHalf[int(start * sample_rate * 2):int(end * sample_rate * 2)]
        dataHalf = np.multiply(dataHalf, volume).astype(np.int32)
        return [dataHalf.astype(np.int32).tobytes()]
    else:
        raise ValueError('Invalid speed.')

def overwrite(wav, start_record, end_record, frames):
    sample_rate = wav["sample_rate"]
    block_align = wav["block_align"]
    dataNormal = wav["dataNormal"]
    num_channels = wav["num_channels"]
    bits_per_sample = wav["bits_per_sample"]
    dataNormal_1 = dataNormal[:int(start_record * sample_rate)]
    dataNormal_3 = dataNormal[int(end_record * sample_rate):]

    temp = b''.join(frames)
    frames=temp
    audio_normal = []
    for i in range(0, len(frames), num_channels * 4):
        sample = []
        for j in range(num_channels):
            sample.append(int.from_bytes(frames[i+j*4:i+(j+1)*4], byteorder='little', signed=True)) #Force 32-bit by recording mechanism
        audio_normal.append(sample)
    dataNormal_2 = np.array(audio_normal, dtype=np.int32) 
    dataArray = np.concatenate((dataNormal_1, dataNormal_2), axis=0)
    dataArray = np.concatenate((dataArray, dataNormal_3), axis=0)
    return [dataArray.astype(np.int32).tobytes()]

if __name__ == "__main__":
    #wav = playback.getData("Raw Test Data/32bitM.wav")
    #frames = edit(wav, 0, 2, 2, 0.5)
    #soundRecording.fileWriting(frames, wav["num_channels"], wav["sample_rate"], 'Test Case/BASIC - Test for audio editing/32bitM_s2v0.5.wav')

    '''# call startRecording
    streamObj, pObj = soundRecording.startRecording(44100, 1024, 2, 1)
    # call threadWriting, get frames
    new_record = soundRecording.threadWriting(streamObj, 1024)
    time.sleep(5)
    # call stopRecording
    soundRecording.stopRecording(streamObj, pObj)'''
    # call record, get frames
    # call overwrite to concatenate
    # call fileWriting to write file
    wav = playback.getData("Raw Test Data/32bitS.wav")
    frames = overwrite(wav, 1, 2, new_record)
    soundRecording.fileWriting(frames, wav["num_channels"], wav["sample_rate"], 'Test Case/BASIC - Test for audio trimming/32bitS.wav') #the path should be equal to the original name
