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
stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_play = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)

audio_record = b''
audio_receive = b''

def unmute():
    global audio
    global stream

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)

def mute():
    global audio
    global stream

    stream.stop_stream()
    stream.close()
    audio.terminate()

def record_pc():
    global audio_record
    while stream.is_active():
        data = stream.read(CHUNK)
        audio_record += data

def send_audio(client_socket):
    global audio_record
    while True:
        if audio_record:
            data = audio_record[:CHUNK]
            audio_record = audio_record[CHUNK:]
            client_socket.sendall(data)
        else:
            continue

def receive_audio(client_socket):
    global audio_receive
    while True:
        data = client_socket.recv(CHUNK)
        print(data)
        if not data:
            continue
        else:
            audio_receive += data

def play_audio():
    global audio_receive
    while True:
        if len(audio_receive) >= CHUNK:
            data = audio_receive[:CHUNK]
            audio_receive = audio_receive[CHUNK:]
            stream_play.write(data)
        else:
            continue

def handle_client(client_socket):
    global clients
    with clients_lock:
        clients.add(client_socket)
        print(f"Connected clients: {len(clients)}")

    receive_audio(client_socket)

    with clients_lock:
        clients.remove(client_socket)
        print(f"Connected clients: {len(clients)}")

    client_socket.close()

def main():
    global audio_receive, audio_record

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, int(PORT)))

    record_thread = threading.Thread(target=record_pc)
    play_thread = threading.Thread(target=play_audio)
    task_send_audio = threading.Thread(target=send_audio, args=(client_socket,))
    # need to handle data from different client, better set a dictionary with client as the key, and values to be the buffer
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))

    record_thread.start()
    play_thread.start()
    task_send_audio.start()
    client_thread.start()

    try:
        record_thread.join()
        play_thread.join()
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
