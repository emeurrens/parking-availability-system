# TODO: Merge car_detector_ncnn.py and ncnn_vehicle_tracker_libcamera.py
# Consider redudancies with camera.py; interface with camera through camera.py

import os, sys, time, requests, json
from typing import Dict, List, Tuple
from collections import deque
from threading import Condition, Event, current_thread
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
import numpy as np
import cv2
from camera import Camera

class Detector():
    # ── configuration dicts ────────────────────────────────────────────────────────────
    MODEL_CONFIG = {
        "vehicle_model_path": "../model/yolo11n_ncnn_model",                        # YOLOv11n NCNN model folder
        "license_plate_model_path": "../model/license_plate_detector_ncnn_model",   # LPD NCNN model folder
        "frames_dir": "../frames",                                                  # Frame cache
        "vehicle_classes": [2, 7],                                                  # 2: car, 7: truck
        "track_timeout": 5.0,
        "capture_sleep": 0.01,
        "source": 0,
    }
    API_CONFIG = {
        "LPR_endpoint": "https://e5v8r7gy4l.execute-api.us-east-2.amazonaws.com/processCar",
        "RDS_endpoint": "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080",
        "LotID": "268f0b51-7e68-46fa-b6d5-1f7346a6012d", # Sebring International Raceway
        "headers": {'Content-Type' : 'application/json'},
    }

    # ── class constructor ────────────────────────────────────────────────────────────
    def __init__(self, direction=str):
        # Create general configuration dictionary
        self.cfg = Detector.MODEL_CONFIG | Detector.API_CONFIG
        # Load models and direction
        self.vehicle_model = YOLO(self.cfg['vehicle_model_path'], 'detect')
        self.plate_model = YOLO(self.cfg['license_plate_model_path'], 'detect')
        self.direction = direction
        # Make file to store frames
        os.makedirs(self.cfg["frames_dir"], exist_ok=True)
        self.frame_times = deque(maxlen=3000)
        self.frame_id = 0  # global counter
        # Storing tracking threads
        self.active_tracks: Dict[int, Dict] = {}
        self.next_tid = 1
        # Process execution controls
        self.shutdown_flag = Event()
        self.executor = ThreadPoolExecutor(max_workers=2)

    # ── inference tasks ────────────────────────────────────────────────────────────
    # def _infer_vehicle(self, frame: np.ndarray):
    #     """
    #     Return the Boxes object for each detection from the vehicle model.
    #     Typically you'll do: results = self.vehicle_model(frame) -> results[0].boxes
    #     """
    #     results = self.vehicle_model(frame)
    #     # results is a list of 'Results' objects, usually length 1 for a single image
    #     return results[0].boxes
    
    # def _infer_plate(self, frame: np.ndarray):
    #     """
    #     Return the Boxes object for each detection from the plate model.
    #     """
    #     results = self.plate_model(frame)
    #     return results[0].boxes

    # ── retrieve frame from camera  ────────────────────────────────────────────────────────────
    def _getNextFrame(self, buffer_cv, writers, readers) -> np.ndarray:
        # Check if it's clear to read from camera buffer
        with buffer_cv:
            while writers > 0:
                buffer_cv.wait()
            readers+=1
            frame = buffer_cv.copy()
            print(f"[{current_thread()}]: DETECTION_THREAD - Copied image from buffer")
            readers-=1
            buffer_cv.notify_all()

        return frame
    
    # ── tracking ────────────────────────────────────────────────────────────
    def _update_tracks(self, det_coords: List[Tuple[int,int,int,int]], frame, frame_id: int):
        print(f"[{current_thread()}]: DETECTION_THREAD - [Frame {frame_id}] updating tracks")
        for (x1,y1,x2,y2) in det_coords:
            best_tid, best_iou = None, 0.0
            for tid, td in self.active_tracks.items():
                v = iou((x1,y1,x2,y2), td["bbox"])
                if v > best_iou:
                    best_tid, best_iou = tid, v

            if best_iou > 0.2 and best_tid:
                td = self.active_tracks[best_tid]
                td["bbox"] = (x1,y1,x2,y2)
                td["last_seen"] = now
                logger.debug(f"[Frame {fid}] updated track {best_tid} (IOU={best_iou:.2f})")
                self._save_frame(frame, best_tid, fid)
            else:
                tid = self.next_tid; self.next_tid += 1
                tdir = os.path.join(self.cfg["frames_dir"], str(tid))
                os.makedirs(tdir, exist_ok=True)
                self.active_tracks[tid] = {
                    "bbox": (x1,y1,x2,y2),
                    "last_seen": now,
                    "dir": tdir,
                }
                logger.info(f"[Frame {fid}] created new track {tid}")
                self._save_frame(frame, tid, fid)

    # ── private main loop ────────────────────────────────────────────────────────────
    def _run(self, buffer_cv, writers, readers):
        try:
            while not self.shutdown_flag.is_set():
                # Capture frame and store it
                rgb = self._getNextFrame(buffer_cv, writers, readers)
                frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)                # Convert frame to cv2 format
                self.frame_id += 1
                print(f"[{current_thread()}]: DETECTION_THREAD - [Frame {self.frame_id}] captured")

                # Do vehicle inference
                car_result = self.vehicle_model.track(frame, persist=True)[0]
                car_boxes = car_result[0].boxes
                print(f"[{current_thread()}]: DETECTION_THREAD - [Frame {self.frame_id}] vehicle inference") # {ms:.1f} ms")
                
                # See if detected object is in vehicle classes
                # If so add the detection box coords to a list to be tracked
                car_coords = []
                if car_boxes is not None and len(car_boxes) > 0:
                    for i in range(len(car_boxes)):
                        class_id = int(car_boxes.cls[i])
                        if class_id not in self.cfg["vehicle_classes"]:
                            continue
                        x1, y1, x2, y2 = car_boxes.xyxy[i].cpu().numpy().astype(int)
                        car_coords.append((x1,y1,x2,y2))
                print(f"[{current_thread()}]: DETECTION_THREAD - [Frame {self.frame_id}] detections kept: {len(car_coords)}")

                # For every car detection, segment that buffer image to the detection bounds and search for a plate
                # If plate(s) detected store box coords in list
                plate_coords = []
                for car_coord in car_coords:
                    car_segment = frame[car_coord[1]:car_coord[3],car_coord[0]:car_coord[2]]
                    plate_result = self.plate_model(car_segment)[0]
                
                # Process tracking
                self._update_tracks(detections, frame, self.frame_id)
                self._dispatch_stale_tracks()

        except KeyboardInterrupt:
            print(f"[{current_thread()}]: DETECTION_THREAD - Interrupted by user")
        finally:
            self.shutdown()
    
    # ── public main loop ────────────────────────────────────────────────────────────
    def mainThread(self, buffer_cv=Condition, writers=int, readers=int):
        while not self.shutdown_flag.is_set():
            # Start frame turnover timer
            start_time = time.time()

            # TODO: Finish pipeline
            self._run(buffer_cv, writers, readers)
            # 

    # ── shutdown ────────────────────────────────────────────────────────────
    def shutdown(self):
        self.shutdown_flag.set()
        self.executor.shutdown(wait=True)
        # self.picam2.stop(); self.picam2.close()
        # if fps_history:
        #     print(f"Max FPS: {max(fps_history):.2f}")
        #     print(f"Min FPS: {min(fps_history):.2f}")
        print(f"[{current_thread()}]: DETECTION_THREAD - Shutdown complete")

