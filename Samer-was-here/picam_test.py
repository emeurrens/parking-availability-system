from flask import Flask, Response
import cv2
import subprocess
import numpy as np

app = Flask(__name__)
width, height = 2560, 1080
frame_size = int(width * height * 1.5)

command = [
    "libcamera-vid", "--width", str(width), "--height", str(height),
    "--codec", "yuv420", "--framerate", "30",
    "--nopreview", "-t", "0", "-o", "-"
]
process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

def generate():
    while True:
        raw = process.stdout.read(frame_size)
        if len(raw) != frame_size:
            continue
        yuv = np.frombuffer(raw, dtype=np.uint8).reshape((int(height * 1.5), width))
        bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
        _, jpeg = cv2.imencode('.jpg', bgr)
        frame = jpeg.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host='0.0.0.0', port=5000)
