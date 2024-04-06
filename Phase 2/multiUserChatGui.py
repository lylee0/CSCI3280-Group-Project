import os.path
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
import showDevice
import cv2
import numpy as np

host = socket.gethostbyname(socket.gethostname())

uri = 'ws://'+ host +':8765'

otherHost = []
userInRoom = []
indexMember = []

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024
SAMPLEWIDTH = 2
a, temp222 = showDevice.getDeviceList()
b, temp333 = showDevice.getOutputDeviceList()

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=a)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK, output_device_index=b)
stream_music = audio.open(format=FORMAT, channels=2, rate=RATE, output=True, output_device_index=b)

file_start_time = 0
#file_format = 0 # 0 for wav, 1 for mp3
music_dict = 'songs'
music_path = './songs/RedSun_(Instrumental).mp3'

recording = {}
mergeRecording = []
class MemberListPopUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Member List")
        self.setFixedSize(700, 500)
        self.initUI()

    def initUI(self):
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        for name in userInRoom:
            nameLabel = QLabel()
            nameLabel.setText(name)
            nameLabel.setStyleSheet("QLabel{font-size: 18pt;}")
            layout.addWidget(nameLabel)

        self.setLayout(layout)

class MultiUserChatWindow(QWidget):
    def __init__(self, userid, roomID, user, otherHost2):
        super().__init__()

        global otherHost, music_path
        self.online=True
        self.mute = False
        self.video = False
        self.videoStartInd = True
        self.cam = None
        self.voiceChange = False
        self.memberCollection = {}
        otherHost = otherHost2
        music_path = os.listdir(os.path.abspath(os.path.join(os.getcwd(), music_dict)))[0]
        music_path = f"./songs/{music_path}"
        self.setWindowTitle("Chatroom")
        self.resize(1024,640)
        self.setMinimumSize(1024,500)
        self.room = roomID
        self.user = user
        self.userid = userid
        self.record = False
        self.music = False
        #self.music_person = False
        #self.playback = False
        self.firstInd = True
        self.updateMember()
        getCamThread = threading.Thread(target=self.getCam,args=())
        getCamThread.start()
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
        self.memberCollection = {}

        for x in userInRoom:
            memberLayout.addWidget(self.MemberUI(x), int((userInRoom.index(x)-1)/3), int((userInRoom.index(x)-1)%3))

        memberWidget.setLayout(memberLayout)

        return memberWidget
    
    def FunctionBarUI(self):

        functionBarLayout = QHBoxLayout()
        functionBarLayout.setContentsMargins(QMargins(30,0,30,0))

        #I/O device dropdowns
        deviceLayout = QVBoxLayout()

        #input device
        self.inputDeivceDropdown = QComboBox()
        self.inputDeivceDropdown.setFixedWidth(200)
        self.inputDeivceDropdown.setStyleSheet("QComboBox{font-size: 8pt;}")

        inputDeviceID, inputDevices = showDevice.getDeviceList()
        for inputDevice in inputDevices:
            self.inputDeivceDropdown.addItem(inputDevice[1])

        self.inputDeivceDropdown.setCurrentIndex(inputDeviceID)
        deviceLayout.addWidget(self.inputDeivceDropdown)

        #output device
        self.outputDeivceDropdown = QComboBox()
        self.outputDeivceDropdown.setFixedWidth(200)
        self.outputDeivceDropdown.setStyleSheet("QComboBox{font-size: 8pt;}")

        outputDeviceID, outputDevices = showDevice.getOutputDeviceList()
        for outputDevice in outputDevices:
            self.outputDeivceDropdown.addItem(outputDevice[1])

        self.outputDeivceDropdown.setCurrentIndex(outputDeviceID - len(inputDevices))
        deviceLayout.addWidget(self.outputDeivceDropdown)

        #camera device
        self.cameraDropdown = QComboBox()
        self.cameraDropdown.setFixedWidth(200)
        self.cameraDropdown.setStyleSheet("QComboBox{font-size: 8pt;}")

        camera = showDevice.getCameraList()
        for x in camera:
            self.cameraDropdown.addItem(x)

        self.cameraDropdown.setCurrentIndex(0)
        deviceLayout.addWidget(self.cameraDropdown)

        functionBarLayout.addLayout(deviceLayout)



        #mute button
        self.muteButton = QLabel()
        self.muteButton.setGeometry(0, 0, 0, 0)
        if not self.mute:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/microphone.png").scaled(QSize(50, 50)))
        else:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/mute.png").scaled(QSize(50, 50)))
        self.muteButton.setFixedSize(100,100)
        self.muteButton.mousePressEvent = self.MuteButtonFunction
        self.muteButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
        
        functionBarLayout.addWidget(self.muteButton)



        #video button
        self.videoButton = QLabel()
        self.videoButton.setGeometry(0, 0, 0, 0)
        if not self.video:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/video.png").scaled(QSize(50, 50)))
        else:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/no_video.png").scaled(QSize(50, 50)))
        self.videoButton.setFixedSize(100,100)
        self.videoButton.mousePressEvent = self.VideoButtonFunction
        self.videoButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
        
        functionBarLayout.addWidget(self.videoButton)



        #member list button
        self.memberListButton = QLabel()
        self.memberListButton.setGeometry(0, 0, 0, 0)
        self.memberListButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/memberlist.png").scaled(QSize(50, 50)))
        self.memberListButton.setFixedSize(100,100)
        self.memberListButton.mousePressEvent = self.MemberListButtonFunction
        self.memberListButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.memberListButton)



        #chat room button
        self.chatRoomButton = QLabel()
        self.chatRoomButton.setGeometry(0, 0, 0, 0)
        self.chatRoomButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/chatroom.png").scaled(QSize(50, 50)))
        self.chatRoomButton.setFixedSize(100,100)
        self.chatRoomButton.mousePressEvent = self.ChatRoomButtonFunction
        self.chatRoomButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.chatRoomButton)



        #music button
        self.musicButton = QLabel()
        self.musicButton.setGeometry(0, 0, 0, 0)
        if not self.music:
            self.musicButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/karaoke_off.png").scaled(QSize(50, 50)))
        else:
            self.musicButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/karaoke_on.png").scaled(QSize(50, 50)))
        self.musicButton.setFixedSize(100,100)
        self.musicButton.mousePressEvent = self.MusicButtonFunction
        self.musicButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.musicButton)



        #recording button
        self.recordingButton = QLabel()
        self.recordingButton.setGeometry(0, 0, 0, 0)
        if not self.record:
            self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/no_recording.png").scaled(QSize(50, 50)))
        else:
            self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/recording.png").scaled(QSize(50, 50)))
        self.recordingButton.setFixedSize(100,100)
        self.recordingButton.mousePressEvent = self.RecordingButtonFunction
        self.recordingButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.recordingButton)



        #voice change button
        self.voiceChangeButton = QLabel()
        self.voiceChangeButton.setGeometry(0, 0, 0, 0)
        if not self.voiceChange:
            self.voiceChangeButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/voice_change_off.png").scaled(QSize(50, 50)))
        else:
            self.voiceChangeButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/voice_change_on.png").scaled(QSize(50, 50)))
        self.videoButton.setFixedSize(100,100)
        self.voiceChangeButton.mousePressEvent = self.VoiceChangeButtonFunction
        self.voiceChangeButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)

        functionBarLayout.addWidget(self.voiceChangeButton)



        #end chat button
        self.endChatButton = QLabel()
        self.endChatButton.setGeometry(0, 0, 0, 0)
        self.endChatButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/end_chat.png").scaled(QSize(50, 50)))
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
        id = indexMember.index(name)
        self.memberCollection[id] = memberUI

        return memberUI
    


    #Function Bar Button Functions

    def MuteButtonFunction(self, event):
        self.mute = not self.mute
        if (self.mute):
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/mute.png").scaled(QSize(50, 50)))
        else:
            self.muteButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/microphone.png").scaled(QSize(50, 50)))


    def VideoButtonFunction(self, event):
        self.video = not self.video
        if (self.video):
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/no_video.png").scaled(QSize(50, 50)))
        else:
            self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/video.png").scaled(QSize(50, 50)))

    def MemberListButtonFunction(self, event):
        

        self.memberListPopUp = MemberListPopUp()
        self.memberListPopUp.show()
    
    def ChatRoomButtonFunction(self, event):
        return
    
    def MusicButtonFunction(self, event):
        self.music = not self.music
        if self.music:
            #self.music_person = True
            #self.playback = True
            asyncio.new_event_loop().run_until_complete(self.sendMusic())
            self.musicButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/karaoke_off.png").scaled(QSize(50, 50)))
        else:
            asyncio.new_event_loop().run_until_complete(self.send_signal(b'music'))
            self.musicButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/karaoke_on.png").scaled(QSize(50, 50)))
        #return

    async def send_signal(self, message):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + message
            await websocket.send(data)
            await websocket.close()

    def RecordingButtonFunction(self, event):
        # after clicking stop, need to wait for write file thread to finish, then users can click start again
        global recording, merge_thread, write_thread
        #self.record = not self.record
        if not self.record:
            asyncio.get_event_loop().run_until_complete(self.send_signal(b'Start'))
        if recording and self.record:
            asyncio.get_event_loop().run_until_complete(self.send_signal(b'Stop'))
    
    def VoiceChangeButtonFunction(self, event):
        self.voiceChange = not self.voiceChange
        if not self.voiceChange:
            self.voiceChangeButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/voice_change_off.png").scaled(QSize(50, 50)))
        else:
            self.voiceChangeButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/voice_change_on.png").scaled(QSize(50, 50)))

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
            global userInRoom, indexMember
            temp = userInRoom
            userInRoom = data["VoiceRoom"][str(self.room)]
            indexMember = [x["parti"] for x in data["chatRoom"] if x["id"] == self.room][0]
            if temp != userInRoom:
                if self.firstInd:
                    userid = self.userid
                    #self.listen_thread = threading.Thread(target=self.listen, args=(userid, self.room))
                    tempReceiver = otherHost.copy()
                    tempReceiver.append(host)
                    for x in tempReceiver:
                        listen_thread = threading.Thread(target=self.listen, args=(userid, self.room, x))
                        listen_thread.start()
                    self.send_thread = threading.Thread(target=self.send, args=(userid, self.room))
                    #self.listen_thread.start()
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

    def getCam(self):
        while self.online:
            if self.video:
                if self.videoStartInd:
                    try:
                        self.cam = cv2.VideoCapture(self.cameraDropdown.currentIndex(), cv2.CAP_DSHOW)
                        self.videoStartInd = False
                    except:
                        self.video = False
                        self.videoButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/no_video.png").scaled(QSize(50, 50)))
                        fail = QtW.QMessageBox()
                        fail.setIcon(QtW.QMessageBox.Critical)
                        fail.setText("Cannot detect camera")
                        fail.exec_()
                else: 
                    ret, frame = self.cam.read()
                    shape = frame.shape
                    info = struct.pack('>h', 32767) + struct.pack('>h', 32767) + struct.pack('>h', self.userid) + struct.pack('>h', shape[0]) + struct.pack('>h', shape[1]) + struct.pack('>h', shape[2]) + frame.tobytes()
                    loop = asyncio.new_event_loop().run_until_complete(self.videoInfo(info))
                    asyncio.set_event_loop(loop)
            else:
                if not self.videoStartInd:
                    self.videoStartInd = True
                    info = struct.pack('>h', 32767) + struct.pack('>h', 32767) + struct.pack('>h', 32767) + struct.pack('>h', self.userid)
                    loop = asyncio.new_event_loop().run_until_complete(self.videoInfo(info))
                    asyncio.set_event_loop(loop)
                if self.cam != None:
                    if self.cam.isOpened():
                        self.cam.release()
            time.sleep(0.003)
    
    async def videoInfo(self, info):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(info)
            await websocket.close()

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
                            recording = {}
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
        output = path + f"/audio_{time}.wav"
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
            #asyncio.get_event_loop().run_until_complete(self.send_signal(b'Stop'))
            # suppose that user will not receive the stop after closing the windows
            self.record = False
            for x in recording.keys():
                recording[x].append(b'Stop')
            waves = self.writeHeader()
            merge_thread = threading.Thread(target=self.merge)
            merge_thread.start()
            write_thread = threading.Thread(target=self.writeFile, args=(waves,))
            write_thread.start()
            '''global file_format
            if file_format == 1:
                mp3_thread = threading.Thread(target=self.wavToMp3)
                mp3_thread.start()
                self.music = not self.music'''

        if self.music:
            self.music = False
            '''if self.music_person:
                self.music_person = False
                self.playback = False
                asyncio.new_event_loop().run_until_complete(self.send_signal(b'music'))'''
            global stream_music
            stream_music.close()

    def listen(self, userid, roomid, x):
        loop = asyncio.new_event_loop().run_until_complete(self.receiveAudio(userid, roomid, x))
        asyncio.set_event_loop(loop)

    def display(self, qImg, info, h, w, d):
        hDiff = qImg.height()/h
        wDiff = qImg.width()/w
        factor = min(hDiff,wDiff)
        qImg.setPixmap(QPixmap.fromImage(QtG.QImage(info, w, h, w*d, QtG.QImage.Format_RGB888).rgbSwapped()).scaled(int(w*factor), int(h*factor)))

    def clear(self, qImg, userId):
        qImg.clear()
        qImg.setText(indexMember[userId])
        qImg.setStyleSheet("background-color : red; color : blue;")

    
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
                    if struct.unpack('>h', data[2:4])[0] == 32767:
                        if struct.unpack('>h', data[4:6])[0] == 32767:
                            userId = struct.unpack('>h', data[6:8])[0]
                            changeImage = self.memberCollection[userId]
                            clearThread = threading.Thread(target=self.clear, args=(changeImage, userId))
                            clearThread.start()
                        else:
                            userId = struct.unpack('>h', data[4:6])[0]
                            changeImage = self.memberCollection[userId]
                            changeImage.setStyleSheet("")
                            info = data[12:]
                            h = struct.unpack('>h', data[6:8])[0]
                            w = struct.unpack('>h', data[8:10])[0]
                            d = struct.unpack('>h', data[10:12])[0]
                            displayThread = threading.Thread(target=self.display, args=(changeImage, info, h, w, d))
                            displayThread.start()
                    else:
                        if data[4:] == b'Start':
                            if not self.record:
                                self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/recording.png").scaled(QSize(50, 50)))
                                self.record = True
                        elif data[4:] == b'Stop':
                            if self.record:
                                self.recordingButton.setPixmap(QPixmap(os.path.dirname(os.path.abspath(__file__)) + "/icon/no_recording.png").scaled(QSize(50, 50)))
                                self.record = False
                                for x in recording.keys():
                                    recording[x].append(b'Stop')
                                waves = self.writeHeader()
                                merge_thread = threading.Thread(target=self.merge)
                                merge_thread.start()
                                write_thread = threading.Thread(target=self.writeFile, args=(waves,))
                                write_thread.start()
                            '''global file_format
                            if file_format == 1:
                                mp3_thread = threading.Thread(target=self.wavToMp3)
                                mp3_thread.start()'''
                        else:
                            global stream_music
                            if data[4:] == b'music':
                                self.music = False
                                stream_music.close()
                            else:
                                global audio
                                self.music = True
                                self.mp3ToWav(data[4:])
                                stream_music = audio.open(format=info[0], channels=info[1], rate=info[2], output=True, output_device_index=4)
                                play_music_thread = threading.Thread(target=self.playMusic)
                                play_music_thread.start()
                else:
                    room = data[2:4]
                    room = struct.unpack('>h', room)[0]
                    mute = data[4:6]
                    mute = struct.unpack('>h', mute)[0]
                    if user != userid and roomid == room and mute == 0:
                        data = data[6:]
                        stream_output.write(data)
                    '''if user == userid and roomid == room and mute == 0 and self.playback == True:
                            data = data[6:]
                            stream_output.write(data)'''
                    if self.record:
                        data = data[6:]
                        if mute == 1:
                            data = list(data)
                            data = [0 for x in data]
                            data = bytes(data)
                            '''if not self.music:
                                if 'music' in recording:
                                    recording['music'].append(bytes([0 for x in list(data)]))
                                else:                                
                                    recording['music'] = [bytes([0 for x in list(data)])]'''
                        if user in recording.keys():
                            recording[user].append(data)
                        else:
                            recording[user] = [data]
            await websocket.send("LostConnection")
        
    def mp3ToWav(self, data):
        with open("temp.mp3", 'wb') as f:
            f.write(data)
            f.flush()
            f.close()
        audio_file = AudioSegment.from_mp3("temp.mp3")
        audio_file.export("temp.wav", format="wav")
        os.remove("temp.mp3")
        audio_file = wave.open("temp.wav", 'rb')
        #global audio
        #info = [audio.get_format_from_width(audio_file.getsampwidth()), audio_file.getnchannels(), audio_file.getframerate()]
        #audio_file.close()
        #return info

    def playMusic(self):
        # please implement a button for start and stop
        # for start, send music
        # for stop, music.stop()
        global stream_music, recording
        audio_file = wave.open("temp.wav", 'rb')
        data = audio_file.readframes(CHUNK)
        while self.music:
            try:
                data = audio_file.readframes(CHUNK)
                stream_music.write(data)
                #recording['music'].append(data)
            except:
                break
        audio_file.close()
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")
        #self.playback = False

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
    
    async def sendMusic(self):
        global music_path
        with open(music_path, 'rb') as f:
            music_bytes = f.read()
        async with websockets.connect(uri, max_size=2**30) as websocket:
            data = struct.pack('>h', 32767) + struct.pack('>h', self.userid) + music_bytes
            await websocket.send(data)
            await websocket.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MultiUserChatWindow(1, 1, 1, 1)
    w.show()
    app.exec_()
