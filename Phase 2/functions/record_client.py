import asyncio
import websockets
import numpy as np
import cv2
import pyautogui
import pygetwindow as gw
import datetime
import wave

audio_merged = []
recording = False
channel = 1
samp_width = 2
fs = 44100
block_align = 2 #???
PORT = "8765"
HOST = "localhost"
URI = "ws://" + HOST + ":" + PORT

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
async def handle_server():
    global f, recording, audio_merged
    async with websockets.connect(URI) as websocket:
        #await start_recording(websocket) # for testing
        async for message in websocket:
            if message == "Start Recording":

                # write file header
                current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"./recordings/recording_{current_time}.wav"
                #global f
                f = wave.open(output_file, 'wb')
                write_file_header(f, channel, samp_width, fs)
                audio_merged = []

                # recieve merged audio data from server
                task_receive = asyncio.create_task(receive_bytes(websocket))
                # write merged audio data to local file
                task_write = asyncio.create_task(write_file(f))

                await asyncio.gather(task_receive, task_write)

                while True:
                    # recieve message
                    message = await websocket.recv()
                    if message == 'Stop Recording':
                        #task.cancel()
                        break
                recording = False
                # need to wait till all data is sent to clients
                f.flush()
                f.close()

asyncio.run(handle_server())
