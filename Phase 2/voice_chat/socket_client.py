import socket
import struct
import os
import pyaudio
import threading
import datetime
import wave

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

audio = pyaudio.PyAudio()
stream_input = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=1)
stream_output = audio.open(format=FORMAT, channels=CHANNEL, rate=RATE, output=True, frames_per_buffer=CHUNK)

audio_receive = {}
audio_record = {}
audio_write = b''

file_start_time = 1

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
    global audio_receive, audio_record, file_start_time
    while True:
        data = client_socket.recv(CHUNK)
        # if data == "Start Recording", record the time and save in file_start_time, recording == True
        # file_start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # if data == "Stop Recording", recording == False
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

'''
    Write the wav file header (all clients will write at the same time)
'''
def write_file_header(f):
    global CHANNEL, RATE, sample_width
    # open file here
    f.setnchannels(CHANNEL)
    f.setsampwidth(sample_width) # 2 bytes
    f.setframerate(RATE)

'''
    Write wav file
'''
def write_file():
    global audio_write, file_start_time
    # only open the file and write the header if it does not exit, record the time received start recording
    # can also add a path
    output_file = f"recording_{file_start_time}.wav"
    if not os.path.exists(output_file):
        f = wave.open(output_file, 'wb')
        write_file_header(f)
    while True: # may need to change, maybe the last element in the list???
        if audio_write:
            data = audio_write[:CHUNK]
            audio_write = audio_write[CHUNK:]
            f.write(data)
            # need to flush the data
            # when to close the file?
        else:
            continue

'''
    Merge all users audio
'''
def merge_audio():
    global audio_record, audio_write, sample_width
    while True:
        #all_audio = audio_record.values()
        #all_audio = list(all_audio)
        all_clients = audio_record.keys()
        #if all_audio:
        compare = []
        for client in all_clients:  # not sure if need to change to 
            audio_bytes = audio_record[client][:sample_width]
            compare.append(struct.unpack('<h', audio_bytes)[0])
            audio_record[client] = audio_record[client][sample_width:]
        audio_write += max(compare)
        #else: 
            #continue

def send_start(client_socket):
    client_socket.sendall("Start Recording") # only send to server

def send_stop(client_socket):
    client_socket.sendall("Stop Recording") # only send to server

def main():
    global audio_receive, audio_record, audio_write

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, int(PORT)))

    audio_receive[client_socket] = []
    audio_record[client_socket] = b''
    audio_write = b''

    record_thread = threading.Thread(target=record_pc, args=(client_socket,))
    #play_thread = threading.Thread(target=play_audio)
    task_send_audio = threading.Thread(target=send_audio, args=(client_socket,))
    # need to handle data from different client, better set a dictionary with client as the key, and values to be the buffer
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    merge_thread = threading.Thread(target=merge_audio)
    write_thread = threading.Thread(target=write_file) # run the infinite loop???

    record_thread.start()
    #play_thread.start()
    task_send_audio.start()
    client_thread.start()
    merge_thread.start()
    write_thread.start()

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
