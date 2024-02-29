from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
import sys
import os
import showDevice
from PIL import ImageTk, Image
import os
import threading
import playback
import soundRecording
import noiseReduction
import speechToTextLib
import audio_trim
import datetime

global input_device, volume, speed, start, end, selected_file, edit_frames
input_device = 1
volume = 1
speed = 1
start = 0
selected_file = None

recordingDirectory = "recordings"

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Recorder")
        self.setFixedSize(1600, 900)

        self.recordingContent = QListView()
        self.slider = QSlider(Qt.Horizontal)
        
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
        label = QLabel()
        pixmap = QPixmap("plot.png")
        label.setPixmap(pixmap)

        waveGraph.addWidget(label)

        #slider
        self.slider = QSlider(Qt.Horizontal)

        waveGraph.addWidget(self.slider)


        return waveGraph
    
    def initLowerLayout(self):

        lowerLayout = QHBoxLayout()

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
        recordingButton = QPushButton()
        recordingButton.setText("Recording")
        recordingButton.clicked.connect(self.record_audio)

        lowerLayout.addWidget(recordingButton)

        #stop recording button
        stopRecordingButton = QPushButton()
        stopRecordingButton.setText("Stop")
        stopRecordingButton.clicked.connect(self.stop_record)

        lowerLayout.addWidget(stopRecordingButton)

        #audio time text
        audioTimeText = QLabel()
        audioTimeText.setStyleSheet("QLabel{font-size: 18pt;}")
        audioTimeText.setText("00:00:00.00 / 00:00:00")
        audioTimeText.setAlignment(Qt.AlignCenter)

        lowerLayout.addWidget(audioTimeText)

        #play button
        playButton = QPushButton()
        playButton.setText("Play")

        playButton.clicked.connect(self.play_audio)

        lowerLayout.addWidget(playButton)

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
        print("Recording audio")
        global streamObj, pObj, frames, input_device
        streamObj, pObj = soundRecording.startRecording(44100, 1024, 1, input_device) #initiate, para = fs, chunk, channel
        frames = soundRecording.threadWriting(streamObj, 1024)
    
    def stop_record(self):
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/record_{current_time}.wav"
        global streamObj, pObj, frames
        soundRecording.stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
        soundRecording.fileWriting(frames, 1, 44100, filename)
        self.update_recordingContent()
    
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
        global selected_file
        selected_file = f"recordings/{self.recordingContent.currentItem().text()}"
        if selected_file:
            global wav
            wav = playback.getData(selected_file)
            self.slider.value = 0
            self.slider.sliderPosition = 0
            self.slider.update()
            self.slider.repaint()
            print(selected_file)

    def play_audio(self):
        global selected_file, wav, volume, start, stream
        start = self.slider.value
        #volume = volume_slider.get()
        print(f"Playing {selected_file}")
        stream = playback.getStream(wav)
        playback.play(stream, wav, speed, volume, start)
        playback.stop(stream)
            
       


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()