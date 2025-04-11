import os
import cv2
import time
import uuid
import base64
import json
import logging
import threading
import queue
import requests
import numpy as np
from openvino.runtime import Core
from typing import Dict, List, Tuple, Optional
import shutil
import subprocess
import select
from datetime import datetime
from collections import deque  # NEW: for FPS tracking

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "vehicle_model_path": "yolo11n_openvino_model/yolo11n.xml",
    "license_plate_model_path": "license_plate_detector_openvino_model/license_plate_detector.xml",
    "frames_dir": "./frames",
    "vehicle_classes": [2, 3, 5, 7],
    "track_timeout": 5.0,
    "api_endpoint": "https://e5v8r7gy4l.execute-api.us-east-2.amazonaws.com/processCar",
    "lot_id": "d65ef517-c64f-4c54-9dd0-706cd0d184ee",
    "source": 0
}

def postprocess_yolo_output(output: np.ndarray, conf_thresh=0.4, iou_thresh=0.5, input_shape=(640, 640), orig_shape=(480, 640)):
    predictions = output.squeeze(0).T
    boxes = predictions[:, :4]
    objectness = predictions[:, 4:5]
    class_probs = predictions[:, 5:]

    scores = objectness * class_probs
    class_ids = np.argmax(scores, axis=1)
    confidences = np.max(scores, axis=1)

    mask = confidences > conf_thresh
    boxes = boxes[mask]
    confidences = confidences[mask]
    class_ids = class_ids[mask]

    if len(boxes) == 0:
        return []

    boxes_xyxy = np.zeros_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2

    input_h, input_w = input_shape
    orig_h, orig_w = orig_shape
    scale = min(input_w / orig_w, input_h / orig_h)
    boxes_xyxy /= scale

    indices = cv2.dnn.NMSBoxes(
        bboxes=boxes_xyxy.tolist(),
        scores=confidences.tolist(),
        score_threshold=conf_thresh,
        nms_threshold=iou_thresh
    )

    final_detections = []
    for i in indices.flatten():
        final_detections.append((
            boxes_xyxy[i], confidences[i], class_ids[i]
        ))

    return final_detections

