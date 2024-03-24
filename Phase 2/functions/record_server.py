import pyaudio
import asyncio
import websockets
import numpy as np
import cv2
import pyautogui
import pygetwindow as gw
import threading
import time
import datetime
import struct
import sys
import wave
from pydub import AudioSegment


clients = set() # a list?
audio_bytes = []
audio_array = [] # 2d numpy array
audio_merged = [] # int
recording = False
channel = 1
samp_width = 2
fs = 44100
block_align = 2 #???


'''
    Recieve audio from client
'''
async def receive_audio(websocket, client_id):
    global clients

    async for message in websocket:
        if recording:
            audio_bytes[client_id].append(message)

'''
    Merge all users audio, and call the write file function
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
    Convert byte to integer
'''
async def byte_to_int():
    global audio_bytes, audio_array
    # length of audio_bytes == number of users
    while audio_bytes:
        for bytes in audio_bytes:
            pass

'''
    Send merged audio data to clients
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

    client_id = id(websocket)

    async for message in websocket:
        if message == "Start Recording":
            recording = True
            audio_bytes = []
            audio_array = [] # 2d numpy array
            audio_merged = []

            await websocket.send('Start Recording')

            task = asyncio.create_task(receive_audio(websocket, client_id)) # recieve audio from clients
            # convert audio to int
            await byte_to_int() # need await???
            # merge users audio
            await merge_audio()
            # send recording to clients
            await send_audio(websocket)
            # write audio
            #await write_file()
            
            while True:
                # recieve message
                message = await websocket.recv()
                if message == 'Stop Recording':
                    task.cancel()
                    break

            recording = False

            # send message when all required data is sent to clients???
            await websocket.send('Stop Recording')
