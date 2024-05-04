import requests

voice_commands_api_url = 'http://voice_commands_api:5000/send_audio'

def send_audio_text(text):
    print("Sending audio text:", text)
    # request = { "text": text }
    # requests.post(voice_commands_api_url, json=request)
