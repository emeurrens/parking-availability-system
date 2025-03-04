import torch
import ultralytics
from picamera2 import Picamera2, Preview
from libcamera import controls
import time
import requests
import json

from ultralytics import YOLO

# global falgs for the picamera functionality, need to check if it has already been intialized and if it needs to be stopped
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
        camera_config = picam2.create_still_configuration(main={'size': (1920, 1080)})
        picam2.configure(camera_config)
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
        time.sleep(1)
    except Exception as e:
        print(f"Error capturing image: {e}")
    return name


def updateServiceRoutine():
        global pi_configuration
        # this is grabbing the lot and updating the capacity
        url = "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080/getLot?id=\"c0cb52ad-ac20-41f7-b996-82d73ae31b73\""

        payload = json.dumps({
        "LotID": "44799a2c-d5ef-42bf-ad61-9f8b074b413e"
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

        return("c0cb52ad-ac20-41f7-b996-82d73ae31b73")

def getLot(idName):
        url = "http://ec2-3-143-172-128.us-east-2.compute.amazonaws.com:8080/getLot?id=" + idName

        payload = json.dumps({
        })

        headers = {
        'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)


def main():
        try:
                model = YOLO('LPR_detector.pt')
                model.eval()
                print("super awesome model loaded")
        except Exception as e:
                print(f"Error loading model: {e}")

        global pi_configuration 
        pi_configuration = input("in/out: ")
        while (1):
                try:
                        # call take pic method to capture current frame of rpi
                        fileName = take_pic()
                        print("image taken")
                        results = model('/home/pi/parking-availability-system/Desktop/'+fileName)

                        for result in results:
                                names = model.names
                                detections = result.boxes
                                print(result.boxes.data.shape[0])
                                if result.boxes.data.shape[0] > 0:
                                        print("THERE IS A LICENSE PLATE!!!! UPDATE THE DATABASE!!!!")
                                        # update the database
                                        updateServiceRoutine()
                                else:
                                        print("This license plate is not bussin!")

                                result.save(filename='result'+fileName)
                        #userResp = input("Would you like to continue? (True/False)")
                        #if (userResp == "False"):
                                #break
                except Exception as e:
                        print(e)

if __name__ == "__main__":
        main()



