from db_interface import get_product
import speech_recognition as sr
from request_interface import send_instructions
from gtts import gTTS
from pydub import AudioSegment
import time

MP3_FILE = "output.mp3"
WAVE_FILE = "result.wav"

r = sr.Recognizer()

def transcribe(audio_file):
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio) 
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service:", e )

def identify_command(text, model, vectorizer):
    commands = ["Go", "Finish", "Cancel", "None"]
    features = vectorizer.transform([text])

    predicted_label = model.predict(features)[0] - 1
    predicted_command = commands[predicted_label]

    return predicted_command

def process_command(command, text):
    return {
        "Go": lambda: go(command, text),
        "Finish": lambda: stop(command),
        "Cancel": lambda: stop(command),
        "None": lambda: none()
    }.get(command)

def go(command, text):
    product = identify_product(text)
    if product is None:
        return none()
    
    request = { 'command': command, 'product': product }
    send_instructions(request)
    return "Going to " + product

def stop(command):
    request = { 'command': command, 'product': None }
    send_instructions(request)
    return "Stopping"

def none():
    return "Command not recognized"
            
def identify_product(text):
    product = get_product(text)
    if product is None:
        print("Product not identified")
        return None
    return product[1]

def make_tts(tts_text, timestamp = False):
    tts = gTTS(text=tts_text, lang='en', tld='com.au')
    tts.save(MP3_FILE)

    sound = AudioSegment.from_mp3(MP3_FILE) 

    file_name = WAVE_FILE
    if timestamp:
        file_name = file_name + str(time.time())

    sound.export(file_name, format="wav") 

    return file_name