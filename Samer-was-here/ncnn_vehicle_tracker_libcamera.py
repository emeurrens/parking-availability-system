import os
import cv2
import time
import uuid
import base64
import json
import logging
import threading
import requests
import numpy as np
from typing import Dict, List, Tuple, Optional
from ultralytics import YOLO
import shutil
import subprocess
import select
from datetime import datetime
from collections import deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    "vehicle_model_path": "./yolo11n_ncnn_model",  # NCNN model folder
    "license_plate_model_path": "./license_plate_detector_ncnn_model",  # NCNN model folder
    "frames_dir": "./frames",
    "vehicle_classes": [2, 3, 5, 7],
    "track_timeout": 5.0,
    "api_endpoint": "https://e5v8r7gy4l.execute-api.us-east-2.amazonaws.com/processCar",
    "lot_id": "d65ef517-c64f-4c54-9dd0-706cd0d184ee",
    "source": 0
}

def iou(boxA, boxB):
    """
    Compute the Intersection over Union (IOU) of two boxes.
    Box format: (x1, y1, x2, y2)
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    if boxAArea == 0 or boxBArea == 0:
        return 0.0
    return interArea / float(boxAArea + boxBArea - interArea)

class VehicleTracker:
    def __init__(self, config: Dict):
        self.config = config
        os.makedirs(self.config["frames_dir"], exist_ok=True)

        logger.info("Loading vehicle detection model (NCNN)...")
        self.vehicle_model = YOLO(self.config["vehicle_model_path"])

        logger.info("Loading license plate detection model (NCNN)...")
        self.plate_model = YOLO(self.config["license_plate_model_path"])

        # Track dictionary:
        # track_id -> {
        #   "bbox": (x1, y1, x2, y2),
        #   "last_seen": float,
        #   "first_seen": float,
        #   "frame_count": int,
        #   "dir": str
        # }
        self.active_tracks = {}
        self.next_track_id = 1

        self.shutdown_flag = threading.Event()
        self.frame_times = deque(maxlen=3000)

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

    def infer_vehicle(self, frame: np.ndarray):
        """
        Return the Boxes object for each detection from the vehicle model.
        Typically you'll do: results = self.vehicle_model(frame) -> results[0].boxes
        """
        results = self.vehicle_model(frame)
        # results is a list of 'Results' objects, usually length 1 for a single image
        return results[0].boxes

    def infer_plate(self, frame: np.ndarray):
        """
        Return the Boxes object for each detection from the plate model.
        """
        results = self.plate_model(frame)
        return results[0].boxes

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

                # Convert raw YUV420 to BGR
                yuv = np.frombuffer(raw_frame, dtype=np.uint8).reshape((int(480 * 1.5), 640))
                frame = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

                # Vehicle inference
                start_time = time.time()
                boxes = self.infer_vehicle(frame)
                inference_time = (time.time() - start_time) * 1000
                self.frame_times.append(time.time())

                logger.info(f"Inference time: {inference_time:.2f} ms")
                if len(self.frame_times) >= 2:
                    elapsed = self.frame_times[-1] - self.frame_times[0]
                    fps = len(self.frame_times) / elapsed
                    logger.info(f"Approx. FPS: {fps:.2f}")

                # Filter for classes of interest
                # 'boxes' is a Boxes object with shape (#detections, 6) typically
                # we can access boxes.cls, boxes.xyxy, etc.
                # We'll gather relevant detections in a list of (x1, y1, x2, y2, conf)
                detections = []
                if boxes is not None and len(boxes) > 0:
                    for i in range(len(boxes)):
                        cls_ = int(boxes.cls[i])
                        if cls_ not in self.config["vehicle_classes"]:
                            continue
                        xyxy = boxes.xyxy[i].cpu().numpy().astype(int)
                        conf = float(boxes.conf[i])
                        x1, y1, x2, y2 = xyxy
                        detections.append((x1, y1, x2, y2, conf))

                # Update tracks
                self._update_tracks(detections, frame)

                # Check for stale tracks
                self._finalize_stale_tracks()

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.shutdown()

    def _update_tracks(self, detections: List[Tuple[int, int, int, int, float]], frame: np.ndarray):
        current_time = time.time()
        updated_track_ids = set()

        # Try to match each detection to an existing track by best IOU
        for (x1, y1, x2, y2, conf) in detections:
            best_track_id = None
            best_iou = 0.0
            for track_id, track_data in self.active_tracks.items():
                iou_val = iou((x1, y1, x2, y2), track_data["bbox"])
                if iou_val > best_iou:
                    best_iou = iou_val
                    best_track_id = track_id

            # If high enough IOU, update that track
            if best_iou > 0.2 and best_track_id is not None:
                track_data = self.active_tracks[best_track_id]
                track_data["bbox"] = (x1, y1, x2, y2)
                track_data["last_seen"] = current_time
                track_data["frame_count"] += 1

                # Save frame
                frame_filename = f"frame_{track_data['frame_count']:04d}.jpg"
                frame_path = os.path.join(track_data["dir"], frame_filename)
                cv2.imwrite(frame_path, frame)

                updated_track_ids.add(best_track_id)
            else:
                # Create new track
                new_track_id = self.next_track_id
                self.next_track_id += 1

                track_dir = os.path.join(self.config["frames_dir"], str(new_track_id))
                os.makedirs(track_dir, exist_ok=True)

                frame_filename = "frame_0001.jpg"
                frame_path = os.path.join(track_dir, frame_filename)
                cv2.imwrite(frame_path, frame)

                self.active_tracks[new_track_id] = {
                    "bbox": (x1, y1, x2, y2),
                    "last_seen": current_time,
                    "first_seen": current_time,
                    "frame_count": 1,
                    "dir": track_dir
                }

                updated_track_ids.add(new_track_id)

        # Tracks not updated remain unchanged; we'll finalize them if they're stale.

    def _finalize_stale_tracks(self):
        """
        Check each active track. If it hasn't been updated for more than 'track_timeout',
        finalize the track (license-plate inference, send best frame, remove folder).
        """
        current_time = time.time()
        stale_ids = []
        for track_id, track_data in self.active_tracks.items():
            if (current_time - track_data["last_seen"]) > self.config["track_timeout"]:
                stale_ids.append(track_id)

        for tid in stale_ids:
            track_data = self.active_tracks[tid]
            self._finalize_track(tid, track_data)
            del self.active_tracks[tid]

    def _finalize_track(self, track_id: int, track_data: Dict):
        """
        Once a track times out, scan all frames, find the highest-confidence plate,
        send that frame to the API, then remove the folder.
        """
        track_dir = track_data["dir"]
        frame_files = sorted([
            f for f in os.listdir(track_dir)
            if f.lower().endswith((".jpg", ".png"))
        ])
        if not frame_files:
            logger.warning(f"No frames found for track {track_id}, removing folder.")
            shutil.rmtree(track_dir, ignore_errors=True)
            return

        best_conf = 0.0
        best_frame_path = None

        for f_name in frame_files:
            frame_path = os.path.join(track_dir, f_name)
            frame = cv2.imread(frame_path)
            if frame is None:
                continue

            plate_boxes = self.infer_plate(frame)  # This should be a 'Boxes' object
            if plate_boxes is None or len(plate_boxes) == 0:
                continue  # No plates found in this frame

            # plate_boxes.conf is a tensor of confidences for each plate
            # We'll check the max confidence in this set of plates
            frame_conf = float(plate_boxes.conf.max().item())
            if frame_conf > best_conf:
                best_conf = frame_conf
                best_frame_path = frame_path

        if best_frame_path is not None:
            # Send to API
            self._send_to_api(best_frame_path, track_id)
        else:
            logger.info(f"No license plate detected for track {track_id}.")

        # Clean up
        shutil.rmtree(track_dir, ignore_errors=True)

    def _send_to_api(self, frame_path: str, track_id: int):
        try:
            with open(frame_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            payload = {
                "lot_id": self.config["lot_id"],
                "image": image_data
            }

            logger.info(f"Sending frame of track {track_id} to API...")
            response = requests.post(
                self.config["api_endpoint"],
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                logger.info(f"Successfully sent data for track {track_id}")
            else:
                logger.error(f"Failed to send data: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"API error for track {track_id}: {str(e)}")

    def shutdown(self):
        self.shutdown_flag.set()
        if hasattr(self, "process") and self.process:
            self.process.terminate()
            self.process.wait()
        #cv2.destroyAllWindows()        

def main():
    tracker = VehicleTracker(CONFIG)
    tracker.run()

if __name__ == "__main__":
    main()