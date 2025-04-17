import os, sys, time, requests, json                             
from picamera2 import Picamera2, Preview
from libcamera import controls
from typing import Dict,List
import numpy as np

from ultralytics import YOLO

# global flags for the picamera functionality, need to check if it has already been intialized and if it needs to be stopped
camera_initialized = False
picam2 = None  
pi_configuration = ""

def decrement(value):
    return value - 1

def increment(value):
   return value + 1

def take_pic():
    global picam2
    global camera_initialized

    # camera has not been initialized so it must be
    if not camera_initialized: 
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration(
               main={
                      'size': picam2.camera_properties['PixelArraySize'],
                      'format': 'RGB888',
                },
                controls={
                        #'AeConstraintMode': controls.AeConstraintModeEnum.Highlight,
                        #'AeExposureMode': controls.AeExposureModeEnum.Short,
                        #'ExposureValue': -1.0,
                        #'AeEnable': True,
                        'AwbMode': controls.AwbModeEnum.Indoor,
                        'AwbEnable': True,
                        'NoiseReductionMode': controls.draft.NoiseReductionModeEnum.Fast,
                        'Brightness': 0.23,
                        'Contrast': 1.2,
                        'Sharpness': 1.5,
                        'ExposureTime': 6000, 
                        'AnalogueGain': 1.0,
                        'Saturation': 1.2
                },
        )
        picam2.align_configuration(camera_config)
        picam2.configure(camera_config)
        print(picam2.camera_controls)
        print(camera_config)

        try:
            picam2.start()
            camera_initialized = True
            print("Camera initialized and started")
        except Exception as e:
            print(f"Camera initialization failed: {e}")
            return

    try:
        name = str(time.time())+".jpg"
        picam2.capture_file(name)
        print("Image captured successfully")
        #time.sleep(1)
    except Exception as e:
        print(f"Error capturing image: {e}")
    return name

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
        if pi_configuration == "in":
                occupancyVal = increment(lot["occupancy"])
                lot["occupancy"] = occupancyVal
        else:
                occupancyVal = decrement(lot["occupancy"])
                lot["occupancy"] = occupancyVal
        print("After update: " + str(lot["occupancy"]))

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


def main(argv):
        if argv[0] != 'in' and argv[0] != 'out':
                raise ValueError(f"Must provide argument 'in' or 'out'. Provided '{argv[0]}'")
        else:
                global pi_configuration
                pi_configuration = argv[0]
        model = YOLO('LPR_detector.pt', "detect")
        model.export(
               format='ncnn'
        )
        model_ncnn = YOLO('./LPR_detector_ncnn_model')
        print("super awesome model loaded")
        
        running = True

        active_track: Dict[int, List] = {}
        while (running):
                try:
                        # call take pic method to capture current frame of rpi
                        fileName = take_pic()
                        print("image taken")
                        results = model_ncnn.track(os.getenv('HOME')+'/parking-availability-system/Desktop/'+fileName, persist=True)
                        for result in results:
                                names = model_ncnn.names
                                detections = result.boxes
                                if result.boxes.data.shape[0] > 0:
                                        print("THERE IS A LICENSE PLATE!!!! UPDATE THE DATABASE!!!!")
                                        for box in result.boxes:
                                                if not (box.id in active_track.keys()):         # Doesn't work not enough time to fix
                                                        updateServiceRoutine()
                                                        result.save(filename='result'+fileName)
                                                        # update the database
                                                        file = open("DB_Com_Times.txt", "a")
                                                        inference_start = time.time()
                                                        file.write(str(time.time() - inference_start) + "\n")
                                                        print(str(time.time() - inference_start) + "\n")
                                                        file.close()
                                                active_track[box.id].append(box)
                                                time.sleep(2)
                                                        
                                        running = True
                                else:
                                        print("This license plate is not bussin!")
                                        if len(active_track.keys()) > 0:
                                                for tid in active_track.keys():
                                                       active_track.clear()              
                                        result.save(filename='result'+fileName)
                        #userResp = input("Would you like to continue? (True/False)")
                        #if (userResp == "False"):
                                #break
                except Exception as e:
                        print(e)

if __name__ == "__main__":
        if len(sys.argv) != 2:
                raise TypeError("Missing single positional argument 'in' or 'out'. Example: \"python car_detector.py 'in'\"")
        else :
                main(sys.argv[1:])
