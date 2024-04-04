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

otherHost = []
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
file_format = 0 # 0 for wav, 1 for mp3
music_path = './songs/Mandarin_(Instrumental)'

recording = {}
mergeRecording = []

class MultiUserChatWindow(QWidget):
    def __init__(self, userid, roomID, user, otherHost2):
        super().__init__()

        global otherHost
        self.online=True
        self.mute = False
        self.video = False
        otherHost = otherHost2
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
    
    async def send_start(self):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + b'Start'
            await websocket.send(data)
            await websocket.close()

    async def send_stop(self):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + b'Stop'
            await websocket.send(data)
            await websocket.close()

    def RecordingButtonFunction(self, event):
        global recording, merge_thread, write_thread
        self.record = not self.record
        if self.record:
            asyncio.get_event_loop().run_until_complete(self.send_start())
        if recording and not self.record:
            asyncio.get_event_loop().run_until_complete(self.send_stop())
    
    def EndChatButtonFunction(self, event):
        self.close()
    

    def updateMember(self):
        asyncio.get_event_loop().run_until_complete(self.updateMemberData())

    
    async def updateMemberData(self):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"VoiceAdd,+++{self.room},+++{self.user}")
            await websocket.close()

    async def sendRead(self, uri):
        async with websockets.connect(uri, max_size=2**30) as websocket:
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
                    tempReceiver = otherHost.copy()
                    tempReceiver.append(host)
                    for x in tempReceiver:
                        listen_thread = threading.Thread(target=self.listen, args=(userid, self.room, x))
                        listen_thread.start()
                    self.send_thread = threading.Thread(target=self.send, args=(userid, self.room))
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
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"VoiceRemove,+++{self.room},+++{self.user}")
            await websocket.close()

    def merge(self):
        global recording, mergeRecording
        while True:
            if recording:
                for x in recording.keys():
                    if not recording[x]:
                        continue
                    length = len(recording[x][0])
                    break
                try:
                    audio_zero = bytes([0] * SAMPLEWIDTH * length)
                    audio_merge = AudioSegment(audio_zero,sample_width=SAMPLEWIDTH,channels=CHANNEL,frame_rate=RATE)
                    for x in recording.keys():
                        flag = recording[x].pop(0)
                        if flag == b'Stop':
                            mergeRecording.append(b'Stop')
                            return
                        audio = AudioSegment(flag,sample_width=SAMPLEWIDTH,channels=CHANNEL,frame_rate=RATE)
                        audio_merge = audio.overlay(audio_merge)
                    mergeRecording.append(audio_merge.raw_data)
                except:
                    continue
    
    def writeHeader(self):
        global userInRoom, mergeRecording, output
        time = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recordings')
        if not os.path.exists(path):
            os.makedirs(path)
        output = path + f"\\audio_{time}.wav"
        waves =  wave.open(output, 'wb')
        waves.setnchannels(CHANNEL)
        waves.setsampwidth(SAMPLEWIDTH)
        waves.setframerate(RATE)
        return waves

    def writeFile(self, waves):
        while True:
            if mergeRecording:
                flag = mergeRecording.pop(0)
                if flag == b'Stop':
                    global recording
                    waves.close()
                    recording = {}
                    return
                waves.writeframes(flag) 

    def wavToMp3(self):
        global output, merge_thread, write_thread
        merge_thread.join()
        write_thread.join()
        wav_file = AudioSegment.from_wav(output)
        wav_file.export(output[:-3] + "mp3", format='mp3')
        os.remove(output)

    def closeEvent(self, event):
        global recording, userInRoom
        asyncio.get_event_loop().run_until_complete(self.removeParti())
        userInRoom.remove(self.user)
        self.timer.stop()
        self.online = False
        if self.record:
            self.record = False
            asyncio.get_event_loop().run_until_complete(self.send_stop())

    def listen(self, userid, roomid, x):
        loop = asyncio.new_event_loop().run_until_complete(self.receiveAudio(userid, roomid, x))
        asyncio.set_event_loop(loop)
    
    async def receiveAudio(self, userid, roomid, x):
        global recording
        async with websockets.connect("ws://" + x + ":8765", max_size=2**30) as websocket:
            await websocket.send("Listener")
            while self.online:
                data = await websocket.recv()
                user = data[:2]
                user = struct.unpack('>h', user)[0]
                if user == 32767:
                    global merge_thread, write_thread
                    if data[4:] == b'Start':
                        self.record = True
                        waves = self.writeHeader()
                        merge_thread = threading.Thread(target=self.merge)
                        merge_thread.start()
                        write_thread = threading.Thread(target=self.writeFile, args=(waves,))
                        write_thread.start()
                    elif data[4:] == b'Stop':
                        self.record = False
                        for x in recording.keys():
                            recording[x].append(b'Stop')
                        global file_format
                        if file_format == 1:
                            mp3_thread = threading.Thread(target=self.wavToMp3)
                            mp3_thread.start()
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
                            recording[user].append(data)
                        else:
                            recording[user] = [data]
            await websocket.send("LostConnection")


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
        async with websockets.connect(uri, max_size=2**30) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + mp3_bytes
            await websocket.send(data)
            await websocket.close()

        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TestApp()
    w.show()
    app.exec_()
