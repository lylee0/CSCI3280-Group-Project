import socket
import asyncio
import websockets
import sys
import pyaudio
import threading

PORT = "8765"
HOST = "localhost"
URI = "ws://" + HOST + ":" + PORT

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024

audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index = 1)
stream_play = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)

audio_record = []
audio_receive = []

def unmute():
    global audio
    global stream

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index = 1) #, input_device_index = 1

def mute():
    global audio
    global stream

    stream.stop_stream()
    stream.close()
    audio.terminate()

def record_pc():
    while stream.is_active():
        data = stream.read(CHUNK)
        audio_record.append(data)

async def send_audio(websocket):
    while True:
        if audio_record:
            await websocket.send(audio_record.pop(0))
        else:
            continue

async def receive_audio(websocket):
    while True:
        async for data in websocket:
            audio_receive.append(data)

def play_audio():
    while True:
        if audio_receive:
            print(audio_receive)
            stream_play.write(audio_receive.pop(0))
            
            #data = await websocket.recv()
        else:
            continue


async def main():
    async with websockets.connect(URI) as websocket:
        record_thread = threading.Thread(target=record_pc)
        play_thread = threading.Thread(target=play_audio)
        task_send_audio = asyncio.create_task(send_audio(websocket))
        task_receive_audio = asyncio.create_task(receive_audio(websocket))
        record_thread.start()
        play_thread.start()
        # Wait for either task to complete
        await asyncio.gather(task_send_audio, task_receive_audio)

    # close audio stream when user leave chat room
    mute()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
