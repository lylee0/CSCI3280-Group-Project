# CSCI3280-Group-Project
Peer-to-Peer Voice Chat System

Sound Recording (soundRecording.py):
1. When press "Record":
1.1. Call startRecording(fs, chunk, channel, device index), get two return object [streamObj, pObj]
1.2. Call threadWriting(streamObj, chunk), get raw audio data (streamObj from 1.1's output)
2. When press "Stop recording":
2.1. Call stopRecording(streamObj, pObj) (both from 1.1's output)
2.2. Call fileWriting(data, channel, fs, file path) (data from 1.2.'s output)

Get device index (showDevice.py):
1. Call getDeviceList() (Will return index & name)

Sound Playback (playback.py):
1. Select a recording file:
1.1 Call getPyAudio()
1.2 Define a class: voice = sound(file_path)
2. Play:
2.1 Call voice.playSound()
3. Pause:
3.1 Call voice.pause()
4 Unpause:
4.1 Call voice.playSound()
5. Change Volume:
5.1 Call voice.playSound(volume=volume) # volume is the input
6. Change Speed (2x):
6.1 Call voice.playSound(speed=2)
7. Change Speed (0.5x):
7.1 Call voice.playSound(speed=0.5)
8. Replay:
8.1 Call voice.replay(speed, volume) # get current speed and volume now
9. When end:
9.1 Call voice.stop()
9.2 Call stop()