class VehicleTracker:
    def __init__(self, config: Dict):
        self.config = config
        os.makedirs(self.config["frames_dir"], exist_ok=True)

        core = Core()
        logger.info("Loading vehicle detection model...")
        self.vehicle_model = core.read_model(model=self.config["vehicle_model_path"])
        self.vehicle_compiled = core.compile_model(self.vehicle_model, "CPU")
        self.vehicle_input_layer = self.vehicle_compiled.input(0)

        logger.info("Loading license plate detection model...")
        self.plate_model = core.read_model(model=self.config["license_plate_model_path"])
        self.plate_compiled = core.compile_model(self.plate_model, "CPU")
        self.plate_input_layer = self.plate_compiled.input(0)

        self.active_tracks = {}
        self.completed_tracks_queue = queue.Queue()
        self.shutdown_flag = threading.Event()
        self.processing_thread = threading.Thread(target=self._process_completed_tracks, daemon=True)
        self.processing_thread.start()

        self.frame_times = deque(maxlen=3000)  # NEW: for FPS tracking

    def start_capture(self):
        width, height = 640, 480
        self.frame_size = int(width * height * 1.5)

        command = [
            "libcamera-vid",
            "--width", str(width),
            "--height", str(height),
            "--codec", "yuv420",
            "--framerate", "30",
            "--nopreview",
            "-t", "0",
            "-o", "-"
        ]

        try:
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=10**8
            )
            logger.info("Started libcamera-vid subprocess")

            def _log_stderr(proc):
                for line in iter(proc.stderr.readline, b''):
                    logger.warning(f"[libcamera-vid] {line.decode().strip()}")

            threading.Thread(target=_log_stderr, args=(self.process,), daemon=True).start()
            return True
        except Exception as e:
            logger.error(f"Failed to start libcamera-vid: {e}")
            return False

    def preprocess(self, frame: np.ndarray, shape=(640, 640)) -> np.ndarray:
        image = cv2.resize(frame, shape)
        image = image.transpose(2, 0, 1)
        image = image[np.newaxis, :]
        return image.astype(np.float32) / 255.0

    def infer_vehicle(self, frame: np.ndarray):
        input_tensor = self.preprocess(frame)
        results = self.vehicle_compiled([input_tensor])[self.vehicle_compiled.outputs[0]]
        return results

    def run(self):
        if not self.start_capture():
            return

        try:
            while not self.shutdown_flag.is_set():
                if self.process.poll() is not None:
                    logger.error("libcamera-vid subprocess has exited unexpectedly")
                    break

                rlist, _, _ = select.select([self.process.stdout], [], [], 2.0)
                if not rlist:
                    logger.warning("Timeout waiting for camera frame")
                    continue

                raw_frame = self.process.stdout.read(self.frame_size)
                if len(raw_frame) != self.frame_size:
                    logger.warning("Incomplete frame received")
                    continue

                yuv = np.frombuffer(raw_frame, dtype=np.uint8).reshape((int(480 * 1.5), 640))
                frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

                start_time = time.time()
                detections_raw = self.infer_vehicle(frame)
                inference_time = (time.time() - start_time) * 1000
                self.frame_times.append(time.time())

                logger.info(f"Inference time: {inference_time:.2f} ms")
                if len(self.frame_times) >= 2:
                    elapsed = self.frame_times[-1] - self.frame_times[0]
                    fps = len(self.frame_times) / elapsed
                    logger.info(f"Approx. FPS: {fps:.2f}")

                detections = postprocess_yolo_output(detections_raw, orig_shape=frame.shape[:2])

                for box, conf, cls in detections:
                    cls = int(cls)
                    if cls not in self.config['vehicle_classes']:
                        continue

                    x1, y1, x2, y2 = map(int, box)
                    track_id = int(uuid.uuid4().int & 0xFFFF)
                    current_time = time.time()

                    track_dir = os.path.join(self.config["frames_dir"], str(track_id))
                    os.makedirs(track_dir, exist_ok=True)

                    frame_path = os.path.join(track_dir, "0000.jpg")
                    cv2.imwrite(frame_path, frame)

                    self.active_tracks[track_id] = {
                        "first_seen": current_time,
                        "last_seen": current_time,
                        "frame_count": 1,
                        "dir": track_dir
                    }

                    logger.info(f"Detected vehicle {track_id} at {x1},{y1},{x2},{y2}")
                    self.completed_tracks_queue.put(track_id)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.shutdown()

    def _process_completed_tracks(self):
        while not self.shutdown_flag.is_set():
            try:
                track_id = self.completed_tracks_queue.get(timeout=1.0)
                track_dir = os.path.join(self.config["frames_dir"], str(track_id))

                frame_path = os.path.join(track_dir, "0000.jpg")
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue

                best_path, conf = self._find_best_license_plate(track_dir, frame)
                if best_path:
                    self._send_to_api(best_path, track_id)
                shutil.rmtree(track_dir)
            except queue.Empty:
                continue

    def _find_best_license_plate(self, track_dir: str, frame: np.ndarray) -> Tuple[Optional[str], float]:
        input_tensor = self.preprocess(frame)
        results = self.plate_compiled([input_tensor])[self.plate_compiled.outputs[0]]

        if results.shape[0] == 0:
            return None, 0.0

        best_conf = 0.0
        best_path = os.path.join(track_dir, "0000.jpg")
        return best_path, best_conf

    def _send_to_api(self, frame_path: str, track_id: int):
        try:
            with open(frame_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "lot_id": self.config["lot_id"],
                "image": image_data
            }

            logger.info(f"Sending data to API for track {track_id}")
            response = requests.post(
                self.config["api_endpoint"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info("Successfully sent data")
            else:
                logger.error(f"Failed to send data: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"API error: {str(e)}")

    def shutdown(self):
        self.shutdown_flag.set()
        if hasattr(self, "process") and self.process:
            self.process.terminate()
            self.process.wait()
        cv2.destroyAllWindows()
        self.processing_thread.join(timeout=10.0)

def main():
    tracker = VehicleTracker(CONFIG)
    tracker.run()

if __name__ == "__main__":
    main()