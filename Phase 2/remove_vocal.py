from audio_separator.separator import Separator

# Initialize the Separator class (with optional configuration properties below)
separator = Separator()

# Load a machine learning model (if unspecified, defaults to 'UVR-MDX-NET-Inst_HQ_3.onnx')
separator.load_model()

# Perform the separation on specific audio files without reloading the model
output_files = separator.separate('./songs/Cantonese.mp3')

print(f"Separation complete! Output file(s): {' '.join(output_files)}")