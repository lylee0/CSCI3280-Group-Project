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
import wave
from pydub import AudioSegment

audio_merged = []
recording = False
channel = 1
samp_width = 2
fs = 44100
block_align = 2 #???

'''
    Start Recording (one client)
'''
# call this function when click record
async def start_recording(websocket):
    #global recording
    #recording = True
    # send start message to server
    await websocket.send("Start Recording")

'''
    Stop Recording (one client)
'''
async def stop_message(websocket):
    await websocket.send("Stop Recording")

'''
    Receive audio bytes from server (all clients)
'''
async def receive_bytes(websocket):
    global audio_merged
    async for message in websocket:
        if recording:
            audio_merged.append(message)

'''
    Write samples to wav file (all clients)
'''
async def write_file(output_file):
    global audio_merged

    while audio_merged:
        for data in audio_merged:
            output_file.writeframes(data.astype(np.int32).tobytes())
            audio_merged.pop(0)

'''
    Write the wav file header (all clients)
'''
def write_file_header(f, channel, samp_width, fs):
    f.setnchannels(channel)
    f.setsampwidth(samp_width) # 4 bytes
    f.setframerate(fs)
    #return f

'''
    Handle messages from server (all clients)
'''
async def handle_server(path):
    global f, recording, audio_merged
    async with websockets.connect(path) as websocket:
        async for message in websocket:
            if message == "Start Recording":

                # write file header
                current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"./recordings/recording_{current_time}.wav"
                global f
                f = wave.open(output_file, 'wb')
                write_file_header(f, channel, samp_width, fs)
                audio_merged = []

                # recieve merged audio data from server
                await receive_bytes(websocket)
                # write merged audio data to local file
                await write_file(f)

                while True:
                    # recieve message
                    message = await websocket.recv()
                    if message == 'Stop Recording':
                        #task.cancel()
                        break
                recording = False
                f.flush()
                f.close()

if __name__ == "_main_":
    path = ""
    asyncio.run(handle_server(path))
