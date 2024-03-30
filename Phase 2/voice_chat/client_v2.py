import socket
import os
import pyaudio
import threading
import datetime
import wave
from pydub import AudioSegment
import websockets
import asyncio
import struct

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024
sample_width = 2

recording = False
chatroom = True

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK, output_device_index=3)


file_start_time = 0

uri = 'ws://'+ "218.250.208.235" +':8765' # How to get server local ip

def listen(userid, roomid):
    loop = asyncio.new_event_loop().run_until_complete(receiveAudio(userid, roomid))
    asyncio.set_event_loop(loop)

async def receiveAudio(userid, roomid):
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            user = data[:2]
            user = struct.unpack('>h', user)[0]
            room = data[2:4]
            room = struct.unpack('>h', room)[0]
            if user != userid and roomid == room:
                data = data[4:]
                stream_output.write(data)


def send(userid, roomid):
    loop = asyncio.new_event_loop().run_until_complete(sendAudio(userid, roomid))
    asyncio.set_event_loop(loop)

def recordVoice():
    while True:
        if stream_input.is_active():
            data = stream_input.read(CHUNK)
            yield data
        else:
            data = bytes([0] * sample_width * CHUNK)
            yield data

async def sendAudio(userid, roomid):
    async with websockets.connect(uri) as websocket:
        for data in recordVoice():
            data = struct.pack('>h', userid) + struct.pack('>h', roomid) + data
            await websocket.send(data)


def main(userid, roomid):
    listen_thread = threading.Thread(target=listen, args=(userid, roomid))
    send_thread = threading.Thread(target=send, args=(userid, roomid))
    listen_thread.start()
    send_thread.start()