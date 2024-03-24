import socket
import asyncio
import websockets
import sys
import pyaudio

PORT = "8765"
HOST = "localhost"
URI = "ws://" + HOST + ":" + PORT

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK)

# def unmute():
#     global audio
#     global stream

#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK)

def mute():
    global audio
    global stream

    stream.stop_stream()
    stream.close()
    audio.terminate()

async def send_audio():
    async with websockets.connect(URI) as websocket:
        while stream.is_active():
            while True:
                data = stream.read(CHUNK)
                await websocket.send(data)

async def play_audio():
    async with websockets.connect(URI) as websocket:
        while True:
            data = await websocket.recv()
            while data:
                stream.write(data)

if __name__ == "__main__":
    asyncio.run(send_audio())