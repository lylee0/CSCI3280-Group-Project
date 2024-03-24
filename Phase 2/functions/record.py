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
audio = []
recording = False
channel = 1
samp_width = 2
fs = 44100
for client in clients:
    audio.append([])

async def merge_audio(audio, output_file):
    # audio is a 2d np array
    #global audio
    if audio:
        compare = []
        for data in audio:
            compare.append(data.pop(0))
        maximum = max(compare)
        # to bytes
        write_file(maximum, output_file)

def write_file(data, output_file):
    output_file.write(data)

async def receive_audio(websocket, client_id):
    global clients

    async for message in websocket:
        if recording:
            audio[client_id].append(message)

'''
    Send wav file to clients
'''
async def send_file(websocket, output_file):
    with open(output_file, 'rb') as f:
        data = f.read()
        await websocket.send(data)

def write_file_header(f, channel, samp_width, fs):
    f.setnchannels(channel)
    f.setsampwidth(samp_width)
    f.setframerate(fs)
    return f


async def handel_server(websocket, path): # client connects to server
    global clients, audio, recording

    client_id = id(websocket)

    async for message in websocket:
        if message == "Start Recording":
            recording = True

            await websocket.send('Start Recording')

            # open file
            output_file = "test.wav" # current time
            f = wave.open(output_file, 'wb')
            write_file_header(f, channel, samp_width, fs)

            task = asyncio.create_task(receive_audio(websocket, client_id))

            
            while True:
                message = await websocket.recv()
                if message == 'Stop Recording':

                    break

            recording = False

            await websocket.send('Stop Recording')
            task.cancel()
            f.flush()
            f.close()

            # send recording to clients
            await send_file(websocket, output_file)


