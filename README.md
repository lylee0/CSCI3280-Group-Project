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

Sound Playback (playback.py):<br>
1. Select a recording file:<br>
1.1 Call getPyAudio()<br>
1.2 Define initial value of speed and volume<br>
1.3 Define a class: voice = sound(file_path, speed, volume)<br>
1.4 Call voice.visualize() # plot.png is saved, which is the waveform of audio<br>
2. Play:<br>
2.1 Call voice.playSound(speed, volume)<br>
3. Pause:<br>
3.1 Call voice.pause()<br>
4. Unpause:<br>
4.1 Call voice.playSound(speed, volume)<br>
5. Change Volume:<br>
5.1 Change value of volume # volume can be in range 0.01 to 3, default is 1<br>
5.2 Call voice.playSound(speed, volume) # volume is the input<br>
6. Change Speed (2x):<br>
6.1 speed = 2<br>
6.2 Call voice.playSound(speed=2, volume)<br>
7. Change Speed (0.5x):<br>
7.1 speed = 0.5<br>
7.2 Call voice.playSound(speed=0.5, volume)<br>
8. Replay:<br>
8.1 Call voice.replay(speed, volume) # get current speed and volume now<br>
9. When end:<br>
9.1 Call voice.stop()<br>
9.2 Call stop()<br>
