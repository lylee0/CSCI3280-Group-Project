import socket
import os
import pyaudio
import threading
import datetime
import wave
from pydub import AudioSegment

PORT = "8765"
HOST = "localhost"

clients_lock = threading.Lock()
clients = set()

FORMAT = pyaudio.paInt16
CHANNEL = 1
RATE = 8000
CHUNK = 1024
sample_width = 2

recording = False
chatroom = True

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)

audio_receive = {}
audio_record = {}

file_start_time = 0

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
    global chatroom, audio_receive, audio_record, sample_width
    while chatroom:
        if stream_input.is_active():
            data = stream_input.read(CHUNK)
            if recording == False:
                audio_receive[client_socket].append(data)
            else:
                audio_receive[client_socket].append(data)
                audio_record[client_socket].append(data)
        else:
            data = bytes([0] * sample_width * CHUNK)
            if recording == False:
                audio_receive[client_socket].append(data)
            else:
                audio_receive[client_socket].append(data)
                audio_record[client_socket].append(data)

'''
    Send client audio to server (only one client)
'''
def send_audio(client_socket):
    global audio_receive
    while chatroom:
        if audio_receive[client_socket]:
            data = audio_receive[client_socket].pop(0)
            client_socket.sendall(data)
        else:
            continue

'''
    Need to receive multiple users audio at the same time (more than one client)
'''
def receive_audio(client_socket):
    global audio_receive, audio_record, file_start_time
    while chatroom:
        data = client_socket.recv(CHUNK)
        check = 1
        if not data:
            continue

        try:
            check = data.decode('utf-8')
        except:
            pass

        if check == "Start Recording":
            recording = True
            file_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            merge_thread = threading.Thread(target=merge_write)
            merge_thread.start()
        elif check == "Stop Recording":
            recording = False
            audio_record[client_socket].append(data.decode('utf-8'))
        else:
            if recording == False:
                audio_receive[client_socket].append(data)
            else:
                audio_receive[client_socket].append(data)
                audio_record[client_socket].append(data)

'''
    Need to play multiple users audio at the same time (more than one client)
'''
def play_audio(client_socket):
    global audio_receive, stream_output
    while chatroom:
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

'''
    Write the wav file header (all clients will write at the same time)
'''
def write_file_header():
    global CHANNEL, RATE, sample_width, f
    # open file here
    f.setnchannels(CHANNEL)
    f.setsampwidth(sample_width) # 2 bytes
    f.setframerate(RATE)

'''
    Merge and write all users audio
'''
def merge_write():
    global audio_record, sample_width, f
    output_file = f"recording_{file_start_time}.wav"
    if (not os.path.exists(output_file)) and (file_start_time != 0):
        f = wave.open(output_file, 'wb')
        write_file_header()
    while True:
        audio_zero = bytes([0] * sample_width * CHUNK)
        audio_merge = AudioSegment(audio_zero,sample_width=2,channels=CHANNEL,frame_rate=RATE)
        all_clients = audio_record.keys()
        for client in all_clients:  # not sure if need to change to 
            if audio_record[client] == []:
                continue
            audio_bytes = audio_record[client].pop(0)
            try:
                if audio_bytes.decode('utf-8') == "Stop Recording":
                    f.flush()
                    f.close()
                    break
            except:
                pass
            audio = AudioSegment(audio_bytes,sample_width=2,channels=CHANNEL,frame_rate=RATE)
            audio_merge = audio.overlay(audio_merge)

        #print(audio_merge.raw_data)
        f.writeframesraw(audio_merge.raw_data)

def send_start(client_socket):
    client_socket.sendall("Start Recording".encode('utf-8')) # only send to server

def send_stop(client_socket):
    client_socket.sendall("Stop Recording".encode('utf-8')) # only send to server

def main():
    global audio_receive, audio_record, audio_write

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, int(PORT)))

    audio_receive[client_socket] = []
    audio_record[client_socket] = []
    #audio_write = b''

    record_thread = threading.Thread(target=record_pc, args=(client_socket,))
    #play_thread = threading.Thread(target=play_audio)
    task_send_audio = threading.Thread(target=send_audio, args=(client_socket,))
    # need to handle data from different client, better set a dictionary with client as the key, and values to be the buffer
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    #merge_thread = threading.Thread(target=merge_write)

    record_thread.start()
    #play_thread.start()
    task_send_audio.start()
    client_thread.start()
    #merge_thread.start()

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
