import pickle
from flask import Flask, request, send_file, make_response
from utils import transcribe, identify_command, process_command, make_tts
from request_interface import send_audio
from time import sleep

# Load the model
with open('model/command_model.pkl', 'rb') as f:
    model = pickle.load(f)

# Load the vectorizer
with open('model/command_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

app = Flask(__name__)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio_file = request.files['audio']
    text = transcribe(audio_file)

    if text is None:
        tts_text = "Zero words received"
    else:
        print("Received audio file with transcription:", text)
        command = identify_command(text, model, vectorizer)
        tts_text = process_command(command, text)()

    print("TTS:", tts_text)
    tts = make_tts(tts_text)

    response = make_response(send_file(tts, mimetype='audio/wav'))
    response.headers['Content-Disposition'] = 'attachment; filename=tts_output.wav'
    return response

@app.route('/send_audio', methods=['POST'])
def send_audio_to_speaker():
    request_data = request.get_json()
    print("Received audio request with payload:", request_data)

    tts_text = request_data.get('text')
    tts = make_tts(tts_text, timestamp=True)

    while True:
        was_accepted = send_audio(tts)
        if was_accepted:
            break
        else:
            sleep(1)

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
