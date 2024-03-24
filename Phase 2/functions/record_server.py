import pyaudio
import asyncio
import websockets
import numpy as np
import cv2
import pyautogui
import pygetwindow as gw
import socket


clients = set() # a list?
audio_bytes = []
audio_array = [] # 2d numpy array
audio_merged = [] # int
recording = False
channel = 1
samp_width = 2
fs = 44100
block_align = 2 #???
PORT = 8765
IP = socket.gethostbyname('localhost')
ADDR = (IP, PORT)
CONNECTIONS = set()


'''
    Recieve audio from all clients
'''
async def receive_audio(websocket, client_id):
    # can client_id be 0 t0 len(clients)?
    global clients

    async for message in websocket: # change 
        if recording:
            audio_bytes[client_id].append(message)

'''
    Merge all users audio, and call the write file function (in server)
'''
async def merge_audio():
    # audio_array is a 2d np array
    global audio_array
    while audio_array:
        compare = []
        for data in audio_array:
            compare.append(data.pop(0))
        maximum = max(compare)
        compare = []
        audio_merged.append(maximum)

'''
    Convert byte to integer (in server)
'''
async def byte_to_int():
    global audio_bytes, audio_array
    # length of audio_bytes == number of users
    while audio_bytes:
        #for bytes in audio_bytes:
        for i in range(len(audio_bytes)):
            # assume 16 bits
            data = int.from_bytes(audio_bytes[i][:2], byteorder='little', signed=True)
            audio_bytes[i] = audio_bytes[i][2:]
            audio_array[i].append(data)

'''
    Send merged audio data to all clients
'''
async def send_audio(websocket):
    while audio_merged:
        data = audio_merged.pop(0)
        await websocket.send(data.astype(np.int32).tobytes())

'''
    Handle the messages sent to server
'''
async def handle_server(websocket): # client connects to server
    global clients, recording, audio_bytes, audio_array, audio_merged

    clients.add(websocket)
    #client_id = id(websocket)

    async for message in websocket:
        if message == "Start Recording":
            recording = True
            audio_bytes = []
            audio_array = [] # 2d numpy array
            audio_merged = []

            # send to all clients
            await websocket.send('Start Recording')

            print(clients)
            #client = clients[0]
            # change this ???
            task_receive = asyncio.create_task(receive_audio(websocket, id(clients))) # recieve audio from clients
            # convert audio to int
            task_byte_to_int = asyncio.create_task(byte_to_int()) # need await???
            # merge users audio
            task_merge = asyncio.create_task(merge_audio())
            # send recording to all clients
            task_send = asyncio.create_task(send_audio(websocket))

            await asyncio.gather(task_receive, task_byte_to_int, task_merge, task_send)

            while True:
                # recieve message
                message = await websocket.recv()
                if message == 'Stop Recording':
                    task_receive.cancel()
                    break

            recording = False

            # send message when all required data is sent to clients???
            await websocket.send('Stop Recording')

async def main():
    async with websockets.serve(handle_server, "localhost", PORT):
        await asyncio.Future()

asyncio.run(main())
