# CSCI3280-Group-Project
Peer-to-Peer Voice Chat System

0. Library required:<br>
struct<br>
numpy<br>
noisereduce<br>
pyaudio<br>
sys<br>
speech_recognition<br>
time<br>
threading<br>
scipy<br>
pyqt5<br>
qtrangeslider<br>
os<br>
PIL<br>
datetime<br>
time<br>
librosa<br>
matplotlib<br>

1. Unzip CSCI3280Group7ProjectCode_1.zip

2. Run gui.py

3. Use the sound recorder

Function available:
1. Sound recording [ Parameter: Number of channels | Input device ]
2. Sound playback [ Parameter: Starting position | Volume | Speed ]
3. Audio to text
4. Audio trim [ Parameter: Starting position | Ending position | Volume | Speed ]
5. Audio overwrite [ Parameter: Starting position | Ending position | Volumn of new recording | Speed of new recording ]
6. Audio equalizer [ Parameter: High pass or Low pass ]
7. Noise reduction 
8. Visualization


-------------------------------------------------------------------------------------------------------------------------
Seperate python file description:

Sound Recording (soundRecording.py):
1. When press "Record":<br>
1.1. Call startRecording(fs, chunk, channel, device index), get two return object [streamObj, pObj]<br>
1.2. Call threadWriting(streamObj, chunk), get raw audio data (streamObj from 1.1's output)<br>
2. When press "Stop recording":
2.1. Call stopRecording(streamObj, pObj) (both from 1.1's output)<br>
2.2. Call fileWriting(data, channel, fs, file path) (data from 1.2.'s output)<br>

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
3. Change Volume:<br>
3.1 Change value of volume # volume can be in range 0.5 to 2, default is 1<br>
3.2 Call playSound(wav, speed, volume, start) # volume is the input<br>
4. Change Speed (2x):<br>
4.1 speed = 2<br>
4.2 Call playSound(wav, speed, volume, start)<br>
5. Change Speed (0.5x):<br>
5.1 speed = 0.5<br>
5.2 Call playSound(wav, speed, volume, start)<br>
6. Replay:<br>
6.1 Call vplaySound(wav, speed, volume, start) # get current speed and volume<br>
7. Replay from another time<br>
7.1 Change value of start (in second)<br>
7.2 Call playSound(wav, speed, volume, start)<br>

Audio Trim (audio_trim.py):
1. edit(wav, start, end, speed, volume) # default: start=0, end=duration, speed=1, volume=1
2. overwrite(wav, start_record, end_record, frames) # frames is the newly recorded audio
3. There should be a 2-end slider controlling the start time and end time
4. When doing overwrite, the record sample_rate and num_channels should be aligned with the selected file

Adjust Pitch (pitch_adjust.py): # input -12 to 12, default 0
1. A seekbar with slider or a input box can be used to get the desired adjustment from users
2. Press 'Adjust' button

Audio Effect (audio_equalizer.py): # input 1 for low pass filter or 2 for high pass filter
1. Make buttons for each types of effects
2. Users then click 'Apply' button, pass the type of filter
