from flask import Flask, request, jsonify, Response, render_template, send_from_directory
from utils import process_command
from virtual_map import generate_map
import motor_controller
import time
import os
import logging
import base64

# Log cleanup
class AjaxFilter(logging.Filter):
    def filter(self, record):  
        return not any(x in record.getMessage() for x in ["upload", "map"])

log = logging.getLogger('werkzeug')
log.addFilter(AjaxFilter())

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 # 50 Mb limit

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
    encoded_frame = data['image']
    frame = base64.b64decode(encoded_frame)
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
    code = motor_controller.code
    if code != 1000:
        if code > 90:
            code = 90
        elif code < -90:
            code = -90
        code = -code
    
    print("Sending instructions:", code)
    return str(code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 
