#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, cv2, time, base64, logging, threading, requests, numpy as np, shutil
from typing import Dict, List, Tuple
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
from picamera2 import Picamera2
from libcamera import controls
import time
import requests
import json
import sys 
import time


# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL = logging.DEBUG          # ← change to INFO for less chatter
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
CONFIG = {
    "vehicle_model_path": "./yolo11n_ncnn_model",
    "license_plate_model_path": "./license_plate_detector_ncnn_model",
    "frames_dir": "./frames",
    "vehicle_classes": [2, 3, 5, 7],
    "track_timeout": 25.0,
    "api_endpoint": "https://e5v8r7gy4l.execute-api.us-east-2.amazonaws.com/processCar",
    "lot_id": "d65ef517-c64f-4c54-9dd0-706cd0d184ee",
    "capture_sleep": 0.01
}

fps_history: List[float] = []

pi_configuration = ""

def decrement(value):
    return value - 1

def increment(value):
   return value + 1

def updateServiceRoutine():
        global pi_configuration
        # this is grabbing the lot and updating the capacity
        url = "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080/getLot?id=\"268f0b51-7e68-46fa-b6d5-1f7346a6012d\""

        payload = json.dumps({
                "LotID": "268f0b51-7e68-46fa-b6d5-1f7346a6012d"
                })
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        lot = response.json()
        occupancyVal = 0
        idName = ""

        print("Before update: " + str(lot["occupancy"]))
        # if pi_configuration == "in":
        #         occupancyVal = increment(lot["occupancy"])
        #         lot["occupancy"] = occupancyVal
        # else:
        #         occupancyVal = decrement(lot["occupancy"])
        #         lot["occupancy"] = occupancyVal
        # print("After update: " + str(lot["occupancy"]))

        occupancyVal = increment(lot["occupancy"])
        lot["occupancy"] = occupancyVal

        # we need to change this so that database datatypes are the same!
        lot["open"] = "07:30"
        lot["close"] = "16:30"

        # this is the update loop to add the new 
        url = "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080/updateLot"

        payload = json.dumps(lot)
        print(payload)
        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("PUT", url, headers=headers, data=payload)
        print(response)

        return("268f0b51-7e68-46fa-b6d5-1f7346a6012d")

def getLot(idName):
        url = "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080/getLot?id=" + idName

        payload = json.dumps({
        })

        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

def iou(a, b):
    xA, yA = max(a[0], b[0]), max(a[1], b[1])
    xB, yB = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, xB - xA) * max(0, yB - yA)
    areaA = (a[2]-a[0]) * (a[3]-a[1])
    areaB = (b[2]-b[0]) * (b[3]-b[1])
    return 0.0 if areaA == 0 or areaB == 0 else inter / (areaA + areaB - inter)

# ─── Tracker ─────────────────────────────────────────────────────────────────
class VehicleTracker:
    def __init__(self, cfg: Dict):
        self.cfg = cfg
        os.makedirs(self.cfg["frames_dir"], exist_ok=True)

        logger.info("Loading models…")
        self.vehicle_model = YOLO(self.cfg["vehicle_model_path"])
        self.plate_model   = YOLO(self.cfg["license_plate_model_path"])

        self.active_tracks: Dict[int, Dict] = {}
        self.next_tid = 1

        self.frame_times = deque(maxlen=3000)
        self.shutdown_flag = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=2)

        self.frame_id = 0  # global counter

        self._init_camera()

    # ── camera ───────────────────────────────────────────────────────────────
    def _init_camera(self):
        self.picam2 = Picamera2()
        cam_cfg = self.picam2.create_still_configuration(
            main={
                "size": self.picam2.camera_properties["PixelArraySize"],
                "format": "RGB888",
            },
            controls={
                "AwbMode": controls.AwbModeEnum.Indoor,
                "AwbEnable": True,
                "NoiseReductionMode": controls.draft.NoiseReductionModeEnum.Fast,
                "Brightness": 0.23,
                "Contrast": 1.2,
                "Sharpness": 1.5,
                "ExposureTime": 6000,
                "AnalogueGain": 1.0,
                "Saturation": 1.2,
            },
        )
        self.picam2.align_configuration(cam_cfg)
        self.picam2.configure(cam_cfg)
        self.picam2.start()
        logger.info("Picamera2 started")

    # ── inference helpers ────────────────────────────────────────────────────
    def infer_vehicle(self, img): return self.vehicle_model(img)[0].boxes
    def infer_plate(self, img):   return self.plate_model(img)[0].boxes

    # ── main loop ────────────────────────────────────────────────────────────
    def run(self):
        try:
            while not self.shutdown_flag.is_set():
                frame = self.picam2.capture_array()
                # frame = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
                self.frame_id += 1
                logger.debug(f"[Frame {self.frame_id}] captured")

                t0 = time.time()
                boxes = self.infer_vehicle(frame)
                ms = (time.time() - t0) * 1000
                self.frame_times.append(time.time())
                logger.info(f"[Frame {self.frame_id}] vehicle inference {ms:.1f} ms")

                if len(self.frame_times) > 1:
                    fps = len(self.frame_times) / (self.frame_times[-1] - self.frame_times[0])
                    fps_history.append(fps)
                    logger.debug(f"Rolling FPS ≈ {fps:.2f}")

                detections = []
                if boxes is not None and len(boxes):
                    for i in range(len(boxes)):
                        cls = int(boxes.cls[i])
                        name = str(time.time())+".jpg"
                        if cls not in self.cfg["vehicle_classes"]:
                            cv2.imwrite(name, frame)
                            continue
                        if boxes.data.shape[0] > 0:
                            updateServiceRoutine()
                        x1, y1, x2, y2 = boxes.xyxy[i].cpu().numpy().astype(int)
                        detections.append((x1, y1, x2, y2))
                        carResults = self.vehicle_model(frame)
                        # lazy but just want to see the bounding boxes
                        for result in carResults:
                                detections = result.boxes
                                name = str(time.time())+".jpg"
                                if result.boxes.data.shape[0] > 0:
                                        result.save(filename='result'+name)

                        # jank method for ending licens eplate detections
                        plateResults = self.plate_model(frame)
                        for plateResult in plateResults:
                            detections = plateResult.boxes
                            name = str(time.time())+".jpg"
                            if plateResult.boxes.data.shape[0] > 0:
                                plateResult.save(filename='plate'+name)
                                break
                        time.sleep(2) 
                        break # this is purely for ending
                logger.debug(f"[Frame {self.frame_id}] detections kept: {len(detections)}")

                self._update_tracks(detections, frame, self.frame_id)
                self._dispatch_stale_tracks()

                time.sleep(self.cfg["capture_sleep"])

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.shutdown()

    # ── tracking ────────────────────────────────────────────────────────────
    def _update_tracks(self, dets: List[Tuple[int,int,int,int]], frame, fid: int):
        logger.debug(f"[Frame {fid}] updating tracks")
        now = time.time()
        for (x1,y1,x2,y2) in dets:
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

    # ── shutdown ────────────────────────────────────────────────────────────
    def shutdown(self):
        self.shutdown_flag.set()
        self.executor.shutdown(wait=True)
        self.picam2.stop(); self.picam2.close()
        if fps_history:
            print(f"Max FPS: {max(fps_history):.2f}")
            print(f"Min FPS: {min(fps_history):.2f}")
        logger.info("Shutdown complete")

# ─── entry point ─────────────────────────────────────────────────────────────
def main():
    VehicleTracker(CONFIG).run()

if __name__ == "__main__":
    main()
