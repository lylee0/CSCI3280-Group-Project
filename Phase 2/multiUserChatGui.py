from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt
from qtrangeslider import QRangeSlider
import os
from datetime import datetime
import websockets
import threading
import time
import sys

#For testing only
class TestApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test App")
        self.setGeometry(100, 100, 800, 600)
        mainWidget = QWidget()


        self.uiWindow = MultiUserChatWindow()

        self.mainLayout = QVBoxLayout()

        self.button = QPushButton()
        self.button.setText("Button")
        self.button.clicked.connect(self.ButtonFunction)

        self.mainLayout.addWidget(self.button)

        mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(mainWidget)

        

    def ButtonFunction(self):
        self.uiWindow.show()


class MultiUserChatWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chatroom")
        self.resize(1024,640)
        self.setMinimumSize(1024,500)

        #Member Display
        self.memberUI = self.MemberGroupUI()

        self.initUI()

    def initUI(self):
        
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)

        #Member Display
        self.memberUI = self.MemberGroupUI()
        mainLayout.addWidget(self.memberUI)

        #Function Bar
        functionBar = self.FunctionBarUI()
        mainLayout.addLayout(functionBar)
        functionBar.setAlignment(Qt.AlignBottom)



        self.setLayout(mainLayout)
    
    def MemberGroupUI(self):
        
        memberWidget = QWidget()
        memberWidget.setStyleSheet("background-color : blue;")
        memberLayout = QGridLayout()

        memberLayout.addWidget(self.MemberUI("AAA"), 0, 0)
        memberLayout.addWidget(self.MemberUI("BBB"), 0, 1)
        memberLayout.addWidget(self.MemberUI("CCC"), 0, 2)

        memberLayout.addWidget(self.MemberUI("AAA"), 1, 0)
        memberLayout.addWidget(self.MemberUI("BBB"), 1, 1)
        memberLayout.addWidget(self.MemberUI("CCC"), 1, 2)

        memberWidget.setLayout(memberLayout)

        return memberWidget
    
    def FunctionBarUI(self):

        functionBarLayout = QHBoxLayout()

        #mute button
        muteButton = QPushButton()
        muteButton.setText("mute")

        functionBarLayout.addWidget(muteButton)



        #video button
        videoButton = QPushButton()
        videoButton.setText("video")

        functionBarLayout.addWidget(videoButton)



        #member list button
        memberListButton = QPushButton()
        memberListButton.setText("member")

        functionBarLayout.addWidget(memberListButton)



        #chat room button
        chatRoomButton = QPushButton()
        chatRoomButton.setText("chatroom")

        functionBarLayout.addWidget(chatRoomButton)



        #share screen button
        shareScreenButton = QPushButton()
        shareScreenButton.setText("share screen")

        functionBarLayout.addWidget(shareScreenButton)



        #recording button
        recordingButton = QPushButton()
        recordingButton.setText("recording")

        functionBarLayout.addWidget(recordingButton)



        #end chat button
        endChatButton = QPushButton()
        endChatButton.setText("end chat")

        functionBarLayout.addWidget(endChatButton)


        return functionBarLayout
    
    def MemberUI(self, name):
        
        memberUI = QLabel()
        memberUI.setText(name)
        memberUI.setAlignment(Qt.AlignCenter)
        memberUI.setStyleSheet("background-color : red; color : blue;")

        return memberUI
app = QApplication(sys.argv)
w = TestApp()
w.show()
app.exec_()