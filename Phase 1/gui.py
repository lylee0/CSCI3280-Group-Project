from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
from qtrangeslider import QRangeSlider
import sys
import os
import showDevice
from PIL import ImageTk, Image
import os
from threading import Thread
import playback
import soundRecording
import noiseReduction
import speechToTextLib
import audio_trim
import datetime
import time
import audio_equalizer
import pitch_adjust

global input_device, volume, speed, start, end, selected_file, edit_frames, stop_thread, number_of_channel
input_device = 1
volume = 1
speed = 1
start = 0
selected_file = None
number_of_channel = 1

recordingDirectory = "recordings"

class AudioTrimWindow(QWidget):
    def __init__(self, end):
        super().__init__()

        self.setWindowTitle("Edit")
        self.setFixedSize(700, 500)

        self.end = end
        self.speed = 1
        self.volume = 1

        self.start_label = QLabel()
        self.end_label = QLabel()
        
        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.volumeSlider = QSlider(Qt.Horizontal)

        self.initUI()
        

    def initUI(self):

        layout = QVBoxLayout()

        #Label
        audioTrimLabel = QLabel()
        audioTrimLabel.setText("Audio Trim")
        audioTrimLabel.setStyleSheet("QLabel{font-size: 18pt;}")

        layout.addWidget(audioTrimLabel)

        #range slider
        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.rangeSlider.setMinimum(0)
        self.rangeSlider.setMaximum(int(self.end*100))

        print(self.end)
        
        self.rangeSlider.setValue([0, int(self.end*100)])
        self.rangeSlider.valueChanged.connect(self.value_changed)

        layout.addWidget(self.rangeSlider)

        #time text
        time_text_layout = QHBoxLayout()

        self.start_label = QLabel()
        self.start_label.setText("00:00:00.00")
        self.start_label.setStyleSheet("QLabel{font-size: 10pt;}")

        time_text_layout.addWidget(self.start_label)

        self.end_label = QLabel()
        end_hour = int(self.end / 3600)
        end_minute = int((self.end - end_hour * 3600) / 60)
        end_second = int((self.end - end_hour % 3600) % 60)
        end_ms = int(((self.end - end_hour * 3600) % 60 - end_second) *100)
        self.end_label.setText(f"{end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")
        self.end_label.setStyleSheet("QLabel{font-size: 10pt;}")
        self.end_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        time_text_layout.addWidget(self.end_label)

        layout.addLayout(time_text_layout)

        #audio speed choice
        audioSpeedChoice = QComboBox()
        audioSpeedChoice.setStyleSheet("QComboBox{font-size: 12pt;}")

        audioSpeedChoice.addItem("0.5x")
        audioSpeedChoice.addItem("1x")
        audioSpeedChoice.addItem("2x")

        audioSpeedChoice.setCurrentIndex(1)
        audioSpeedChoice.currentIndexChanged.connect(self.speed_change)
        
        layout.addWidget(audioSpeedChoice)

        #volume 
        volumeLayout = QHBoxLayout()

        #volume text
        volumeText = QLabel()
        volumeText.setText("Volume: ")

        volumeLayout.addWidget(volumeText)

        #volume slider
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(5)
        self.volumeSlider.setMaximum(20)
        self.volumeSlider.setValue(10)
        self.volumeSlider.setSliderPosition(10)
        self.volumeSlider.update()
        self.volumeSlider.repaint()
        self.volumeSlider.valueChanged.connect(self.volume_slider_move)

        volumeLayout.addWidget(self.volumeSlider)

        layout.addLayout(volumeLayout)


        #save button
        saveButton = QPushButton()
        saveButton.setText("Save")
        saveButton.clicked.connect(self.save_button_function)

        layout.addWidget(saveButton)


        self.setLayout(layout)

    def value_changed(self):
        current_hour = int(self.rangeSlider.value()[0] / 360000)
        current_minute = int((self.rangeSlider.value()[0] - current_hour * 360000) / 6000)
        current_second = int((self.rangeSlider.value()[0] - current_hour * 360000) % 6000) // 100
        current_ms = int(int((self.rangeSlider.value()[0] - current_hour * 360000) % 6000) % 100)
        current_end_hour = int(self.rangeSlider.value()[1] / 360000)
        current_end_minute = int((self.rangeSlider.value()[1] - current_hour * 360000) / 6000)
        current_end_second = int((self.rangeSlider.value()[1] - current_hour * 360000) % 6000) // 100
        current_end_ms = int(int((self.rangeSlider.value()[1] - current_hour * 360000) % 6000)%100)
        self.start_label.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}.{current_ms:02d}")
        self.end_label.setText(f"{current_end_hour:02d}:{current_end_minute:02d}:{current_end_second:02d}.{current_end_ms:02d}")
    
    def speed_change(self, speed_index):
        if speed_index == 0:
            self.speed = 0.5
        elif speed_index == 2:
            self.speed = 2
        else:
            self.speed = 1

    def volume_slider_move(self):
        currentVolume = self.volumeSlider.value()
        self.volume = currentVolume / 10

    def save_button_function(self):
        global wav, selected_file
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fileName = selected_file.split('.')[0]
        displayFileName = fileName.split('/')[1]
        start = self.rangeSlider.value()[0]/100
        end = self.rangeSlider.value()[1]/100
        trim_audio = audio_trim.edit(wav, start, end, self.speed, self.volume)
        soundRecording.fileWriting(trim_audio, wav["num_channels"], wav["sample_rate"], f"{fileName}_{current_time}_trim.wav")
        w.recordingContent.addItem(f"{displayFileName}_{current_time}_trim.wav")
        popup_message = QMessageBox()
        popup_message.setText("file save")
        popup_message.exec_()

class PitchAdjustWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pitch Adjust")
        self.setFixedSize(700, 500)

        self.slider = QSlider()

        #self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.initUI()
        
    def initUI(self):

        layout = QVBoxLayout()

        #Label
        pitchAdjustLabel = QLabel()
        pitchAdjustLabel.setText("Pitch Adjust")
        pitchAdjustLabel.setStyleSheet("QLabel{font-size: 18pt;}")

        layout.addWidget(pitchAdjustLabel)


        #pitch slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(-12)
        self.slider.setMaximum(12)
        self.slider.setToolTip("Current value: " + str(self.slider.value()))
        self.slider.valueChanged.connect(self.value_changed)

        layout.addWidget(self.slider)


        #pitch text
        pitch_text_layout = QHBoxLayout()

        start_label = QLabel()
        start_label.setText("-12")
        start_label.setStyleSheet("QLabel{font-size: 10pt;}")

        pitch_text_layout.addWidget(start_label)

        end_label = QLabel()
        end_label.setText("12")
        end_label.setStyleSheet("QLabel{font-size: 10pt;}")
        end_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        pitch_text_layout.addWidget(end_label)

        layout.addLayout(pitch_text_layout)


        #save button
        saveButton = QPushButton()
        saveButton.setText("Save")
        saveButton.clicked.connect(self.save_button_function)

        layout.addWidget(saveButton)










        self.setLayout(layout)

    def value_changed(self):
        self.slider.setToolTip("Current value: " + str(self.slider.value()))
    
    def save_button_function(self):
        global selected_file
        #start = self.rangeSlider.value()[0]
        #end = self.rangeSlider.value()[1]
        fileName = selected_file.split('.')[0]
        displayFileName = fileName.split('/')[1]
        shift = self.slider.value()
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pitch_adjust.pitch_shift(selected_file, shift, f"{fileName}_{current_time}_pitch_{shift}.wav")
        w.recordingContent.addItem(f"{displayFileName}_{current_time}_pitch_{shift}.wav")
        popup_message = QMessageBox()
        popup_message.setText("file save")
        popup_message.exec_()
        #audio_trim.edit(wav, shift)

