# CSCI3280-Group-Project
Peer-to-Peer Voice Chat System

Library required (plz add the list if new library used):
struct
numpy
noisereduce
pyaudio
sys
speech_recognition
time
threading
wave

Sound Recording (soundRecording.py):
1. When press "Record":
1.1. Call startRecording(fs, chunk, channel, device index), get two return object [streamObj, pObj]
1.2. Call threadWriting(streamObj, chunk), get raw audio data (streamObj from 1.1's output)
2. When press "Stop recording":
2.1. Call stopRecording(streamObj, pObj) (both from 1.1's output)
2.2. Call fileWriting(data, channel, fs, file path) (data from 1.2.'s output)

Get device index (showDevice.py):
1. Call getDeviceList() (Will return index & name)

Noise Reduction (noiseReduction.py):
1. Call noiseReduction(input path, output path, fs)

Sound Playback (playback.py):<br>
1. Select a recording file:<br>
1.1 Call wav = getData(file_path)<br>
1.2 Define initial value of speed, volume, and start # start is the start time in second<br>
1.4 Call visualize(wav) # plot.png is saved, which is the waveform of audio<br>
2. Play Sound:<br>
2.1 Call playSound(wav, speed, volume, start)<br>
3. Pause:<br>
3.1 Call pause()<br>
4. Unpause:<br>
4.1 Call playSound(wav, speed, volume, start)<br>
5. Change Volume:<br>
5.1 Change value of volume # volume can be in range 0.01 to 3, default is 1<br>
5.2 Call playSound(wav, speed, volume, start) # volume is the input<br>
6. Change Speed (2x):<br>
6.1 speed = 2<br>
6.2 Call playSound(wav, speed, volume, start)<br>
7. Change Speed (0.5x):<br>
7.1 speed = 0.5<br>
7.2 Call playSound(wav, speed, volume, start)<br>
8. Replay:<br>
8.1 Call vplaySound(wav, speed, volume, start) # get current speed and volume<br>
9. Replay from another time<br>
9.1 Change value of start (in second)<br>
9.2 Call playSound(wav, speed, volume, start)<br>
9. When end:<br>
9.1 Call stop()<br>
10.2 pause()<br>
10.3 stop()<br>
10.4 visualize(file_path)<br>

Audio Trim(audio-edit.py):
1. Drag 2 sliders to the desired start time(s) and end time(s) and press Trim button:<br>
Call audio_trim(input_file, start_time, end_time), return trimmed audio file
