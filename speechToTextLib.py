import speech_recognition as sr

def speechToText(path):                                    
    r = sr.Recognizer()                                                       
    audio = sr.AudioFile(path)
    with audio as source:
        audio = r.record(source)    
        print(source)              
        result = r.recognize_google(audio)
    return result

if __name__ == "__main__":
    print(speechToText('example.wav'))