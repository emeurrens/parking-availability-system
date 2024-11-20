#!/usr/bin/env python
# coding: utf-8

# In[5]:


import psycopg2
from psycopg2 import Binary
from picamera2 import Picamera2, Preview
import time
import cv2
from flask import Flask, Response
from libcamera import controls
import requests
import json

app = Flask(__name__)

def getCar(url):
    url += "getCar"

    payload = json.dumps({
      "CarID": "361bb702-0f10-45b6-a795-929f3cba739f"
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    
def getAllCars(url):
    url += "getAllCars"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)

def updateCar(url, carID, licensePlate, color, valid):
    url += "updateCar"

    payload = json.dumps({
      "CarID": carID,
      "license_plate": licensePlate,
      "color": {
        "String": color,
        "Valid": valid
      }
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    print(response.text)
    
def saveCar():
    url += "saveCar"

    payload = json.dumps({
      "license_plate": "621-ABC",
      "color": {
        "String": "Orange",
        "Valid": True
      },
      "LotID": "f24dacb0-9513-45d9-90f8-b07e5dee5271"
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    
def deleteCar(url):
    url += "deleteCar"

    payload = json.dumps({
      "CarID": "9b5559cf-d277-4a52-b341-7d5831e597d0"
    })
    headers = {
      'Content-Type': 'application/json'
    }

    response = requests.request("DELETE", url, headers=headers, data=payload)

    print(response.text)

def captureCar():
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={'size': (1920, 1080)})
    picam2.configure(camera_config)
    try:
        picam2.start()
        time.sleep(2) # zzz
        picam2.capture_file("test.jpg")
    except Exception as e:
        print(f"Camera smells like: {e}")

def captureFrames():
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(controls={"FrameDurationLimits": (100000, 100000),'NoiseReductionMode': controls.draft.NoiseReductionModeEnum.Fast},main={"size": (1920, 1080)})
    picam2.configure(camera_config)
    picam2.start()
    i = 0
    while True:
        frame = picam2.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image\r\n\r\n' + frame + b'\r\n')
        i += 1
        print(i)

@app.route('/video_feed')
def video_feed():
    return Response(captureFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    print("Opening secrets")
    f = open("/home/parkings/Desktop/TemporaryConnectionFolder/url.txt")
    url = str(f.readline()).strip() 
#     app.run(host='0.0.0.0', port=5000)
#     captureFrames()
    #getCar()
    getAllCars(url)

if __name__ == "__main__":
    main()


# In[ ]:




