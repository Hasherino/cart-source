import requests

navigation_api_url = 'http://navigation_api:5000/process_command'
speaker_api_url = 'http://192.168.1.154:4041/send_audio'

def send_instructions(request):
    requests.post(navigation_api_url, json=request)

def send_audio(file_name):
    with open(file_name, 'rb') as file:
        files = {'audio': file}
        res = requests.post(speaker_api_url, files=files)
        if res.status_code == 420:
            return False
        return True
