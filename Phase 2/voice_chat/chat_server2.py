import asyncio
import socket
import websockets
import threading
import pyaudio

PORT = 8765
IP = socket.gethostbyname('localhost')
ADDR = (IP, PORT)
CONNECTIONS = set()

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 44100
CHUNK = 1024

audio_play = pyaudio.PyAudio()
stream_play = audio_play.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)
audio_receive = []

async def handle_connection(websocket, path):
    CONNECTIONS.add(websocket)
    print(f'connected client: {CONNECTIONS}')
    try:
        async for audio in websocket:
            audio_receive.append(audio)
            print(audio)
            await broadcast(websocket)
    finally:
        CONNECTIONS.remove(websocket)

async def broadcast(sender):
    for peer in CONNECTIONS:
        #if peer != sender:
        await peer.send(audio_receive.pop(0))

async def main():
    async with websockets.serve(handle_connection, 'localhost', PORT):
        await asyncio.Future()


if __name__ == '__main__':
    print(f'The server has started running')
    asyncio.run(main())
