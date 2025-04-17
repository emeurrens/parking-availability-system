# from flask import Flask, Response
# from picamera2 import picamera2, Preview
# import cv2
# import subprocess
# import numpy as np

# app = Flask(__name__)
# width, height = 2560, 1440
# frame_size = int(width * height * 1.0)

# command = [
#     "libcamera-vid", "--width", str(width), "--height", str(height),
#     "--codec", "yuv420", "--framerate", "30",
#     "--nopreview", "-t", "0", "-o", "-"
# ]
# process = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

# def generate():
#     while True:
#         raw = process.stdout.read(frame_size)
#         if len(raw) != frame_size:
#             continue
#         yuv = np.frombuffer(raw, dtype=np.uint8).reshape((int(height * 1.0), width))
#         bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
#         _, jpeg = cv2.imencode('.jpg', bgr)
#         frame = jpeg.tobytes()
#         yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/')
# def video_feed():
#     return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

# app.run(host='0.0.0.0', port=5000)

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import cv2
import socket
from threading import Event

cam = Picamera2()
video_config = cam.create_video_configuration(main={'size': cam.camera_properties['PixelArraySize'], 'format':'RGB888',},     # Main stream resolution
                                              lores={'size': (640,480), 'format':'YUV420'},                                   # Low res stream resolution
                                              raw={},                                                                         # Raw stream resolution default
                                              controls={},
                                              encode='main')
cam.configure(video_config)

encoder = MJPEGEncoder()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 5000))

    while True:
        sock.listen()
        conn, addr = sock.accept() # client connected

        output = FileOutput(conn.makefile('wb'))
        event = Event()
        output.error_callback = lambda e: event.set()
        
        cam.start_recording(encoder, output)

        event.wait()

        cam.stop_recording()