import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG
import os
from datetime import datetime
import asyncio
import websockets
import json
import socket
import multiUserChatGui
import platform

host = socket.gethostbyname(socket.gethostname())
otherHost = []

class chatData:
    def __init__(self, id, name, lastChatTime, lastMessage, pinned, conv, parti):
        self.id = id
        self.name = name
        self.lCT = lastChatTime
        self.lM = lastMessage
        self.pin = pinned
        self.conv = conv
        self.parti = parti
    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.lCT == other.lCT and self.lM == other.lM and self.pin==other.pin and self.conv == other.conv and self.parti == other.parti

class convData:
    def __init__(self, parti, conv, time):
        self.parti =  parti
        self.conv = conv
        self.time = time
    def __eq__(self, other):
        return self.parti==other.parti and self.conv == other.conv and self.time==other.time

serverData = []

User = ""

async def getInitialList(uri):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send("Read")
            data = await websocket.recv()
            await websocket.close()
            return data
        
async def getInitialProfile(uri, other):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send("Get,+++" + User)
            await websocket.close()
        for x in other:
            async with websockets.connect("ws://" + x + ":8765") as websocket:
                await websocket.send("Get,+++" + User)
                await websocket.close()

async def sendInitialConfig(uri, other):
        global User
        async with websockets.connect(uri, max_size=2**30) as websocket:
            strings = "Connect"
            for x in other:
                strings += ",+++"
                strings += x
            await websocket.send(strings)
            await websocket.close()
        
data = asyncio.get_event_loop().run_until_complete(getInitialList('ws://'+host+':8765'))

data =json.loads(data)

network = data["User"]

for x in data["chatRoom"]:
    if User in x["pinnedBy"]:
        pin = True
    else:
        pin = False
    temp2 = []
    for y in x["conv"]:
        temp = convData(y[0],y[1],y[2])
        temp2.append(temp)
    temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
    serverData.append(temp3)

chatDataCollection = serverData.copy()

