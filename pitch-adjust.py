import librosa
import soundfile as sf

def pitchAdjust(wavfile, factor):
    """
    Change the pitch of audio wav file
    Suggested Range of factor: -12 <= x <= 12
    """
    data, sample_rate = sf.read(wavfile)
    wavShifted = librosa.effects.pitch_shift(data, sr=sample_rate, n_steps=factor)
    
    sf.write("pitchShifted.wav", wavShifted, sample_rate)

# For testing
pitchAdjust('Raw Test Data/16bitM.wav', 6)