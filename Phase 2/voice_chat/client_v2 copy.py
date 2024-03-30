import socket
import os
import pyaudio
import threading
import datetime
import wave
from pydub import AudioSegment
import websockets
import asyncio
import time
import base64
import json
import struct

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024
sample_width = 2

recording = False
chatroom = True

UserID = 1

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK, output_device_index=3)


file_start_time = 0

uri = 'ws://'+ "218.250.208.235" +':8765' # How to get server local ip

def listen():

    loop = asyncio.new_event_loop().run_until_complete(receiveAudio())
    asyncio.set_event_loop(loop)

async def receiveAudio():
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            user = data[:2]
            user = struct.unpack('>h', user)[0]
            if user != UserID:
                data = data[2:]
                stream_output.write(data)


def send():
    loop = asyncio.new_event_loop().run_until_complete(sendAudio())
    asyncio.set_event_loop(loop)

def recordVoice():
    while True:
        data = stream_input.read(CHUNK)
        yield data

async def sendAudio():
    async with websockets.connect(uri) as websocket:
        for data in recordVoice():
            data = struct.pack('>h', UserID) + data
            await websocket.send(data)



listen_thread = threading.Thread(target=listen, args=())
send_thread = threading.Thread(target=send, args=())
listen_thread.start()
send_thread.start()