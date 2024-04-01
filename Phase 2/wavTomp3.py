from pydub import AudioSegment

# Load the WAV file
wav_file = AudioSegment.from_wav('Japanese_(Instrumental).wav')

# Export as MP3
wav_file.export('Japanese_(Instrumental).mp3', format='mp3')