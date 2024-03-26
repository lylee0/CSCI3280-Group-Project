import socket
import asyncio
import sys
import pyaudio
import threading

PORT = "8765"
HOST = "localhost"

clients_lock = threading.Lock()
clients = set()

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 8000
CHUNK = 1024

recording = False

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)

audio_receive = {}
audio_record = {}

def unmute():
    global audio, stream_input

    audio = pyaudio.PyAudio()
    stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)

def mute():
    global audio, stream_input

    stream_input.stop_stream()
    stream_input.close()
    audio.terminate()

'''
    Record client audio from device (only one client)
'''
def record_pc(client_socket):
    global audio_receive, audio_record
    while stream_input.is_active():
        data = stream_input.read(CHUNK)
        if recording == False:
            audio_receive[client_socket].append(data)
        else:
            audio_receive[client_socket].append(data)
            audio_record[client_socket] += data

'''
    Send client audio to server (only one client)
'''
def send_audio(client_socket):
    global audio_receive
    while True:
        if audio_receive[client_socket]:
            data = audio_receive[client_socket].pop(0)
            client_socket.sendall(data)
        else:
            continue

'''
    Need to receive multiple users audio at the same time (more than one client)
'''
def receive_audio(client_socket):
    global audio_receive, audio_record
    while True:
        data = client_socket.recv(CHUNK)
        #print(data)
        if not data:
            continue
        else:
            if recording == False:
                audio_receive[client_socket].append(data)
            else:
                audio_receive[client_socket].append(data)
                audio_record[client_socket] += data

'''
    Need to play multiple users audio at the same time (more than one client)
'''
def play_audio(client_socket):
    global audio_receive, stream_output
    while True:
        if audio_receive[client_socket]:
            data = audio_receive[client_socket].pop(0)
            stream_output.write(data)
        else:
            continue

'''
    Check how many clients
'''
def handle_client(client_socket):
    global clients
    with clients_lock:
        clients.add(client_socket)
        print(f"Connected clients: {len(clients)}")

    receive_audio(client_socket)
    play_audio(client_socket) # not sure

    with clients_lock:
        clients.remove(client_socket)
        print(f"Connected clients: {len(clients)}")

    client_socket.close()

def main():
    global audio_receive, audio_record

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, int(PORT)))

    audio_receive[client_socket] = []
    audio_record[client_socket] = b''

    record_thread = threading.Thread(target=record_pc, args=(client_socket,))
    #play_thread = threading.Thread(target=play_audio)
    task_send_audio = threading.Thread(target=send_audio, args=(client_socket,))
    # need to handle data from different client, better set a dictionary with client as the key, and values to be the buffer
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))

    record_thread.start()
    #play_thread.start()
    task_send_audio.start()
    client_thread.start()

    try:
        record_thread.join()
        #play_thread.join()
        task_send_audio.join()
        client_thread.join()
    except KeyboardInterrupt:
        pass

    client_socket.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