class OverWriteWindow(QWidget):
    def __init__(self, end):
        super().__init__()

        self.setWindowTitle("Overwrite")
        self.setFixedSize(700, 500)
        self.end = end
        self.input_device = 1

        self.rangeSlider = QRangeSlider(Qt.Horizontal)

        
        self.start_label = QLabel()
        self.end_label = QLabel()

        self.recording = 0
        self.recordingButton = QPushButton()

        self.initUI()
        
    def initUI(self):

        layout = QVBoxLayout()

        #Label
        overwriteLabel = QLabel()
        overwriteLabel.setText("Overwrite")
        overwriteLabel.setStyleSheet("QLabel{font-size: 18pt;}")

        layout.addWidget(overwriteLabel)

        #range slider
        self.rangeSlider = QRangeSlider(Qt.Horizontal)
        self.rangeSlider.setMinimum(0)
        self.rangeSlider.setMaximum(int(self.end*100))
        
        self.rangeSlider.setValue([0, int(self.end*100)])
        self.rangeSlider.valueChanged.connect(self.value_changed)

        layout.addWidget(self.rangeSlider)

        #time text
        time_text_layout = QHBoxLayout()

        self.start_label = QLabel()
        self.start_label.setText("00:00:00.00")
        self.start_label.setStyleSheet("QLabel{font-size: 10pt;}")

        time_text_layout.addWidget(self.start_label)

        self.end_label = QLabel()
        end_hour = int(self.end / 3600)
        end_minute = int((self.end - end_hour * 3600) / 60)
        end_second = int((self.end - end_hour % 3600) % 60)
        end_ms = int(((self.end - end_hour * 3600) % 60 - end_second) *100)
        self.end_label.setText(f"{end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")
        self.end_label.setStyleSheet("QLabel{font-size: 10pt;}")
        self.end_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        time_text_layout.addWidget(self.end_label)

        layout.addLayout(time_text_layout)

        #device choice
        deviceChoices = QComboBox()
        deviceChoices.setStyleSheet("QComboBox{font-size: 12pt;}")

        deviceList = showDevice.getDeviceList()
        for device in deviceList:
            deviceChoices.addItem(device[1])

        deviceChoices.setCurrentIndex(input_device)
        deviceChoices.currentIndexChanged.connect(self.device_change)

        layout.addWidget(deviceChoices)

        #recording button
        self.recordingButton = QPushButton()
        self.recordingButton.setText("Recording")
        self.recordingButton.clicked.connect(self.record_audio)

        layout.addWidget(self.recordingButton)

        #stop recording button
        stopRecordingButton = QPushButton()
        stopRecordingButton.setText("Stop")
        stopRecordingButton.clicked.connect(self.stop_record)

        layout.addWidget(stopRecordingButton)

        self.setLayout(layout)
    
    
    def value_changed(self):
        current_hour = int(self.rangeSlider.value()[0] / 360000)
        current_minute = int((self.rangeSlider.value()[0] - current_hour * 360000) / 6000)
        current_second = int((self.rangeSlider.value()[0] - current_hour * 360000) % 6000) // 100
        current_ms = int(int((self.rangeSlider.value()[0] - current_hour * 360000) % 6000) % 100)
        current_end_hour = int(self.rangeSlider.value()[1] / 360000)
        current_end_minute = int((self.rangeSlider.value()[1] - current_hour * 360000) / 6000)
        current_end_second = int((self.rangeSlider.value()[1] - current_hour * 360000) % 6000) // 100
        current_end_ms = int(int((self.rangeSlider.value()[1] - current_hour * 360000) % 6000)%100)
        self.start_label.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}.{current_ms:02d}")
        self.end_label.setText(f"{current_end_hour:02d}:{current_end_minute:02d}:{current_end_second:02d}.{current_end_ms:02d}")
    
    def device_change(self, device_index):
        self.input_device = device_index

    def record_audio(self):
        if self.recording == 0:
            self.recording = 1
            print("Recording audio")
            self.recordingButton.setText("Recording - Live")
            global streamObj, pObj, frames, input_device,wav
            streamObj, pObj = soundRecording.startRecording(44100, 1024, wav["num_channels"], self.input_device) #initiate, para = fs, chunk, channel
            frames = soundRecording.threadWriting(streamObj, 1024)
        else:
            popup_message = QMessageBox()
            popup_message.setText("You are recording already!")
            popup_message.exec_()

    
    def stop_record(self):
        if self.recording == 1:
            global selected_file
            selected_file_name = selected_file.split('.')[0]
            selected_file_name = selected_file_name.split('/')[1]
            self.recording = 0
            self.recordingButton.setText("Recording")
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/{selected_file_name}_{current_time}_overwrite.wav"
            displayFilename = f"{selected_file_name}_{current_time}_overwrite.wav"
            global streamObj, pObj, frames, wav
            start_record = self.rangeSlider.value()[0]/100
            end_record = self.rangeSlider.value()[1]/100
            soundRecording.stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
            new_frames = audio_trim.overwrite(wav, start_record, end_record, frames)
            soundRecording.fileWriting(new_frames, wav["num_channels"], wav["sample_rate"], filename)
            w.recordingContent.addItem(displayFilename)
            popup_message = QMessageBox()
            popup_message.setText("file save")
            popup_message.exec_()
        else:
            popup_message = QMessageBox()
            popup_message.setText("You have to start a recording first!")
            popup_message.exec_()

class EqualizerWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Equalizer")
        self.setFixedSize(700, 500)

        self.initUI()
        
    def initUI(self):

        layout = QVBoxLayout()

        #Label
        equalizerLabel = QLabel()
        equalizerLabel.setText("Equalizer")
        equalizerLabel.setStyleSheet("QLabel{font-size: 18pt;}")

        layout.addWidget(equalizerLabel)

        #low pass filter button
        lowPassFilterButton = QPushButton()
        lowPassFilterButton.setText("Low Pass Filter")

        lowPassFilterButton.clicked.connect(self.low_pass_filter_button_function)

        layout.addWidget(lowPassFilterButton)

        #high pass filter button

        highPassFilterButton = QPushButton()
        highPassFilterButton.setText("High Pass Filter")

        highPassFilterButton.clicked.connect(self.high_pass_filter_button_function)

        layout.addWidget(highPassFilterButton)



        self.setLayout(layout)

    def low_pass_filter_button_function(self):
        global selected_file
        fileName = selected_file.split('.')[0]
        displayFileName = fileName.split('/')[1]
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_equalizer.audioEqualizer(f'{selected_file}', 1, f"{fileName}_{current_time}_lowPass.wav")
        w.recordingContent.addItem(f"{displayFileName}_{current_time}_lowPass.wav")
        popup_message = QMessageBox()
        popup_message.setText("file save")
        popup_message.exec_()

    def high_pass_filter_button_function(self):
        global selected_file
        fileName = selected_file.split('.')[0]
        displayFileName = fileName.split('/')[1]
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_equalizer.audioEqualizer(f'{selected_file}', 2, f"{fileName}_{current_time}_highPass.wav")
        w.recordingContent.addItem(f"{displayFileName}_{current_time}_highPass.wav")
        popup_message = QMessageBox()
        popup_message.setText("file save")
        popup_message.exec_()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Recorder")
        self.showMaximized() 

        playback.getPyAudio()

        self.recordingContent = QListView()
        self.slider = QSlider(Qt.Horizontal)
        self.waveGraph = QLabel()
        self.audioTimeText = QLabel()
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.recordingButton = QPushButton()
        self.recording = 0

        self.audioTrimWindow = AudioTrimWindow(0)
        self.pitchAdjustWindow = PitchAdjustWindow()
        self.overWriteWindow = OverWriteWindow(0)
        self.equalizerWindow = EqualizerWindow()
        
        self.initUI()

    def initUI(self):
        # Main window settings
        self.setGeometry(100, 100, 800, 600)

        mainWidget = QWidget()
        mainLayout = QVBoxLayout()

        upperLayout = self.initUpperLayout()
        lowerLayout = self.initLowerLayout()
        mainLayout.addLayout(upperLayout)
        mainLayout.addLayout(lowerLayout)

        mainWidget.setLayout(mainLayout)

        self.setCentralWidget(mainWidget)
    
    def initUpperLayout(self):

        upperLayout = QHBoxLayout()

        #recording content scroll list
        recordingContentScrollList = self.initRecordingContentScrollList()
        upperLayout.addLayout(recordingContentScrollList)



        return upperLayout
    
    def initRecordingContentScrollList(self):

        recordingScrollList = QHBoxLayout()

        #recording content
        self.recordingContent = QListWidget()
        self.recordingContent.resize(50, self.recordingContent.height())

        self.recordingContent.setGeometry(50, 70, 150, 80)

        self.update_recordingContent()
        self.recordingContent.currentItemChanged.connect(self.recording_selected)

        recordingScrollList.addWidget(self.recordingContent)

        #wave graph
        waveGraph = self.initWaveGraph()
        recordingScrollList.addLayout(waveGraph)

        return recordingScrollList

    def initWaveGraph(self):

        waveGraph = QVBoxLayout()

        #graph
        self.waveGraph = QLabel()
        pixmap = QPixmap("plot.png")
        self.waveGraph.setPixmap(pixmap)

        waveGraph.addWidget(self.waveGraph)

        #slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.valueChanged.connect(self.audio_slider_move)

        waveGraph.addWidget(self.slider)
        

        #volume 
        volumeLayout = QHBoxLayout()

        #volume text
        volumeText = QLabel()
        volumeText.setText("Volume: ")

        volumeLayout.addWidget(volumeText)

        #volume slider
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setMinimum(5)
        self.volumeSlider.setMaximum(20)
        self.volumeSlider.valueChanged.connect(self.volume_slider_move)

        volumeLayout.addWidget(self.volumeSlider)

        waveGraph.addLayout(volumeLayout)


        #function tools
        functionToolLayout = QHBoxLayout()


        #audio to text button
        audioToTextButton = QPushButton()
        audioToTextButton.setText("Audio To Text")
        audioToTextButton.clicked.connect(self.audio_to_text_button_function)

        functionToolLayout.addWidget(audioToTextButton)


        #audio trim button
        audioTrimButton = QPushButton()
        audioTrimButton.setText("Audio Trim")
        audioTrimButton.clicked.connect(self.audio_trim_button_function)

        functionToolLayout.addWidget(audioTrimButton)

        #pitch adjust button
        pitchAdjustButton = QPushButton()
        pitchAdjustButton.setText("Pitch Adjust")
        pitchAdjustButton.clicked.connect(self.pitch_adjust_button_function)

        functionToolLayout.addWidget(pitchAdjustButton)

        #overwrite button
        overwriteButton = QPushButton()
        overwriteButton.setText("Overwrite")
        overwriteButton.clicked.connect(self.ovewrite_button_function)

        functionToolLayout.addWidget(overwriteButton)
        
        #equalizer button
        equalizerButton = QPushButton()
        equalizerButton.setText("Equalizer")
        equalizerButton.clicked.connect(self.equalizer_button_function)

        functionToolLayout.addWidget(equalizerButton)

        #noise reduction button
        noiseReductionButton = QPushButton()
        noiseReductionButton.setText("Noise Reduction")
        noiseReductionButton.clicked.connect(self.noise_reduction_button_function)

        functionToolLayout.addWidget(noiseReductionButton)

        waveGraph.addLayout(functionToolLayout)

        return waveGraph
    
    def initLowerLayout(self):

        lowerLayout = QHBoxLayout()

        #channel choice
        channelChoices = QComboBox()
        channelChoices.setStyleSheet("QComboBox{font-size: 8pt;}")

        channelChoices.addItem("Mono Sound Recording")
        channelChoices.addItem("Stereo Sound Recording")

        channelChoices.setCurrentIndex(0)
        channelChoices.currentIndexChanged.connect(self.channel_change)
        
        lowerLayout.addWidget(channelChoices)

        #device choice
        deviceChoices = QComboBox()
        deviceChoices.setStyleSheet("QComboBox{font-size: 12pt;}")

        deviceList = showDevice.getDeviceList()
        for device in deviceList:
            deviceChoices.addItem(device[1])

        deviceChoices.setCurrentIndex(input_device)
        deviceChoices.currentIndexChanged.connect(self.device_change)

        lowerLayout.addWidget(deviceChoices)

        #recording button
        self.recordingButton = QPushButton()
        self.recordingButton.setText("Recording")
        self.recordingButton.setStyleSheet("background-color: rgb(144,238,144);")
        #self.recordingButton.clicked.connect(self.record_audio)
        self.recordingButton.clicked.connect(self.recording_function)

        lowerLayout.addWidget(self.recordingButton)

        #stop recording button
        #stopRecordingButton = QPushButton()
        #stopRecordingButton.setText("Stop")
        #stopRecordingButton.clicked.connect(self.stop_record)

        #lowerLayout.addWidget(stopRecordingButton)

        #audio time text
        self.audioTimeText = QLabel()
        self.audioTimeText.setStyleSheet("QLabel{font-size: 18pt;}")
        self.audioTimeText.setText("00:00:00 / 00:00:00")
        self.audioTimeText.setAlignment(Qt.AlignCenter)

        lowerLayout.addWidget(self.audioTimeText)

        #play button
        playButton = QPushButton()
        playButton.setText("Play")

        playButton.clicked.connect(self.play_audio)

        lowerLayout.addWidget(playButton)

        #pause button
        #pauseButton = QPushButton()
        #pauseButton.setText("Pause")

        #pauseButton.clicked.connect(self.pause_audio)

        #lowerLayout.addWidget(pauseButton)

        #audio speed choice
        audioSpeedChoice = QComboBox()
        audioSpeedChoice.setStyleSheet("QComboBox{font-size: 12pt;}")

        audioSpeedChoice.addItem("0.5x")
        audioSpeedChoice.addItem("1x")
        audioSpeedChoice.addItem("2x")

        audioSpeedChoice.setCurrentIndex(1)
        audioSpeedChoice.currentIndexChanged.connect(self.speed_change)
        
        lowerLayout.addWidget(audioSpeedChoice)
        
        return lowerLayout
    
    def get_wav_files(self):
        return [file for file in os.listdir(recordingDirectory) if file.endswith(".wav")]

    def update_recordingContent(self):
        self.recordingContent.clear()
        files = [file for file in os.listdir(recordingDirectory) if file.endswith(".wav")]
        for f in files:
            item = QListWidgetItem(f'{f}')
            self.recordingContent.addItem(item)
    
    def record_audio(self):
        if self.recording == 0:
            self.recording = 1
            self.recordingButton.setText("Recording - Live")
            self.recordingButton.setStyleSheet("background-color: rgb(144,238,144);")
            print("Recording audio")
            global streamObj, pObj, frames, input_device
            streamObj, pObj = soundRecording.startRecording(44100, 1024, number_of_channel, input_device) #initiate, para = fs, chunk, channel
            frames = soundRecording.threadWriting(streamObj, 1024)
        else:
            popup_message = QMessageBox()
            popup_message.setText("You are recording already!")
            popup_message.exec_()
    
    def stop_record(self):
        if self.recording == 1:
            self.recording = 0
            self.recordingButton.setText("Recording")
            self.recordingButton.setStyleSheet("")
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/record_{current_time}.wav"
            global streamObj, pObj, frames
            soundRecording.stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
            soundRecording.fileWriting(frames, number_of_channel, 44100, filename)
            self.recordingContent.addItem(f"record_{current_time}.wav")
        else:
            popup_message = QMessageBox()
            popup_message.setText("You have to start a recording first!")
            popup_message.exec_()

    def recording_function(self):
        global streamObj, pObj, frames, input_device
        if self.recording == 0:
            self.recording = 1
            self.recordingButton.setText("Stop")
            self.recordingButton.setStyleSheet("background-color: rgb(255,0,0);")
            print("Recording audio")
            
            streamObj, pObj = soundRecording.startRecording(44100, 1024, number_of_channel, input_device) #initiate, para = fs, chunk, channel
            frames = soundRecording.threadWriting(streamObj, 1024)
        else:
            self.recording = 0
            self.recordingButton.setText("Recording")
            self.recordingButton.setStyleSheet("background-color: rgb(144,238,144);")
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recordings/record_{current_time}.wav"
            soundRecording.stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
            soundRecording.fileWriting(frames, number_of_channel, 44100, filename)
            self.recordingContent.addItem(f"record_{current_time}.wav")


    def channel_change(self, channel_index):
        global number_of_channel
        if channel_index == 0:
            number_of_channel = 1
        else:
            number_of_channel = 2

    def speed_change(self, speed_index):
        global speed
        if speed_index == 0:
            speed = 0.5
        elif speed_index == 2:
            speed = 2
        else:
            speed = 1

    def device_change(self, device_index):
        global input_device
        input_device = device_index

    def recording_selected(self):
        global selected_file, end
        selected_file = f"recordings/{self.recordingContent.currentItem().text()}"
        if selected_file:
            global wav
            wav = playback.getData(selected_file)
            self.slider.setValue(0)
            value = wav["duration_float"]
            end = value
            self.slider.setMaximum(int(value * 100))
            self.slider.setSliderPosition(0)
            self.slider.update()
            self.slider.repaint()
            playback.visualize(wav)
            pixmap = QPixmap("plot.png")
            self.waveGraph.setPixmap(pixmap)
            end_hour = int(end / 3600)
            end_minute = int((end - end_hour * 3600) / 60)
            end_second = int((end - end_hour * 3600) % 60)
            end_ms = int(((end - end_hour * 3600) % 60 - end_second) *100)
            self.audioTimeText.setText(f"00:00:00.00 / {end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")
            print(selected_file)

    def play_audio(self):
        global selected_file, wav, volume, start, stream
        start = self.slider.value()/100
        #volume = volume_slider.get()
        print(f"Playing {selected_file}")
        stream = playback.getStream(wav)
        thread = Thread(target = self.slider_move)
        thread.start()
        playback.play(stream, wav, speed, volume, start)
        playback.stop(stream)
        #play = Thread(target = self.playAudio, args=(stream, wav, speed, volume, start))
        #play.start()


    #def playAudio(stream, wav, speed, volume, start):
        #playback.play(stream, wav, speed, volume, start)
        #playback.stop(stream)

    
    def slider_move(self):
        global end, stop_thread, speed
        stop_thread = False
        current_value = self.slider.value()
        current_hour = int(current_value / 360000)
        current_minute = int((current_value - current_hour * 360000) / 6000)
        current_second = int((current_value - current_hour * 360000) % 6000) // 100
        current_ms = int(((current_value - current_hour * 360000) % 6000) % 100)

        end_hour = int(end / 3600)
        end_minute = int((end - end_hour * 3600) / 60)
        end_second = int((end - end_hour % 3600) % 60)
        end_ms = int(((end - end_hour * 3600) % 60 - end_second) *100)
        self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}.{current_ms:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")
        while((current_value + 2)/100 < end):
            #print(f"{current_value} / {end}")
            time.sleep(0.02 / speed)
            current_value += 2
            self.slider.setValue(current_value)
            self.slider.setSliderPosition(current_value)
            self.slider.update()
            self.slider.repaint()
            current_hour = int(current_value / 360000)
            current_minute = int((current_value - current_hour * 360000) / 6000)
            current_second = int((current_value - current_hour * 360000) % 6000) // 100
            current_ms = int(((current_value - current_hour * 360000) % 6000) % 100)
            self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}.{current_ms:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")
            if stop_thread == True:
                return
        self.slider.setSliderPosition(0)

    def pause_audio(self):
        global stream, stop_thread
        stop_thread = True
        print("Pausing audio")
        playback.pause(stream)
        
    def audio_slider_move(self):
        global start, end
        current_value = self.slider.value()
        current_hour = int(current_value / 360000)
        current_minute = int((current_value - current_hour * 360000) / 6000)
        current_second = int((current_value - current_hour * 360000) % 6000) // 100
        current_ms = int(((current_value - current_hour * 360000) % 6000) % 100)

        end_hour = int(end / 3600)
        end_minute = int((end - end_hour * 3600) / 60)
        end_second = int((end - end_hour % 3600) % 60)
        end_ms = int(((end - end_hour * 3600) % 60 - end_second) *100)
        self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d}.{current_ms:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}.{end_ms:02d}")


    def volume_slider_move(self):
        global volume
        currentVolume = self.volumeSlider.value()
        volume = currentVolume / 10
    
    def audio_to_text_button_function(self):
        global selected_file
        text_content = speechToTextLib.speechToText(f"{selected_file}")
        popup_message = QMessageBox()
        popup_message.setText(text_content)
        popup_message.exec_()
        return
    
    def audio_trim_button_function(self, checked):
        global end
        self.audioTrimWindow = AudioTrimWindow(end = end)
        self.audioTrimWindow.show()

    def pitch_adjust_button_function(self, checked):
        self.pitchAdjustWindow = PitchAdjustWindow()
        self.pitchAdjustWindow.show()

    def ovewrite_button_function(self, checked):
        global end
        self.overWriteWindow = OverWriteWindow(end = end)
        self.overWriteWindow.show()

    def equalizer_button_function(self, checked):
        self.equalizerWindow = EqualizerWindow()
        self.equalizerWindow.show()

    def noise_reduction_button_function(self, checked):
        global selected_file
        fileName = selected_file.split('.')[0]
        displayFileName = fileName.split('/')[1]
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        noiseReduction.noiseReduction(selected_file, f"{fileName}_{current_time}_reduced_noise.wav")
        popup_message = QMessageBox()
        popup_message.setText(f"file save as {fileName}_{current_time}_reduced_noise.wav")
        popup_message.exec_()
        self.recordingContent.addItem(f"{displayFileName}_{current_time}_reduced_noise.wav")
            
       


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()