class initialWindow(QtW.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Room Lobby")
        self.resize(200,100)
        temp = QtW.QVBoxLayout()
        question = QtW.QLabel("Enter your user name, only proceed when all servers are online:")
        response = QtW.QLineEdit()
        temp.addWidget(question)
        temp.addWidget(response)
        self.setLayout(temp)
        response.returnPressed.connect(lambda: self.prompt(response.text()))
        self.show()
    
    def prompt(self, text):
        global network
        if text in network:
            fail = QtW.QMessageBox()
            fail.setIcon(QtW.QMessageBox.Critical)
            fail.setText("User with same name already online: " + text)
            fail.exec_()
        else:
            global User
            User = text
            network.append(User)
            self.close()

class chooseConnection(QtW.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Room Lobby")
        self.resize(300, 300)
        temp = QtW.QVBoxLayout()
        devices = []
        self.ip = []
        for x in os.popen('arp -a'): 
            if platform.system() == "Windows":
                x = x.split(" ")
                temp4 = [y for y in x if [w for w in y.split(".") if not w.isdigit()]==[]]
                devices += temp4
            else:
                x = x.split(")")
                x = x[0].split("(")
                temp4 = [y for y in x if [w for w in y.split(".") if not w.isdigit()]==[]]
                devices += temp4
        self.add = []
        temp.addWidget(QtW.QLabel())
        question = QtW.QLabel("Select all devices online:")
        hint = QtW.QLabel("Your local ip is " + host)
        temp.addWidget(question)
        temp.addWidget(hint)
        searchbox = QtW.QLineEdit()
        searchbox.textChanged.connect(lambda arg = searchbox.text(): self.search(arg))
        temp.addWidget(searchbox)
        scroll = QtW.QScrollArea()
        tempgroup = QtW.QWidget()
        templayout = QtW.QVBoxLayout()
        for x in devices:
            temp2 = QtW.QCheckBox(x,self)
            temp2.stateChanged.connect(lambda chekced, arg = temp2: self.addConnection(arg))
            temp2.setFixedHeight(15)
            temp2.setStyleSheet("margin: 0 2")
            self.ip.append(temp2)
            templayout.addWidget(temp2)
        templayout.addWidget(QtW.QLabel())
        templayout.setSpacing(0)
        tempgroup.setLayout(templayout)
        scroll.setWidget(tempgroup)
        temp.addWidget(scroll)
        proceed = QtW.QPushButton("Continue")
        proceed.clicked.connect(lambda: self.prompt())
        temp.addWidget(proceed)
        temp.addWidget(QtW.QLabel())
        self.setLayout(temp)
        self.show()
    
    def search(self, text):
            print(text)
            for y in self.ip:
                if text == "":
                    y.show()
                else:
                    if not text in y.text():
                        y.hide()
                    else: 
                        y.show()


    def prompt(self):
        global otherHost
        otherHost = self.add 
        asyncio.get_event_loop().run_until_complete(sendInitialConfig('ws://'+ host +':8765', otherHost))
        asyncio.get_event_loop().run_until_complete(getInitialProfile('ws://'+host+':8765', otherHost))
        self.close()

    def addConnection(self,temp2):
        if temp2.isChecked():
            self.add.append(temp2.text())
        else:
            self.add.remove(temp2.text())

class lobbyWindow(QtW.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Room Lobby")
        self.resize(1024,640)
        self.setMinimumSize(1024,500)
        self.currRoom = 0
        self.newChatWindow = newChat()
        self.newChatWindow.status_signal.connect(self.newChatAction)
        self.chatRoomList()
        self.chatRoomDetail()
        self.timer = QtC.QTimer()
        self.timer.timeout.connect(self.getRefresh)
        self.timer.start(1000)
        self.show()
    
    def chatRoomList(self):
        self.pinExpand = QtW.QLabel()
        self.searchField = QtW.QLineEdit()
        self.pinExpandInd = True
        self.otherExpand = QtW.QLabel()
        self.otherExpandInd = True
        self.pinContent = []
        self.otherContent = []
        self.fflag = True
        self.filter = ""

        self.list = QtW.QWidget(self)
        self.listLayout = QtW.QVBoxLayout()
        self.listLayout.addLayout(self.functionBar())
        self.listLayout.addLayout(self.searchBar())
        self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
        self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
        self.listLayout.setSpacing(5)
        self.list.setLayout(self.listLayout)
        self.list.setStyleSheet("background-color:#92ddc8")


    def functionBar(self):
        functionBar = QtW.QHBoxLayout()
        newChat = QtW.QLabel()
        newChat.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\chat.png").scaled(QtC.QSize(20, 20)))
        newChat.setFixedSize(20,20)
        newChat.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
        newChat.mousePressEvent = self.addChatRoom
        newChat.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
        functionBar.addWidget(QtW.QLabel("Username: " + User))
        functionBar.addWidget(newChat)
        return functionBar
    
    def searchBar(self):
        searchBar = QtW.QVBoxLayout()
        self.searchField.setPlaceholderText("Search Chat Name...")
        self.searchField.setFixedHeight(20)
        self.searchField.setStyleSheet("background-color: None")
        self.searchField.setText(self.filter)
        self.searchField.returnPressed.connect(lambda: self.search(self.searchField.text()))
        searchBar.addWidget(self.searchField)
        return searchBar

    def pinChat(self, showContent):
        pinChat = QtW.QVBoxLayout()
        pinChat.setContentsMargins(0,10,0,10)
        #Title component
        pinTitle = QtW.QHBoxLayout()
        self.pinExpand = QtW.QLabel()
        self.pinExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\collapse.png").scaled(QtC.QSize(10, 10)))
        self.pinExpand.setFixedSize(10,10)
        self.pinExpand.mousePressEvent = self.changeStatusPin
        pinTitle.addWidget(self.pinExpand)
        pinText = QtW.QLabel()
        pinText.setText("Pinned Chat")
        pinText.setFixedSize(290,10)
        pinTitle.addWidget(pinText)
        pinTitle.setSpacing(5)
        pinChat.addLayout(pinTitle)
        #Content
        for x in range(len(chatDataCollection)):
            if chatDataCollection[x].pin and showContent:
                tempBox = QtW.QHBoxLayout()
                tempBox2 = QtW.QVBoxLayout()
                name = QtW.QLabel()
                name.setText(chatDataCollection[x].name)
                name.setFixedHeight(12)
                nameFont = QtG.QFont()
                nameFont.setBold(True)
                name.setFont(nameFont)
                tempBox.addWidget(name)
                lCT = QtW.QLabel()
                if User in chatDataCollection[x].parti:
                    lCT.setText(chatDataCollection[x].lCT)
                else:
                    lCT.setText("N/A")
                lCT.setFixedHeight(12)
                lCT.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
                lCT.setStyleSheet("color: grey")
                lCTFont = QtG.QFont()
                lCT.setFont(lCTFont)
                tempBox.addWidget(lCT)
                tempBox2.addLayout(tempBox)
                lM = QtW.QLabel()
                if User in chatDataCollection[x].parti:
                    lM.setText(chatDataCollection[x].lM)
                else:
                    lM.setText("You are not in this chat room")
                lM.setFixedHeight(12)
                lMFont = QtG.QFont()
                lMFont.setItalic(True)
                lM.setFont(lMFont)
                tempBox2.addWidget(lM)
                tempBox2.setContentsMargins(0,3,0,3)
                tempW = QtW.QFrame()
                tempW.setLayout(tempBox2)
                tempW.setFixedHeight(30)
                tempW.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
                self.pinContent.append([tempW,tempW.geometry(),chatDataCollection[x].id])
                pinChat.addWidget(tempW)
        return pinChat
    
    def otherChat(self, showContent):
        otherChat = QtW.QVBoxLayout()
        otherChat.setContentsMargins(0,10,0,10)
        #Title component
        otherTitle = QtW.QHBoxLayout()
        self.otherExpand = QtW.QLabel()
        self.otherExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\collapse.png").scaled(QtC.QSize(10, 10)))
        self.otherExpand.setFixedSize(10,10)
        self.otherExpand.mousePressEvent = self.changeStatusOther
        otherTitle.addWidget(self.otherExpand)
        otherText = QtW.QLabel()
        otherText.setText("All Chat")
        otherText.setFixedSize(290,10)
        otherTitle.addWidget(otherText)
        otherTitle.setSpacing(5)
        otherChat.addLayout(otherTitle)
        #Content
        for x in range(len(chatDataCollection)):
            if showContent:
                tempBox = QtW.QHBoxLayout()
                tempBox2 = QtW.QVBoxLayout()
                name = QtW.QLabel()
                name.setText(chatDataCollection[x].name)
                name.setFixedHeight(12)
                nameFont = QtG.QFont()
                nameFont.setBold(True)
                name.setFont(nameFont)
                tempBox.addWidget(name)
                lCT = QtW.QLabel()
                if User in chatDataCollection[x].parti:
                    lCT.setText(chatDataCollection[x].lCT)
                else:
                    lCT.setText("N/A")
                lCT.setFixedHeight(12)
                lCT.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
                lCT.setStyleSheet("color: grey")
                lCTFont = QtG.QFont()
                lCT.setFont(lCTFont)
                tempBox.addWidget(lCT)
                tempBox2.addLayout(tempBox)
                lM = QtW.QLabel()
                if User in chatDataCollection[x].parti:
                    lM.setText(chatDataCollection[x].lM)
                else:
                    lM.setText("You are not in this chat room")
                lM.setFixedHeight(12)
                lMFont = QtG.QFont()
                lMFont.setItalic(True)
                lM.setFont(lMFont)
                tempBox2.addWidget(lM)
                tempW = QtW.QFrame()
                tempBox2.setContentsMargins(0,3,0,3)
                tempW.setLayout(tempBox2)
                tempW.setFixedHeight(30)
                tempW.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
                self.otherContent.append([tempW,tempW.geometry(),chatDataCollection[x].id])
                otherChat.addWidget(tempW)
        otherChat.addWidget(QtW.QLabel())
        return otherChat


    def changeStatusPin(self, event):
        if(self.pinExpandInd): 
            self.pinExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\expand.png").scaled(QtC.QSize(10, 10)))
            self.pinExpandInd = False
            for x in self.pinContent:
                x[0].hide()
                x[1] = QtC.QRect(0, 0, 0, 0)
        else:
            self.pinExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\collapse.png").scaled(QtC.QSize(10, 10)))
            self.pinExpandInd = True
            for x in self.pinContent:
                x[0].show()
                x[1] = x[0].geometry()
    
    def changeStatusOther(self, event):
        if(self.otherExpandInd): 
            self.otherExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\expand.png").scaled(QtC.QSize(10, 10)))
            self.otherExpandInd = False
            for x in self.otherContent:
                x[0].hide()
                x[1] = QtC.QRect(0, 0, 0, 0)
        else:
            self.otherExpand.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\collapse.png").scaled(QtC.QSize(10, 10)))
            self.otherExpandInd = True
            for x in self.otherContent:
                x[0].show()
                x[1] = x[0].geometry()

    
    
    def addChatRoom(self, event):
        self.newChatWindow.show()

    def search(self, text):
        global chatDataCollection
        if text == "":
            chatDataCollection = serverData.copy()
            self.removeLayout(self.listLayout)
            self.filter = ""
            self.pinContent = []
            self.otherContent = []
            self.searchField = QtW.QLineEdit()
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True
        else:
            chatDataCollection = [x for x in serverData if text.upper() in x.name.upper()]
            self.removeLayout(self.listLayout)
            self.filter = text
            self.pinContent = []
            self.otherContent = []
            self.searchField = QtW.QLineEdit()
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True
    
    def chatRoomDetail(self):
        self.sendButton = QtW.QLabel()
        self.sendButton.setGeometry(0,0,0,0)
        self.textContext = QtW.QLineEdit()
        self.textContext.setGeometry(0,0,0,0)

        self.detail = QtW.QWidget(self)
        self.detailLayout = QtW.QVBoxLayout()
        self.detailLayout.addLayout(self.infoBar(self.currRoom))
        self.detailLayout.addLayout(self.content(self.currRoom))
        self.detailLayout.addLayout(self.chatBox(self.currRoom))
        self.detailLayout.setSpacing(0)
        self.detailLayout.setContentsMargins(0,0,0,0)
        self.detail.setLayout(self.detailLayout)
        self.detail.setStyleSheet("background-color:#81b69d")

    def infoBar(self, chatRoom):
        if chatRoom != 0:
            tempID = [x for x in serverData if x.id == chatRoom][0]
            userInRoom = User in tempID.parti
        else:
            userInRoom = False
        if(chatRoom == 0) or not userInRoom:
            temp = QtW.QVBoxLayout()
            tempL = QtW.QLabel()
            tempL.setFixedHeight(0)
            temp.addWidget(tempL)
            return temp
        else:
            indexRoom = [x for x in chatDataCollection if x.id == chatRoom][0]
            temp = QtW.QHBoxLayout()
            tempL = QtW.QLabel()
            tempL.setText(indexRoom.name)
            tempL.setFixedHeight(50)
            tempLFont = QtG.QFont(QtG.QFontDatabase.applicationFontFamilies(QtG.QFontDatabase.addApplicationFont(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\Candal.ttf"))[0], 20, 0, False)
            tempL.setFont(tempLFont)
            tempL.setContentsMargins(10,0,10,0)
            tempL.setStyleSheet("background-color:#d2ffb0")

            tempB1 = QtW.QLabel()
            tempB1.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\add-user.png").scaled(QtC.QSize(25, 25)))
            tempB1.setFixedSize(40,50)
            tempB1.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
            tempB1.setContentsMargins(7,12,7,12)
            tempB1.setStyleSheet("background-color:#d2ffb0")
            tempB1.mousePressEvent = self.addParti

            tempB2 = QtW.QLabel()
            tempB2.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\call.png").scaled(QtC.QSize(25, 25)))
            tempB2.setFixedSize(40,50)
            tempB2.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
            tempB2.setContentsMargins(7,12,7,12)
            tempB2.setStyleSheet("background-color:#d2ffb0")
            tempB2.mousePressEvent = self.call

            
            tempB3 = QtW.QLabel()
            tempB3.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\info.png").scaled(QtC.QSize(25, 25)))
            tempB3.setFixedSize(40,50)
            tempB3.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
            tempB3.setContentsMargins(7,12,7,12)
            tempB3.setStyleSheet("background-color:#d2ffb0")
            tempB3.mousePressEvent = self.showInfo
            tempB1.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
            tempB2.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
            tempB3.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
            temp.addWidget(tempL)
            temp.addWidget(tempB1)
            temp.addWidget(tempB2)
            temp.addWidget(tempB3)
            return temp

    def content(self, chatRoom):
        if chatRoom != 0:
            tempID = [x for x in serverData if x.id == chatRoom][0]
            userInRoom = User in tempID.parti
        else:
            userInRoom = False
        if(chatRoom == 0) or not userInRoom:
            notiBox = QtW.QVBoxLayout()
            temp1 = QtW.QLabel()
            noti = QtW.QLabel()
            demoPic = QtW.QLabel()
            if chatRoom == 0:
                demoPic.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\ghost.png").scaled(QtC.QSize(250, 250)))
                demoPic.setFixedSize(250,250)
                noti.setText("Nothing here...")
            else:
                demoPic.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\sleep.png").scaled(QtC.QSize(250, 250)))
                demoPic.setFixedSize(250,250)
                noti.setText("Stop sleeping on it...")
            noti.setFixedHeight(30)
            noti.setFont(QtG.QFont('Times', 20))
            noti2 = QtW.QLabel()
            if chatRoom == 0:
                noti2.setText("Select a chat room from the list to start...")
            else:
                noti2.setText("You have to join this room to engage in discussion here!")
            noti2.setFixedHeight(30)
            noti2.setFont(QtG.QFont('Times', 20))
            temp2 = QtW.QLabel()
            if chatRoom != 0:
                tempHL = QtW.QHBoxLayout()
                joinRoom = QtW.QPushButton("Join now")
                joinRoom.clicked.connect(self.joinRoom)
                joinRoom.resize(100,50)
                joinRoom.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
                joinRoom.setStyleSheet("border: 1px solid black; font-size:25px; background-color: #f5bcbc")
                tempHL.addWidget(QtW.QLabel())
                tempHL.addWidget(joinRoom)
                tempHL.addWidget(QtW.QLabel())
            notiBox.addWidget(temp1)
            notiBox.addWidget(demoPic, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
            notiBox.addWidget(noti, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
            notiBox.addWidget(noti2, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
            if chatRoom !=0:
                notiBox.addLayout(tempHL)
            notiBox.addWidget(temp2)
            return notiBox
        else:
            scroll = QtW.QScrollArea()
            scroll.setVerticalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOn)
            scroll.setHorizontalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
            scroll.setWidgetResizable(True)
            indexRoom = [x for x in chatDataCollection if x.id == chatRoom][0]
            temp = QtW.QVBoxLayout()
            temp.addWidget(QtW.QLabel())
            for x in indexRoom.conv:
                if x.parti != "@SYSTEM":
                    tempLayout = QtW.QHBoxLayout()
                    tempP = QtW.QLabel()
                    tempL = QtW.QLabel()
                    tempL.setText(x.parti)
                    tempL.setFixedSize(610,30)
                    tempL.setFont(QtG.QFont('SansSerif', 12, 100, False))
                    tempL.setContentsMargins(10,10,10,0)
                    tempLayout2 = QtW.QHBoxLayout()
                    tempP2 = QtW.QLabel()
                    tempL2 = QtW.QLabel()
                    tempL2.setText(x.conv)
                    tempL2.setFixedSize(600, 20 + ((tempL2.fontMetrics().boundingRect(tempL2.text()).width() + 20)//580 + 1)*15)
                    tempL2.setFont(QtG.QFont('SansSerif', 11, 50, False))
                    tempL2.setStyleSheet("background-color: #d2ffb0; border-radius: 15px;")
                    tempL2.setWordWrap(True)
                    tempL2.setContentsMargins(10,5,10,5)
                    if x.parti == User:
                        tempLayout.addWidget(tempP)
                        tempLayout.addWidget(tempL)
                        tempLayout2.addWidget(tempP2)
                        tempLayout2.addWidget(tempL2)
                    else:
                        tempLayout.addWidget(tempL)
                        tempLayout2.addWidget(tempL2)
                        tempLayout.setAlignment(QtC.Qt.AlignmentFlag.AlignLeft)
                        tempLayout.setContentsMargins(10,10,10,0)
                        tempLayout2.setAlignment(QtC.Qt.AlignmentFlag.AlignLeft)
                    tempLayout2.setContentsMargins(10,5,10,5)
                    temp.addLayout(tempLayout)
                    temp.addLayout(tempLayout2)
                else:
                    tempL = QtW.QLabel(x.conv)
                    tempL.setAlignment(QtC.Qt.AlignmentFlag.AlignHCenter)
                    tempL.setContentsMargins(0,10,0,10)
                    tempL.setFixedHeight(30)
                    temp.addWidget(tempL)
            tempW = QtW.QWidget()
            tempW.setLayout(temp)
            scroll.setWidget(tempW)
            scroll.verticalScrollBar().setSliderPosition(scroll.verticalScrollBar().maximum())
            tempF = QtW.QVBoxLayout()
            tempF.addWidget(scroll)
            return tempF
    
    def chatBox(self, chatRoom):
        if chatRoom != 0:
            tempID = [x for x in serverData if x.id == chatRoom][0]
            userInRoom = User in tempID.parti
        else:
            userInRoom = False
        if(chatRoom == 0) or not userInRoom:
            temp = QtW.QVBoxLayout()
            tempL = QtW.QLabel()
            tempL.setFixedHeight(0)
            temp.addWidget(tempL)
            return temp
        else:
            indexRoom = [x for x in chatDataCollection if x.id == chatRoom][0]
            temp = QtW.QVBoxLayout()
            temp2 = QtW.QHBoxLayout()
            self.textContext.setPlaceholderText("Type Your Message...")
            self.textContext.setStyleSheet("background-color: #ffffff")
            self.textContext.setContentsMargins(10,20,0,20)
            self.textContext.setFixedHeight(70)
            self.textContext.returnPressed.connect(lambda: self.addMessage())
            self.sendButton.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\send.png").scaled(QtC.QSize(25, 25)))
            self.sendButton.setFixedSize(50,70)
            self.sendButton.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
            self.sendButton.setContentsMargins(10,22,15,22)
            self.sendButton.setCursor(QtC.Qt.CursorShape.PointingHandCursor)
            temp2.addWidget(self.textContext)
            temp2.addWidget(self.sendButton)
            tempL = QtW.QLabel()
            tempL.setFixedHeight(1)
            tempL.setStyleSheet("border: 1px solid grey;")
            temp.addWidget(tempL)
            temp.addLayout(temp2)
            return temp

    async def sendUpdate(self, uri, id, method, item, content):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"Update,+++{id},+++{method},+++{item},+++{content}")
            data = await websocket.recv()
            await websocket.close()
            return data
   
    async def sendRead(self, uri):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"Read")
            data = await websocket.recv()
            await websocket.close()
            return data

    async def transformation(self, data):
        global serverData, chatDataCollection, network

        serverData = []
        chatDataCollection = []

        data =json.loads(data)

        network = data["User"]

        for x in data["chatRoom"]:
            if User in x["pinnedBy"]:
                pin = True
            else:
                pin = False
            temp2 = []
            for y in x["conv"]:
                temp = convData(y[0],y[1],y[2])
                temp2.append(temp)
            temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
            serverData.append(temp3)

        chatDataCollection = serverData.copy()
    
    def joinRoom(self):
        data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', self.currRoom, "add", "parti", User))
        self.transformation(data)
        self.removeLayout(self.listLayout)
        self.pinContent = []
        self.otherContent = []
        self.searchField = QtW.QLineEdit()
        self.listLayout.addLayout(self.functionBar())
        self.listLayout.addLayout(self.searchBar())
        self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
        self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
        self.listLayout.setSpacing(5)
        self.fflag = True
        self.removeLayout(self.detailLayout)
        self.sendButton = QtW.QLabel()
        self.sendButton.setGeometry(0,0,0,0)
        self.textContext = QtW.QLineEdit()
        self.textContext.setGeometry(0,0,0,0)
        self.detailLayout.addLayout(self.infoBar(self.currRoom))
        self.detailLayout.addLayout(self.content(self.currRoom))
        self.detailLayout.addLayout(self.chatBox(self.currRoom))
        self.textContext.setText("")

    def addMessage(self):
        if self.textContext.text() != "":
            [x for x in chatDataCollection if x.id == self.currRoom][0].conv.append(convData(User, self.textContext.text(), datetime.now().strftime("%H:%M %Y/%m/%d")))
            [x for x in chatDataCollection if x.id == self.currRoom][0].lCT = datetime.now().strftime("%H:%M %Y/%m/%d")
            [x for x in chatDataCollection if x.id == self.currRoom][0].lM = User + ": " + self.textContext.text()
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', self.currRoom, "add", "conv", f"{User}&+&{self.textContext.text()}&+&" + str(datetime.now().strftime("%H:%M %Y/%m/%d"))))
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', self.currRoom, "change", "lCT", datetime.now().strftime("%H:%M %Y/%m/%d")))
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', self.currRoom, "change", "lM", User + ": " + self.textContext.text()))
            self.transformation(data)
            self.removeLayout(self.listLayout)
            self.pinContent = []
            self.otherContent = []
            self.searchField = QtW.QLineEdit()
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True
            self.removeLayout(self.detailLayout)
            self.sendButton = QtW.QLabel()
            self.sendButton.setGeometry(0,0,0,0)
            self.textContext = QtW.QLineEdit()
            self.textContext.setGeometry(0,0,0,0)
            self.detailLayout.addLayout(self.infoBar(self.currRoom))
            self.detailLayout.addLayout(self.content(self.currRoom))
            self.detailLayout.addLayout(self.chatBox(self.currRoom))
            self.textContext.setText("")
    
    def showInfo(self, event):
        temp = [x.id for x in serverData]
        pos = temp.index(self.currRoom)
        self.infoWindow = chatInfo(pos)
        self.infoWindow.status_signal.connect(self.newPinAction)
        self.infoWindow.show()
    
    def call(self, event):
        global otherHost
        userid = [x for x in serverData if x.id == self.currRoom][0].parti.index(User)
        self.callWindow = multiUserChatGui.MultiUserChatWindow(userid, self.currRoom, User, otherHost)
        self.callWindow.show()

    def addParti(self, event):
        temp = [x.id for x in serverData]
        pos = temp.index(self.currRoom)
        self.infoWindow = newParti(pos)
        self.infoWindow.show()
    
    def newPinAction(self, info):
        if info=='Go':
            self.removeLayout(self.listLayout)
            self.pinContent = []
            self.otherContent = []
            self.searchField = QtW.QLineEdit()
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True


    def resizeEvent(self, event):
        self.list.setGeometry(0,0,300,self.height())
        self.detail.setGeometry(300,0,self.width()-300,self.height())
        QtW.QMainWindow.resizeEvent(self, event)
    
    def mousePressEvent(self, event):
        #For Room Selection
        if self.fflag:
            if self.pinExpandInd and self.otherExpandInd:
                for x in self.pinContent:
                    x[1] = x[0].geometry()
                for x in self.otherContent:
                    x[1] = x[0].geometry()
            elif not self.pinExpandInd:
                for x in self.otherContent:
                    x[1] = x[0].geometry()
            else:
                for x in self.pinContent:
                    x[1] = x[0].geometry()
            self.fflag = False
        idPin = [x[2] for x in self.pinContent if x[1].contains(event.pos())]
        idAll = [x[2] for x in self.otherContent if x[1].contains(event.pos())]
        if(len(idPin) == 0):
            if(len(idAll) == 0):
                True
            else:
                self.currRoom = idAll[0]
                self.removeLayout(self.detailLayout)
                self.sendButton = QtW.QLabel()
                self.sendButton.setGeometry(0,0,0,0)
                self.textContext = QtW.QLineEdit()
                self.textContext.setGeometry(0,0,0,0)
                self.detailLayout.addLayout(self.infoBar(self.currRoom))
                self.detailLayout.addLayout(self.content(self.currRoom))
                self.detailLayout.addLayout(self.chatBox(self.currRoom))
        else:
            self.currRoom = idPin[0]
            self.removeLayout(self.detailLayout)
            self.sendButton = QtW.QLabel()
            self.sendButton.setGeometry(0,0,0,0)
            self.textContext = QtW.QLineEdit()
            self.textContext.setGeometry(0,0,0,0)
            self.detailLayout.addLayout(self.infoBar(self.currRoom))
            self.detailLayout.addLayout(self.content(self.currRoom))
            self.detailLayout.addLayout(self.chatBox(self.currRoom))
        #For Sending Message
        print(self.currRoom)
        if self.sendButton.geometry().contains(QtC.QPoint(event.pos().x()-300,event.pos().y())):
            self.addMessage()


    def newChatAction(self, info):
        if info=='Go':
            self.removeLayout(self.listLayout)
            self.pinContent = []
            self.otherContent = []
            self.searchField = QtW.QLineEdit()
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True

    def getRefresh(self):
        data = asyncio.get_event_loop().run_until_complete(self.sendRead('ws://'+host+':8765'))
        try:
            data = json.loads(data)
            global network, chatDataCollection, serverData
            temp10 = serverData.copy()
            serverData = []
            network = data["User"]
            for x in data["chatRoom"]:
                if User in x["pinnedBy"]:
                    pin = True
                else:
                    pin = False
                temp2 = []
                for y in x["conv"]:
                    temp = convData(y[0],y[1],y[2])
                    temp2.append(temp)
                temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
                serverData.append(temp3)
            if temp10 != serverData:
                chatDataCollection = serverData.copy()
                temp = self.textContext.text()
                temp2 = self.searchField.text()
                self.removeLayout(self.listLayout)
                self.searchField = QtW.QLineEdit()
                self.pinContent = []
                self.otherContent = []
                self.listLayout.addLayout(self.functionBar())
                self.listLayout.addLayout(self.searchBar())
                self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
                self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
                self.listLayout.setSpacing(5)
                self.fflag = True
                self.removeLayout(self.detailLayout)
                self.sendButton = QtW.QLabel()
                self.sendButton.setGeometry(0,0,0,0)
                self.textContext = QtW.QLineEdit()
                self.textContext.setGeometry(0,0,0,0)
                self.detailLayout.addLayout(self.infoBar(self.currRoom))
                self.detailLayout.addLayout(self.content(self.currRoom))
                self.detailLayout.addLayout(self.chatBox(self.currRoom))
                self.textContext.setText(temp)
                self.searchField.setText(temp2)
                self.searchField.setFocus()
        except:
            print("blank json")

    def removeLayout(self, layout):
        while layout.count()>0:
            childrenLayout = layout.takeAt(0)
            if childrenLayout.widget() != None:
                childrenLayout.widget().deleteLater()
            else:
                self.removeLayout(childrenLayout)

    async def removeParti(self, uri):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"Update,+++-1,+++remove,+++,+++{User}")
            await websocket.close()

    def closeEvent(self, event):
        asyncio.get_event_loop().run_until_complete(self.removeParti('ws://'+host+':8765'))
        event.accept()

class newChat(QtW.QWidget):
    status_signal = QtC.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create chat room")
        self.resize(300,100)
        self.majorL = QtW.QVBoxLayout()
        self.ins = QtW.QLabel("Enter new chat name:")
        self.box = QtW.QLineEdit()
        self.majorL.addWidget(self.ins)
        self.majorL.addWidget(self.box)
        self.setLayout(self.majorL)
        self.box.returnPressed.connect(lambda: self.newChat())

    async def sendUpdate(self, uri, id, name, user):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"NewRoom,+++{id},+++{name},+++{user}")
            data = await websocket.recv()
            await websocket.close()
            return data

    async def transformation(self, data):
        global serverData, chatDataCollection, network

        serverData = []
        chatDataCollection = []

        data =json.loads(data)

        network = data["User"]

        for x in data["chatRoom"]:
            if User in x["pinnedBy"]:
                pin = True
            else:
                pin = False
            temp2 = []
            for y in x["conv"]:
                temp = convData(y[0],y[1],y[2])
                temp2.append(temp)
            temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
            serverData.append(temp3)

        chatDataCollection = serverData.copy()
    
    def newChat(self):
        if self.box.text() != "":
            global chatDataCollection
            temp = serverData[-1].id+1
            serverData.append(chatData(serverData[-1].id+1, self.box.text(), "N/A", "No message yet...", False, [], [User]))
            chatDataCollection = serverData.copy()
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', temp, self.box.text(), User))
            self.transformation(data)
            self.status_signal.emit('Go')
            self.hide()

class chatInfo(QtW.QWidget):
    status_signal = QtC.pyqtSignal(str)
    def __init__(self, room):
        super().__init__()
        self.setWindowTitle("Chat room info")
        self.resize(300,100)
        self.room = room
        self.majorL = QtW.QVBoxLayout()
        self.majorH1 = QtW.QHBoxLayout()
        self.majorH2 = QtW.QHBoxLayout()
        self.partiT = QtW.QLabel("Participant:")
        self.partiT.setFixedWidth(10+self.partiT.fontMetrics().boundingRect(self.partiT.text()).width())
        self.partiT.setContentsMargins(5,10,5,5)
        self.majorH1.addWidget(self.partiT)
        for x in serverData[self.room].parti:
            partiC = QtW.QLabel(x)
            partiC.setFixedWidth(10+partiC.fontMetrics().boundingRect(partiC.text()).width())
            partiC.setContentsMargins(5,10,5,5)
            self.majorH1.addWidget(partiC)
        self.majorH1.addWidget(QtW.QLabel())
        self.pinT = QtW.QLabel("Pinned?")
        self.pinT.setFixedWidth(10+self.partiT.fontMetrics().boundingRect(self.partiT.text()).width())
        self.pinT.setContentsMargins(5,10,5,5)
        self.majorH2.addWidget(self.pinT)
        self.pinC = QtW.QCheckBox()
        self.pinC.setChecked(serverData[self.room].pin)
        self.pinC.stateChanged.connect(lambda: self.pin(self.room))
        self.pinC.setContentsMargins(5,10,5,5)
        self.majorH2.addWidget(self.pinC)
        self.majorL.addLayout(self.majorH1)
        self.majorL.addLayout(self.majorH2)
        self.setLayout(self.majorL)
    
    async def sendUpdate(self, uri, id, method, item, content):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"Update,+++{id},+++{method},+++{item},+++{content}")
            data = await websocket.recv()
            await websocket.close()
            return data

    async def transformation(self, data):
        global serverData, chatDataCollection, network

        serverData = []
        chatDataCollection = []

        data =json.loads(data)

        network = data["User"]

        for x in data["chatRoom"]:
            if User in x["pinnedBy"]:
                pin = True
            else:
                pin = False
            temp2 = []
            for y in x["conv"]:
                temp = convData(y[0],y[1],y[2])
                temp2.append(temp)
            temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
            serverData.append(temp3)

        chatDataCollection = serverData.copy()
    
    def pin(self, checked):
        global chatDataCollection
        serverData[self.room].pin = self.pinC.isChecked()
        if self.pinC.isChecked():
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', serverData[self.room].id, "add", "pinnedBy", User))
        else:
            data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', serverData[self.room].id, "remove", "pinnedBy", User))
        self.transformation(data)
        chatDataCollection = serverData.copy()
        self.status_signal.emit('Go')

class newParti(QtW.QWidget):
    status_signal = QtC.pyqtSignal(str)
    def __init__(self, room):
        super().__init__()
        self.setWindowTitle("Add new participant")
        self.resize(300,300)
        self.room = room
        scroll = QtW.QScrollArea()
        scroll.setVerticalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        self.majorL = QtW.QHBoxLayout()
        self.majorV1 = QtW.QVBoxLayout()
        self.majorV2 = QtW.QVBoxLayout()
        for x in network:
            tempP = QtW.QLabel(x)
            self.majorV1.addWidget(tempP)
            tempPP = QtW.QPushButton()
            tempPP.setText("Add")
            if x in [x for x in serverData[room].parti]:
                tempPP.setEnabled(False)
                print(x)
            tempPP.clicked.connect(lambda checked, arg = x: self.add(arg))
            self.majorV2.addWidget(tempPP)
        self.majorL.addLayout(self.majorV1)
        self.majorL.addLayout(self.majorV2)
        tempW = QtW.QWidget()
        tempW.setLayout(self.majorL)
        scroll.setWidget(tempW)
        scroll.verticalScrollBar().setSliderPosition(scroll.verticalScrollBar().maximum())
        tempF = QtW.QVBoxLayout()
        tempF.addWidget(scroll)
        self.setLayout(tempF)

    async def sendUpdate(self, uri, id, method, item, content):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send(f"Update,+++{id},+++{method},+++{item},+++{content}")
            data = await websocket.recv()
            await websocket.close()
            return data

    async def transformation(self, data):
        global serverData, chatDataCollection, network

        serverData = []
        chatDataCollection = []

        data =json.loads(data)

        network = data["User"]

        for x in data["chatRoom"]:
            if User in x["pinnedBy"]:
                pin = True
            else:
                pin = False
            temp2 = []
            for y in x["conv"]:
                temp = convData(y[0],y[1],y[2])
                temp2.append(temp)
            temp3 = chatData(x["id"], x["name"], x["lCT"], x["lM"], pin, temp2, x["parti"])
            serverData.append(temp3)

        chatDataCollection = serverData.copy()

    def add(self, x):
        serverData[self.room].parti.append(x)
        data = asyncio.get_event_loop().run_until_complete(self.sendUpdate('ws://'+host+':8765', serverData[self.room].id, "add", "parti", x))
        self.transformation(data)
        index = network.index(x)
        self.majorV2.itemAt(index).widget().setEnabled(False)
        


        


app = QtW.QApplication([])
initial = initialWindow()
app.exec_()
if User != "":
    connection = chooseConnection()
    app.exec_()
    lobby = lobbyWindow()
    app.exec_()
