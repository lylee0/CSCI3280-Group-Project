import threading
import os
import time

def serverStart():
    os.system('python \"' + os.path.dirname(os.path.abspath(__file__)) + '/server.py\"')

def lobbyStart():
    os.system('python \"' + os.path.dirname(os.path.abspath(__file__)) + '/lobbyGui.py\"')    

servering = threading.Thread(target=serverStart, args=())
lobbyGuiing = threading.Thread(target=lobbyStart, args=())
servering.start()
time.sleep(1)
lobbyGuiing.start()
