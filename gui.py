from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import sys
import os
import showDevice

global volume, speed, start, selected_file, edit_frames
volume = 1
speed = 1
start = 0
selected_file = None

recordingDirectory = r"D:\Develop\CSCI3280-Group-Project\TKinter\recordings"

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sound Recorder")
        self.setFixedSize(1600, 900)
        
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
        recordingContent = QListWidget()

        recordingContent.setGeometry(50, 70, 150, 80)

        files = [file for file in os.listdir(recordingDirectory) if file.endswith(".wav")]
        for f in files:
            item = QListWidgetItem(f'{f}')
            recordingContent.addItem(item)

        recordingScrollList.addWidget(recordingContent)

        #wave graph
        waveGraph = self.initWaveGraph()
        recordingScrollList.addWidget(waveGraph)

        return recordingScrollList

    
    def initWaveGraph(self):

        waveGraph = QWidget()

        return waveGraph
    
    def initLowerLayout(self):

        lowerLayout = QHBoxLayout()

        #recording content scroll list
        deviceChoices = QComboBox()

        deviceList = showDevice.getDeviceList()
        for device in deviceList:
            deviceChoices.addItem(device[1])

        lowerLayout.addWidget(deviceChoices)



        return lowerLayout
    
    def initPlayButton(self):

        playButton = QComboBox()

        

        return playButton
    
 
    

       


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec_()