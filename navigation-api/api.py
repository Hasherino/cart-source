from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from utils import process_command, check_time
from virtual_map import generate_map, move
import motor_controller
import time
import os
import logging
import base64
from request_interface import send_audio_text

class AjaxFilter(logging.Filter):
    def filter(self, record):  
        return not any(x in record.getMessage() for x in ["upload", "map"])

log = logging.getLogger('werkzeug')
log.addFilter(AjaxFilter())

app = Flask(__name__)
frame = None
markers = None
cart_image_pos = None
heading = None
initialized = False
released_time = None

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/upload', methods=['PUT'])
def upload():
    global frame, markers, cart_image_pos, heading
    data = request.get_json()
    encoded = data['image']
    frame = base64.b64decode(encoded)
    markers = data['markers']
    heading = data['cartHeading']
    cart_image_pos = (data['cartX'], data['cartY'])
    return "OK"

def gen():
    while True:
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'\r\n' + frame + b'\r\n')
        time.sleep(0.04)

@app.route('/video')
def video():
    if frame:
        return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return ""
    
@app.route('/map')
def get_map():
    generate_map(markers, cart_image_pos, heading)
    global released_time, initialized
    if released_time:
        stopping = check_time(released_time)
        if stopping:
            released_time = None
    return Response(open('map.png', 'rb').read(), mimetype='image/png')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/process_command', methods=['POST'])
def process():
    request_data = request.get_json()
    print("Received request with payload:", request_data)

    command = request_data.get('command')
    product = request_data.get('product')

    response = process_command(command, product)()

    print("Sending response:", response)
    return jsonify(response)

@app.route('/get_instructions', methods=['GET'])
def instructions():
    print("Sending instructions:", motor_controller.code)
    return str(motor_controller.code)

@app.route('/move', methods=['POST'])
def move_endpoint():
    request_data = request.get_json()
    print("Received request with payload:", request_data)

    command = request_data.get('command')

    res = move(command)
    
    if res == 1:
        response = "Moving cart:", command
    else:
        response = "Invalid move command:", command
    print(response)
    return jsonify(response)

@app.route('/set_handlebar', methods=['POST'])
def handlebar_state():
    request_data = request.get_json()
    print("Received request with payload:", request_data)

    state = request_data.get('state')
    state = state[2]
    global released_time, initialized
    
    if state == "1" and not initialized:
        send_audio_text("Hello, what would you like to buy?")
        initialized = True
    else:
        released_time = time.time()

    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
