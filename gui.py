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

global input_device, volume, speed, start, end, selected_file, edit_frames, stop_thread, number_of_channel
input_device = 1
volume = 1
speed = 1
start = 0
selected_file = None
number_of_channel = 1

recordingDirectory = "recordings"

class EditWindow(QWidget):
    def __init__(self, end):
        super().__init__()

        self.setWindowTitle("Edit")
        self.setFixedSize(1600, 900)

        self.end = end

        self.initUI()
        

    def initUI(self):

        layout = QVBoxLayout()

        #Label
        audioTrimLabel = QLabel()
        audioTrimLabel.setText("Audio Trim")
        audioTrimLabel.setStyleSheet("QLabel{font-size: 18pt;}")

        layout.addWidget(audioTrimLabel)

        #range slider
        rangeSlider = QRangeSlider(Qt.Horizontal)
        rangeSlider.setMinimum(0)
        rangeSlider.setMaximum(self.end)
        
        rangeSlider.setValue([0, self.end])


        layout.addWidget(rangeSlider)






        self.setLayout(layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Recorder")
        self.setFixedSize(1800, 900)

        playback.getPyAudio()

        self.recordingContent = QListView()
        self.slider = QSlider(Qt.Horizontal)
        self.waveGraph = QLabel()
        self.audioTimeText = QLabel()
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.editWindow = EditWindow(0)
        
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


        #edit button
        editButton = QPushButton()
        editButton.setText("Edit")
        editButton.clicked.connect(self.edit_button_function)

        functionToolLayout.addWidget(editButton)

        waveGraph.addLayout(functionToolLayout)




        return waveGraph
    
    def initLowerLayout(self):

        lowerLayout = QHBoxLayout()

        #channel choice
        channelChoices = QComboBox()
        channelChoices.setStyleSheet("QComboBox{font-size: 8pt;}")

        channelChoices.addItem("1")
        channelChoices.addItem("2")

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
        pauseButton = QPushButton()
        pauseButton.setText("Pause")

        pauseButton.clicked.connect(self.pause_audio)

        lowerLayout.addWidget(pauseButton)

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
        streamObj, pObj = soundRecording.startRecording(44100, 1024, number_of_channel, input_device) #initiate, para = fs, chunk, channel
        frames = soundRecording.threadWriting(streamObj, 1024)
    
    def stop_record(self):
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recordings/record_{current_time}.wav"
        global streamObj, pObj, frames
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
            value = int(wav["duration"])
            end = value
            self.slider.setMaximum(value)
            self.slider.setSliderPosition(0)
            self.slider.update()
            self.slider.repaint()
            playback.visualize(wav)
            pixmap = QPixmap("plot.png")
            self.waveGraph.setPixmap(pixmap)
            end_hour = int(end / 3600)
            end_minute = int((end - end_hour * 3600) / 60)
            end_second = int((end - end_hour % 3600) % 60)
            self.audioTimeText.setText(f"00:00:00 / {end_hour:02d}:{end_minute:02d}:{end_second:02d}")
            print(selected_file)

    def play_audio(self):
        global selected_file, wav, volume, start, stream
        start = self.slider.value()
        #volume = volume_slider.get()
        print(f"Playing {selected_file}")
        stream = playback.getStream(wav)
        thread = Thread(target = self.slider_move)
        thread.start()
        playback.play(stream, wav, speed, volume, start)
        playback.stop(stream)


    def slider_move(self):
        global end, stop_thread, speed
        stop_thread = False
        current_value = self.slider.value()
        current_hour = int(current_value / 3600)
        current_minute = int((current_value - current_hour * 3600) / 60)
        current_second = int((current_value - current_hour * 3600) % 60)

        end_hour = int(end / 3600)
        end_minute = int((end - end_hour * 3600) / 60)
        end_second = int((end - end_hour % 3600) % 60)
        self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}")
        while(current_value < end):
            print(f"{current_value} / {end}")
            time.sleep(1 / speed)
            current_value += 1
            self.slider.setValue(current_value)
            self.slider.setSliderPosition(current_value)
            self.slider.update()
            self.slider.repaint()
            current_hour = int(current_value / 3600)
            current_minute = int((current_value - current_hour * 3600) / 60)
            current_second = int((current_value - current_hour * 3600) % 60)
            self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}")
            if stop_thread == True:
                return

    def pause_audio(self):
        global stream, stop_thread
        stop_thread = True
        print("Pausing audio")
        playback.pause(stream)
        
    def audio_slider_move(self):
        global start, end
        current_value = self.slider.value()
        current_hour = int(current_value / 3600)
        current_minute = int((current_value - current_hour * 3600) / 60)
        current_second = int((current_value - current_hour * 3600) % 60)

        end_hour = int(end / 3600)
        end_minute = int((end - end_hour * 3600) / 60)
        end_second = int((end - end_hour % 3600) % 60)
        self.audioTimeText.setText(f"{current_hour:02d}:{current_minute:02d}:{current_second:02d} / {end_hour:02d}:{end_minute:02d}:{end_second:02d}")


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
    
    def edit_button_function(self, checked):
        global end
        self.editWindow = EditWindow(end = end)
        self.editWindow.show()
            
       


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()