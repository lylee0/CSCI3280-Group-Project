import speech_recognition as sr

def speechToText(path):                                    
    r = sr.Recognizer()                                                       
    audio = sr.AudioFile(path)
    with audio as source:
        audio = r.record(source)    
        print(source)              
        result = r.recognize_google(audio)
    return result

print(speechToText('example.wav'))