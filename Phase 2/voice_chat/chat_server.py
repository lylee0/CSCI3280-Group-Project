import asyncio
import socket
import websockets
import threading

PORT = 8765
IP = socket.gethostbyname('localhost')
ADDR = (IP, PORT)
CONNECTIONS = set()

async def handle_connection(websocket, path):
    CONNECTIONS.add(websocket)
    print(f'connected client: {CONNECTIONS}')
    try:
        async for audio in websocket:
            print(audio)
            await broadcast(audio, websocket)
    finally:
        CONNECTIONS.remove(websocket)

async def broadcast(audio, sender):
    for peer in CONNECTIONS:
        #if peer != sender:
        await peer.send(audio)

async def main():
    async with websockets.serve(handle_connection, 'localhost', PORT):
        await asyncio.Future()


if __name__ == '__main__':
    print(f'The server has started running')
    asyncio.run(main())