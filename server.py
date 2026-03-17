from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import threading
import time

app = Flask(__name__)

latest_image = None

@app.route('/upload', methods=['POST'])
def upload_image():
    global latest_image
    # Get raw data from request
    image_data = request.get_data()
    if image_data:
        # Convert to PIL Image
        image = Image.open(BytesIO(image_data))
        latest_image = image
        return jsonify({'message': 'Image received'}), 200
    else:
        return jsonify({'error': 'No image data'}), 400

@app.route('/stream')
def stream():
    def generate():
        global latest_image
        while True:
            if latest_image:
                # Convert PIL to JPEG
                buf = BytesIO()
                latest_image.save(buf, format='JPEG')
                frame = buf.getvalue()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.1)
    return app.response_class(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Test esp32 camera</title>
    </head>
    <body>
        <h1>Test esp32 camera</h1>
        <img src="/stream" width="640" height="480">
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)