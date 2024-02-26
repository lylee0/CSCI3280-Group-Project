import wave

def audio_trim(input_file, start_time, end_time):
    """
    Modify the start and end time of the audio
    Parameter: 
        input_file - file to be trimmed
        start_time - new start time of the audio (in seconds)
        end_time - new end time of the audio (in seconds)
    Output:
        a trimmed audio wav file
    """
    with wave.open(input_file, 'rb') as wav_in:
        with wave.open('audio_trimmed.wav', 'wb') as wav_out:
            # Set the output file parameters to match the input file
            wav_out.setparams(wav_in.getparams())

            # Calculate the start and end sample positions based on the input times
            frame_rate = wav_in.getframerate()
            start_position = int(start_time * frame_rate)
            end_position = int(end_time * frame_rate)

            # Get the start position in the input file
            wav_in.setpos(start_position)

            # Read and write audio frames from the input file to the output file
            num_frames = end_position - start_position
            frames = wav_in.readframes(num_frames)
            wav_out.writeframes(frames)
    wav_in.close()
    wav_out.close()
# For testing
audio_trim('Raw Test Data/32bitS.wav', 1.0, 2.0)
