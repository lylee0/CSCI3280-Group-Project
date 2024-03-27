import socket
import threading
import pyaudio

PORT = 8765
IP = socket.gethostbyname('localhost')
ADDR = (IP, PORT)
CONNECTIONS = set()

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 8000
CHUNK = 1024
audio_receive = [] # only store 1 client?

def handle_connection(client_socket, address):
    global audio_receive
    CONNECTIONS.add(client_socket)
    audio_receive = []
    print(f'connected client: {address}')
    receive_thread = threading.Thread(target=receive_audio, args=(client_socket,))
    broadcast_thread = threading.Thread(target=broadcast, args=(client_socket,))
    receive_thread.start()
    broadcast_thread.start()
    #receive_audio(client_socket)

'''
    Receive audio from client (only one client)
'''
def receive_audio(client_socket):
    global audio_receive
    while True:
        data = client_socket.recv(CHUNK)
        # if receive message "Start Recording", send "Start Recording to all clients"
        # if receive message "Stop Recording", send "Stop Recording to all clients"
        audio_receive.append(data)
        #print(data)

'''
    Send the received audio to all clients except the sender (handle data only from one client)
'''
def broadcast(sender):
    global audio_receive
    while True:
        if audio_receive:
            data = audio_receive.pop(0)
            for client_socket in CONNECTIONS:
                if client_socket != sender:
                    client_socket.sendall(data)
                #print(data)
        else:
            continue

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDR)
    server_socket.listen()

    print(f'Serving on {ADDR}')

    while True:
        client_socket, address = server_socket.accept()
        client_thread = threading.Thread(target=handle_connection, args=(client_socket, address))
        client_thread.start()

if __name__ == '__main__':
    print(f'The server has started running')
    main()
