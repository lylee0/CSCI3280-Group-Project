import PyQt5.QtWidgets as QtW
import PyQt5.QtCore as QtC
import PyQt5.QtGui as QtG
import os
from datetime import datetime
import websockets
import threading
import time

class chatData:
    def __init__(self, id, name, lastChatTime, lastMessage, pinned, conv, parti):
        self.id = id
        self.name = name
        self.lCT = lastChatTime
        self.lM = lastMessage
        self.pin = pinned
        self.conv = conv
        self.parti = parti

class convData:
    def __init__(self, parti, conv, time):
        self.parti =  parti
        self.conv = conv
        self.time = time


ChatA = convData("Ken", "Let's have a call. This call aims to discuss the project milestones that we've set last time. Would be good if everyone can join the meeting.", "22:05 2022/01/05")

ChatB = convData("Jason", "Sure", "22:05 2022/01/05")

ChatC = convData("@SYSTEM", "Call started", "22:05 2022/01/05")

ChatD = convData("@SYSTEM", "Call ended", "22:15 2022/01/05")

chatHistoryCollection = [ChatA, ChatB, ChatC, ChatD]

TestA = chatData(1,"TestA", "22:05 2022/01/05", "Call ended", True, chatHistoryCollection, ["Ken", "Jason"])

ChatD = convData("Ken", "Testing", "22:15 2022/01/05")

TestB = chatData(2,"TestB", "22:05 2022/01/05", "Ken: Testing", False, [ChatD], ["Ken"])

serverData = [TestA, TestB]

chatDataCollection = serverData.copy()

network = ["Ken", "Jason", "Amy", "Tom"]

User = "Ken"

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
        self.show()

    def chatRoomList(self):
        self.pinExpand = QtW.QLabel()
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
        searchField = QtW.QLineEdit()
        searchField.setPlaceholderText("Search Chat Name...")
        searchField.setFixedHeight(20)
        searchField.setStyleSheet("background-color: None")
        searchField.setText(self.filter)
        searchField.returnPressed.connect(lambda: self.search(searchField.text()))
        searchBar.addWidget(searchField)
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
                lCT.setText(chatDataCollection[x].lCT)
                lCT.setFixedHeight(12)
                lCT.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
                lCT.setStyleSheet("color: grey")
                lCTFont = QtG.QFont()
                lCT.setFont(lCTFont)
                tempBox.addWidget(lCT)
                tempBox2.addLayout(tempBox)
                lM = QtW.QLabel()
                lM.setText(chatDataCollection[x].lM)
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
                lCT.setText(chatDataCollection[x].lCT)
                lCT.setFixedHeight(12)
                lCT.setAlignment(QtC.Qt.AlignmentFlag.AlignRight)
                lCT.setStyleSheet("color: grey")
                lCTFont = QtG.QFont()
                lCT.setFont(lCTFont)
                tempBox.addWidget(lCT)
                tempBox2.addLayout(tempBox)
                lM = QtW.QLabel()
                lM.setText(chatDataCollection[x].lM)
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
        if(chatRoom == 0):
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
        if(chatRoom == 0):
            notiBox = QtW.QVBoxLayout()
            temp1 = QtW.QLabel()
            noti = QtW.QLabel()
            demoPic = QtW.QLabel()
            demoPic.setPixmap(QtG.QPixmap(os.path.dirname(os.path.abspath(__file__)) + "\\icon\\ghost.png").scaled(QtC.QSize(250, 250)))
            demoPic.setFixedSize(250,250)
            noti.setText("Nothing here...")
            noti.setFixedHeight(30)
            noti.setFont(QtG.QFont('Times', 20))
            noti2 = QtW.QLabel()
            noti2.setText("Select a chat room from the list to start...")
            noti2.setFixedHeight(30)
            noti2.setFont(QtG.QFont('Times', 20))
            temp2 = QtW.QLabel()
            notiBox.addWidget(temp1)
            notiBox.addWidget(demoPic, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
            notiBox.addWidget(noti, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
            notiBox.addWidget(noti2, alignment=QtC.Qt.AlignmentFlag.AlignHCenter)
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
        if(chatRoom == 0):
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

    
    def addMessage(self):
        if self.textContext.text() != "":
            [x for x in chatDataCollection if x.id == self.currRoom][0].conv.append(convData(User, self.textContext.text(), datetime.now().strftime("%H:%M %Y/%m/%d")))
            [x for x in chatDataCollection if x.id == self.currRoom][0].lCT = datetime.now().strftime("%H:%M %Y/%m/%d")
            [x for x in chatDataCollection if x.id == self.currRoom][0].lM = User + ": " + self.textContext.text()
            self.removeLayout(self.listLayout)
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
            self.textContext.setText("")
    
    def showInfo(self, event):
        temp = [x.id for x in serverData]
        pos = temp.index(self.currRoom)
        self.infoWindow = chatInfo(pos)
        self.infoWindow.status_signal.connect(self.newPinAction)
        self.infoWindow.show()
    
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
            self.listLayout.addLayout(self.functionBar())
            self.listLayout.addLayout(self.searchBar())
            self.listLayout.addLayout(self.pinChat(self.pinExpandInd))
            self.listLayout.addLayout(self.otherChat(self.otherExpandInd))
            self.listLayout.setSpacing(5)
            self.fflag = True

    def removeLayout(self, layout):
        while layout.count()>0:
            childrenLayout = layout.takeAt(0)
            if childrenLayout.widget() != None:
                childrenLayout.widget().deleteLater()
            else:
                self.removeLayout(childrenLayout)

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

    def newChat(self):
        if self.box.text() != "":
            global chatDataCollection
            serverData.append(chatData(serverData[-1].id+1, self.box.text(), "N/A", "No message yet...", False, [], [User]))
            chatDataCollection = serverData.copy()
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
    
    def pin(self, checked):
        global chatDataCollection
        serverData[self.room].pin = self.pinC.isChecked()
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
    
    def add(self, x):
        serverData[self.room].parti.append(x)
        index = network.index(x)
        self.majorV2.itemAt(index).widget().setEnabled(False)
        



        


app = QtW.QApplication([])
lobby = lobbyWindow()
app.exec_()