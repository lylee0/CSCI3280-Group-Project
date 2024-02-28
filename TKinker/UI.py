import tkinter as tk
from tkinter import ttk
import os
import threading
import playback
import soundRecording
import datetime

global volume, speed, start, selected_file, edit_frames
volume = 1
speed = 1
start = 0
selected_file = None
playback.getPyAudio()

def get_wav_files():
    files = [file for file in os.listdir("recordings") if file.endswith(".wav")]
    return files

def update_listbox():
    listbox.delete(0, tk.END)
    wav_files = get_wav_files()
    for file in wav_files:
        listbox.insert(tk.END, file)
    root.after(1000, update_listbox)

def get_selected_file(event):
    global selected_file
    selected_file = listbox.get(listbox.curselection())
    selected_file = "recordings/" + selected_file
    if selected_file:
        global wav
        wav = playback.getData(selected_file)

def trim():
    global wav, edit_frames
    if selected_file:
        start_end_slider = ttk.Scale(player_frame, from_=0, to=wav["duration"], orient=tk.HORIZONTAL, length=200)
        start_end_slider.set("0")
        start_end_slider.pack()

def saveFile():
    global edit_frames
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recordings/record_{current_time}.wav"
    soundRecording.fileWriting(edit_frames, 1, 44100, filename)

def play_audio():
    global selected_file, wav, stream
    print(f"Playing {selected_file}")
    stream = playback.getStream(wav)
    playback.play(stream, wav, speed, volume, start)
    playback.stop(stream)

'''def time_callback(time):
    # Update the time bar value
    time_bar['value'] = time'''

def play_audio_thread():
    #play_button.config(state=tk.DISABLED)
    threading.Thread(target=play_audio).start()

def record_audio():
    print("Recording audio")
    global streamObj, pObj, frames
    streamObj, pObj = soundRecording.startRecording(44100, 1024, 1, 1) #initiate, para = fs, chunk, channel
    frames = soundRecording.threadWriting(streamObj, 1024) #keep writing, para = stream object, chunk
    update_listbox()

def stop_record():
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"recordings/record_{current_time}.wav"
    global streamObj, pObj, frames
    soundRecording.stopRecording(streamObj, pObj) #stop writing, para = stream object, audio object
    soundRecording.fileWriting(frames, 1, 44100, filename)

def pause_audio():
    print("Pausing audio")
    playback.pause(stream)

'''def on_slider_moved(event):
    playback.pause(stream)
    global start
    start = start_time_slider.get()
    print(start)'''

root = tk.Tk()
root.title("Audio Player")

# Create the file listbox
listbox_frame = ttk.Frame(root)
listbox_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

listbox_label = ttk.Label(listbox_frame, text="WAV Files")
listbox_label.pack()

listbox_scrollbar = ttk.Scrollbar(listbox_frame)
listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(listbox_frame, yscrollcommand=listbox_scrollbar.set)
listbox.pack(fill=tk.BOTH, expand=True)

listbox_scrollbar.config(command=listbox.yview)

wav_files = get_wav_files()
for file in wav_files:
    listbox.insert(tk.END, file)

player_frame = ttk.Frame(root)
player_frame.pack(side=tk.LEFT, padx=10)

play_button = ttk.Button(player_frame, text="Play", command=play_audio_thread)
play_button.pack(pady=5)

record_button = ttk.Button(player_frame, text="Record", command=record_audio)
record_button.pack(pady=5)

pause_button = ttk.Button(player_frame, text="Pause", command=pause_audio)
pause_button.pack(pady=5)

stop_record_button = ttk.Button(player_frame, text="Stop Record", command=stop_record)
stop_record_button.pack(pady=5)

trim_button = ttk.Button(player_frame, text="Audio Trim", command=trim)
trim_button.pack(pady=5)

save_button = ttk.Button(player_frame, text="Save", command=saveFile)
save_button.pack(pady=5)

player_frame = ttk.Frame(root)
player_frame.pack(side=tk.LEFT, padx=10)

listbox.bind("<<ListboxSelect>>", get_selected_file)
#start_time_slider.bind("<<ButtonRelease-1>>", on_slider_moved)

root.mainloop()