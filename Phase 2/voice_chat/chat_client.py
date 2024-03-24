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

def unmute():
    global audio
    global stream

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK)

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
                print(data)
                stream.write(data)

async def main():
    task_send_audio = asyncio.create_task(send_audio())
    task_play_audio = asyncio.create_task(play_audio())

    # Wait for either task to complete
    await asyncio.gather(task_send_audio, task_play_audio)

    # close audio stream when user leave chat room
    mute()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass