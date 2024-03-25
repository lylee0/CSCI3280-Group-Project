from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize, QMargins
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
        mainLayout.addLayout(functionBar, Qt.AlignBottom)



        self.setLayout(mainLayout)
        self.setStyleSheet("background-color:#92ddc8")
    
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
        functionBarLayout.setContentsMargins(QMargins(30,0,30,0))

        #mute button
        self.mute = False
        self.muteButton = QLabel()
        self.muteButton.setGeometry(0, 0, 0, 0)
        self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\microphone.png").scaled(QSize(25, 25)))
        self.muteButton.setFixedSize(100,100)
        self.muteButton.mousePressEvent = self.MuteButtonFunction
        
        functionBarLayout.addWidget(self.muteButton)



        #video button
        self.video = False
        self.videoButton = QLabel()
        self.videoButton.setGeometry(0, 0, 0, 0)
        self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\video.png").scaled(QSize(25, 25)))
        self.videoButton.setFixedSize(100,100)
        self.videoButton.mousePressEvent = self.VideoButtonFunction
        
        functionBarLayout.addWidget(self.videoButton)



        #member list button
        self.memberListButton = QLabel()
        self.memberListButton.setGeometry(0, 0, 0, 0)
        self.memberListButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\memberlist.png").scaled(QSize(25, 25)))
        self.memberListButton.setFixedSize(100,100)
        self.memberListButton.mousePressEvent = self.MemberListButtonFunction

        functionBarLayout.addWidget(self.memberListButton)



        #chat room button
        self.chatRoomButton = QLabel()
        self.chatRoomButton.setGeometry(0, 0, 0, 0)
        self.chatRoomButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\chatroom.png").scaled(QSize(25, 25)))
        self.chatRoomButton.setFixedSize(100,100)
        self.chatRoomButton.mousePressEvent = self.ChatRoomButtonFunction

        functionBarLayout.addWidget(self.chatRoomButton)



        #share screen button
        self.shareScreenButton = QLabel()
        self.shareScreenButton.setGeometry(0, 0, 0, 0)
        self.shareScreenButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\share_screen.png").scaled(QSize(25, 25)))
        self.shareScreenButton.setFixedSize(100,100)
        self.shareScreenButton.mousePressEvent = self.ShareScreenButtonFunction

        functionBarLayout.addWidget(self.shareScreenButton)



        #recording button
        self.recordingButton = QLabel()
        self.recordingButton.setGeometry(0, 0, 0, 0)
        self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\recording.png").scaled(QSize(50, 50)))
        self.recordingButton.setFixedSize(100,100)
        self.recordingButton.mousePressEvent = self.RecordingButtonFunction

        functionBarLayout.addWidget(self.recordingButton)



        #end chat button
        endChatButton = QPushButton()
        self.endChatButton = QLabel()
        self.endChatButton.setGeometry(0, 0, 0, 0)
        self.endChatButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\end_chat.png").scaled(QSize(50, 50)))
        self.endChatButton.setFixedSize(100,100)
        self.endChatButton.mousePressEvent = self.RecordingButtonFunction

        functionBarLayout.addWidget(self.endChatButton, Qt.AlignRight)


        return functionBarLayout
    
    def MemberUI(self, name):
        
        memberUI = QLabel()
        memberUI.setText(name)
        memberUI.setAlignment(Qt.AlignCenter)
        memberUI.setStyleSheet("background-color : red; color : blue;")

        return memberUI
    


    #Function Bar Button Functions

    def MuteButtonFunction(self, event):
        self.mute = not self.mute
        if (self.mute):
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\mute.png").scaled(QSize(25, 25)))
        else:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\microphone.png").scaled(QSize(25, 25)))

    def VideoButtonFunction(self, event):
        self.video = not self.video
        if (self.video):
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\no_video.png").scaled(QSize(25, 25)))
        else:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\video.png").scaled(QSize(25, 25)))

    def MemberListButtonFunction(self, event):
        return
    
    def ChatRoomButtonFunction(self, event):
        return
    
    def ShareScreenButtonFunction(self, event):
        return
    
    def RecordingButtonFunction(self, event):
        return
    
    def EndChatButtonFunction(self, event):
        return
    

app = QApplication(sys.argv)
w = TestApp()
w.show()
app.exec_()