# ─── Tracker ─────────────────────────────────────────────────────────────────
class VehicleTracker:
    # ── tracking ────────────────────────────────────────────────────────────
    def _update_tracks(self, det_coords: List[Tuple[int,int,int,int]], frame, frame_id: int):
        print(f"[{current_thread()}]: DETECTION_THREAD - [Frame {frame_id}] updating tracks")
        now = time.time()
        for (x1,y1,x2,y2) in det_coords:
            best_tid, best_iou = None, 0.0
            for tid, td in self.active_tracks.items():
                v = iou((x1,y1,x2,y2), td["bbox"])
                if v > best_iou:
                    best_tid, best_iou = tid, v

            if best_iou > 0.2 and best_tid:
                td = self.active_tracks[best_tid]
                td["bbox"] = (x1,y1,x2,y2)
                td["last_seen"] = now
                logger.debug(f"[Frame {fid}] updated track {best_tid} (IOU={best_iou:.2f})")
                self._save_frame(frame, best_tid, fid)
            else:
                tid = self.next_tid; self.next_tid += 1
                tdir = os.path.join(self.cfg["frames_dir"], str(tid))
                os.makedirs(tdir, exist_ok=True)
                self.active_tracks[tid] = {
                    "bbox": (x1,y1,x2,y2),
                    "last_seen": now,
                    "dir": tdir,
                }
                logger.info(f"[Frame {fid}] created new track {tid}")
                self._save_frame(frame, tid, fid)

    def _save_frame(self, frame, tid: int, fid: int):
        path = os.path.join(self.cfg["frames_dir"], str(tid), f"{fid}.jpg")
        cv2.imwrite(path, frame)
        logger.debug(f"[Frame {fid}] saved to {path}")

    # ── stale track handling (threaded) ───────────────────────────────────────
    def _dispatch_stale_tracks(self):
        now = time.time()
        stale = [tid for tid,td in self.active_tracks.items()
                 if now - td["last_seen"] > self.cfg["track_timeout"]]
        for tid in stale:
            td = self.active_tracks.pop(tid)
            logger.info(f"Track {tid} stale → submit finalisation")
            self.executor.submit(self._finalise_track, tid, td)

    def _finalise_track(self, tid: int, td: Dict):
        logger.info(f"[T{tid}] finalisation started")
        imgs = sorted(os.listdir(td["dir"]), key=lambda f:int(os.path.splitext(f)[0]))
        logger.debug(f"[T{tid}] {len(imgs)} cached frames to inspect")

        best_conf, best_path = 0.0, None
        for fn in imgs:
            p = os.path.join(td["dir"], fn)
            img = cv2.imread(p)
            plates = self.infer_plate(img)
            if plates is None or len(plates) == 0:
                logger.debug(f"[T{tid}] {fn}: no plate")
                continue
            conf = float(plates.conf.max().item())
            logger.debug(f"[T{tid}] {fn}: max plate conf {conf:.3f}")
            if conf > best_conf:
                best_conf, best_path = conf, p
                logger.debug(f"[T{tid}] best frame updated → {fn}")

        if best_path:
            logger.info(f"[T{tid}] best frame {os.path.basename(best_path)} conf={best_conf:.3f}")
            self._send_to_api(best_path, tid)
        else:
            logger.info(f"[T{tid}] no plate detected in any frame")

        shutil.rmtree(td["dir"], ignore_errors=True)
        logger.debug(f"[T{tid}] cache folder removed")

    # ── API ──────────────────────────────────────────────────────────────────
    def _send_to_api(self, img_path, tid):
        try:
            with open(img_path,"rb") as f:
                data = f.read()
            b64 = base64.b64encode(data).decode()
            logger.info(f"[T{tid}] uploading {os.path.basename(img_path)} ({len(data)/1024:.1f} KB)")
            r = requests.post(self.cfg["api_endpoint"],
                              json={"lot_id": self.cfg["lot_id"], "image": b64},
                              headers={"Content-Type":"application/json"})
            if r.status_code == 200:
                logger.info(f"[T{tid}] upload OK")
            else:
                logger.error(f"[T{tid}] upload failed {r.status_code}: {r.text}")
        except Exception as e:
            logger.error(f"[T{tid}] API exception: {e}")             