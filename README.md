# CSCI3280-Group-Project
Peer-to-Peer Voice Chat System

Sound Recording (soundRecording.py):
1. When press "Record":
1.1. Call startRecording(fs, chunk, channel, device index), get two return object [streamObj, pObj]
1.2. Call threadWriting(streamObj, chunk) (streamObj from 1.1's output)
2. When press "Step recording":
2.1. Call stopRecording(streamObj, pObj) (both from 1.1's output)
2.2. Call fileWriting(fs, channel, fs, file path)

Get device index (showDevice.py):
1. Call getDeviceList() (Will return index & name)