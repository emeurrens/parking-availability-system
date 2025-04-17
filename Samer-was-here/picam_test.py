#!/usr/bin/env python3
"""
High‑quality MJPEG stream from Picamera2 still captures.

• Uses the same still‑capture configuration you provided
  (RGB888, full sensor size, custom controls).
• Frames are captured in a background thread so the web
  server stays responsive.
• Adjust the sleep in `generate()` if you want a higher
  or lower preview rate – it does **not** affect capture
  quality, only how often we push the latest JPEG out.
"""

from flask import Flask, Response
from picamera2 import Picamera2
from libcamera import controls
import cv2
import threading
import time

# ------------------------------------------------------------------
# Camera initialisation – identical quality path to your take_pic()
# ------------------------------------------------------------------
picam2 = Picamera2()

camera_config = picam2.create_still_configuration(
    main={
        "size": picam2.camera_properties["PixelArraySize"],  # full sensor res
        "format": "RGB888",
    },
    controls={
        "AwbMode": controls.AwbModeEnum.Indoor,
        "AwbEnable": True,
        "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast,
        "Brightness": 0.23,
        "Contrast": 1.2,
        "Sharpness": 1.5,
        "ExposureTime": 6000,      # µs
        "AnalogueGain": 1.0,
        "Saturation": 1.2,
    },
)
picam2.align_configuration(camera_config)
picam2.configure(camera_config)
picam2.start()                     # one‑off start‑up

# ------------------------------------------------------------------
# Background capture loop
# ------------------------------------------------------------------
latest_jpeg = None
frame_lock = threading.Lock()

def capture_worker():
    global latest_jpeg
    while True:
        # Grab full‑quality RGB frame
        rgb = picam2.capture_array()
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        ok, jpeg = cv2.imencode(".jpg", bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if ok:
            with frame_lock:
                latest_jpeg = jpeg.tobytes()

capture_thread = threading.Thread(target=capture_worker, daemon=True)
capture_thread.start()

# ------------------------------------------------------------------
# Flask app – serves the most recent JPEG as MJPEG
# ------------------------------------------------------------------
app = Flask(__name__)

def generate():
    """Yields multipart MJPEG stream."""
    while True:
        with frame_lock:
            frame = latest_jpeg
        if frame is None:
            time.sleep(0.05)
            continue

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" +
               frame +
               b"\r\n")
        time.sleep(0.05)           # ~20 fps preview (tweak as desired)

@app.route("/")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    # threaded=True lets Flask serve multiple viewers simultaneously
    app.run(host="0.0.0.0", port=5000, threaded=True)
