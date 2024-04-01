from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize, QMargins
import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG
from qtrangeslider import QRangeSlider
import os
from datetime import datetime
import websockets
import threading
import time
import sys
from pydub import AudioSegment
import asyncio
import json
import pyaudio
import struct
import wave
import socket

host = socket.gethostbyname(socket.gethostname())

uri = 'ws://'+ host +':8765'

userInRoom = []

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024
SAMPLEWIDTH = 2

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK, output_device_index=3)

file_start_time = 0

recording = {}

class MultiUserChatWindow(QWidget):
    def __init__(self, userid, roomID, user):
        super().__init__()

        self.online=True
        self.mute = False
        self.video = False
        self.setWindowTitle("Chatroom")
        self.resize(1024,640)
        self.setMinimumSize(1024,500)
        self.room = roomID
        self.user = user
        self.userid = userid
        self.record = False
        self.firstInd = True
        self.updateMember()
        self.timer = QtC.QTimer()
        self.timer.timeout.connect(self.getRefresh)
        self.timer.start(1000)

        #Member Display
        self.memberUI = self.MemberGroupUI()

        self.initUI()

    def initUI(self):
        
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setSpacing(10)

        #Member Display
        self.memberUI = self.MemberGroupUI()
        self.mainLayout.addWidget(self.memberUI)

        #Function Bar
        functionBar = self.FunctionBarUI()
        self.mainLayout.addLayout(functionBar, QtC.Qt.AlignmentFlag.AlignBottom)



        self.setLayout(self.mainLayout)
        self.setStyleSheet("background-color:#92ddc8")
    
    def MemberGroupUI(self):
        
        memberWidget = QWidget()
        memberWidget.setStyleSheet("background-color : blue;")
        memberLayout = QGridLayout()

        for x in userInRoom:
            memberLayout.addWidget(self.MemberUI(x), int((userInRoom.index(x)-1)/3), int((userInRoom.index(x)-1)%3))

        memberWidget.setLayout(memberLayout)

        return memberWidget
    
    def FunctionBarUI(self):

        functionBarLayout = QHBoxLayout()
        functionBarLayout.setContentsMargins(QMargins(30,0,30,0))

        #mute button
        self.muteButton = QLabel()
        self.muteButton.setGeometry(0, 0, 0, 0)
        if not self.mute:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\microphone.png").scaled(QSize(25, 25)))
        else:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\mute.png").scaled(QSize(25, 25)))
        self.muteButton.setFixedSize(100,100)
        self.muteButton.mousePressEvent = self.MuteButtonFunction
        self.muteButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
        
        functionBarLayout.addWidget(self.muteButton)



        #video button
        self.videoButton = QLabel()
        self.videoButton.setGeometry(0, 0, 0, 0)
        if not self.video:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\video.png").scaled(QSize(25, 25)))
        else:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\no_video.png").scaled(QSize(25, 25)))
        self.videoButton.setFixedSize(100,100)
        self.videoButton.mousePressEvent = self.VideoButtonFunction
        self.videoButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
        
        functionBarLayout.addWidget(self.videoButton)



        #member list button
        self.memberListButton = QLabel()
        self.memberListButton.setGeometry(0, 0, 0, 0)
        self.memberListButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\memberlist.png").scaled(QSize(25, 25)))
        self.memberListButton.setFixedSize(100,100)
        self.memberListButton.mousePressEvent = self.MemberListButtonFunction
        self.memberListButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.memberListButton)



        #chat room button
        self.chatRoomButton = QLabel()
        self.chatRoomButton.setGeometry(0, 0, 0, 0)
        self.chatRoomButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\chatroom.png").scaled(QSize(25, 25)))
        self.chatRoomButton.setFixedSize(100,100)
        self.chatRoomButton.mousePressEvent = self.ChatRoomButtonFunction
        self.chatRoomButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.chatRoomButton)



        #share screen button
        self.shareScreenButton = QLabel()
        self.shareScreenButton.setGeometry(0, 0, 0, 0)
        self.shareScreenButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\share_screen.png").scaled(QSize(25, 25)))
        self.shareScreenButton.setFixedSize(100,100)
        self.shareScreenButton.mousePressEvent = self.ShareScreenButtonFunction
        self.shareScreenButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.shareScreenButton)



        #recording button
        self.recordingButton = QLabel()
        self.recordingButton.setGeometry(0, 0, 0, 0)
        self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\recording.png").scaled(QSize(50, 50)))
        self.recordingButton.setFixedSize(100,100)
        self.recordingButton.mousePressEvent = self.RecordingButtonFunction
        self.recordingButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.recordingButton)



        #end chat button
        endChatButton = QPushButton()
        self.endChatButton = QLabel()
        self.endChatButton.setGeometry(0, 0, 0, 0)
        self.endChatButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\end_chat.png").scaled(QSize(50, 50)))
        self.endChatButton.setFixedSize(100,100)
        self.endChatButton.mousePressEvent = self.EndChatButtonFunction
        self.endChatButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.endChatButton, QtC.Qt.AlignmentFlag.AlignRight)


        return functionBarLayout
    
    def MemberUI(self, name):

        memberUI = QLabel()
        memberUI.setText(name)
        memberUI.setAlignment(QtC.Qt.AlignmentFlag.AlignCenter)
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
        global recording
        self.record = not self.record
        if recording and not self.record:
            audio_merge = self.merge()
            mp3_bytes = self.writeFile(audio_merge)
            asyncio.get_event_loop().run_until_complete(self.sendRecording(mp3_bytes))
            recording = {}
    
    def EndChatButtonFunction(self, event):
        self.close()
    

    def updateMember(self):
        asyncio.get_event_loop().run_until_complete(self.updateMemberData())

    
    async def updateMemberData(self):
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"VoiceAdd,+++{self.room},+++{self.user}")
            await websocket.close()

    async def sendRead(self, uri):
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"Read")
            data = await websocket.recv()
            await websocket.close()
            return data

    def getRefresh(self):
        data = asyncio.get_event_loop().run_until_complete(self.sendRead(uri))
        try:
            data = json.loads(data)
            global userInRoom
            temp = userInRoom
            userInRoom = data["VoiceRoom"][str(self.room)]
            if temp != userInRoom:
                if self.firstInd:
                    userid = self.userid
                    self.listen_thread = threading.Thread(target=self.listen, args=(userid, self.room))
                    self.send_thread = threading.Thread(target=self.send, args=(userid, self.room))
                    self.listen_thread.start()
                    self.send_thread.start()
                    self.firstInd = False
                self.removeLayout(self.mainLayout)
                self.mainLayout.setSpacing(10)
                self.memberUI = self.MemberGroupUI()
                self.mainLayout.addWidget(self.memberUI)
                functionBar = self.FunctionBarUI()
                self.mainLayout.addLayout(functionBar, QtC.Qt.AlignmentFlag.AlignBottom)
        except:
            print("empty json")

    def removeLayout(self, layout):
        while layout.count()>0:
            childrenLayout = layout.takeAt(0)
            if childrenLayout.widget() != None:
                childrenLayout.widget().deleteLater()
            else:
                self.removeLayout(childrenLayout)

    async def removeParti(self):
        async with websockets.connect(uri) as websocket:
            await websocket.send(f"VoiceRemove,+++{self.room},+++{self.user}")
            await websocket.close()

    def merge(self):
        global recording
        for x in recording.keys():
            length = len(recording[x])
            break
        audio_zero = bytes([0] * SAMPLEWIDTH * length)
        audio_merge = AudioSegment(audio_zero,sample_width=SAMPLEWIDTH,channels=CHANNEL,frame_rate=RATE)
        for x in recording.keys():
            audio = AudioSegment(recording[x],sample_width=SAMPLEWIDTH,channels=CHANNEL,frame_rate=RATE)
            audio_merge = audio.overlay(audio_merge)
        audio_merge = audio_merge.raw_data
        return audio_merge
    
    def writeFile(self, merge_audio):
        #print(merge_audio)
        global userInRoom
        time = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings')
        if not os.path.exists(path):
            os.makedirs(path)
        output = path + f"\\audio_{time}.mp3"
        audio = AudioSegment(data=merge_audio, sample_width=SAMPLEWIDTH, channels=CHANNEL, frame_rate=RATE)
        audio.export(output, format="mp3")
        with open(output, 'rb') as f:
            mp3_bytes = f.read()
        f.close()
        return mp3_bytes

    def closeEvent(self, event):
        global recording, userInRoom
        asyncio.get_event_loop().run_until_complete(self.removeParti())
        userInRoom.remove(self.user)
        self.timer.stop()
        self.online = False
        self.record = not self.record
        if recording and not self.record:
            audio_merge = self.merge()
            mp3_bytes = self.writeFile(audio_merge)
            asyncio.get_event_loop().run_until_complete(self.sendRecording(mp3_bytes))
            recording = {}

    def listen(self, userid, roomid):
        loop = asyncio.new_event_loop().run_until_complete(self.receiveAudio(userid, roomid))
        asyncio.set_event_loop(loop)

    async def receiveAudio(self, userid, roomid):
        global recording
        async with websockets.connect(uri, max_size=2**30) as websocket:
            while self.online:
                data = await websocket.recv()
                user = data[:2]
                user = struct.unpack('>h', user)[0]
                if user == 32767:
                    if struct.unpack('>h', data[2:4])[0] != self.userid:
                        write_thread = threading.Thread(target=self.writeFile, args=([data[2:]]))
                        write_thread.start()
                else:
                    room = data[2:4]
                    room = struct.unpack('>h', room)[0]
                    mute = data[4:6]
                    mute = struct.unpack('>h', mute)[0]
                    if user != userid and roomid == room and mute == 0:
                        data = data[6:]
                        stream_output.write(data)
                    if self.record:
                        data = data[6:]
                        if mute == 1:
                            data = list(data)
                            data = [0 for x in data]
                            data = bytes(data)
                        if user in recording.keys():
                            recording[user] += data
                        else:
                            recording[user] = data


    def send(self, userid, roomid):
        loop = asyncio.new_event_loop().run_until_complete(self.sendAudio(userid, roomid))
        asyncio.set_event_loop(loop)

    def recordVoice(self):
        while self.online:
            data = stream_input.read(CHUNK)
            yield data

    async def sendAudio(self, userid, roomid):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            for data in self.recordVoice():
                if self.mute:
                    data = struct.pack('>h', userid) + struct.pack('>h', roomid) + struct.pack('>h', 1) + data
                else:
                    data = struct.pack('>h', userid) + struct.pack('>h', roomid) + struct.pack('>h', 0) + data
                await websocket.send(data)
    
    async def sendRecording(self, mp3_bytes):
        async with websockets.connect(uri) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + mp3_bytes
            await websocket.send(data)
            websocket.close()

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TestApp()
    w.show()
    app.exec_()
