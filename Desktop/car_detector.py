import torch
import ultralytics
from picamera2 import Picamera2, Preview
from libcamera import controls
import time

from ultralytics import YOLO

# global falgs for the picamera functionality, need to check if it has already been intialized and if it needs to be stopped
camera_initialized = False
picam2 = None  

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
        picam2.capture_file("image.jpg")
        print("Image captured successfully")
        time.sleep(1)
    except Exception as e:
        print(f"Error capturing image: {e}")

def get_counter():
        print('get counter val from database')

def update_counter(val):
        print(val)
        # send the val to the DB

def main():
        try:
                model = YOLO('LPR_detector.pt')
                model.eval()
                print("super awesome model loaded")
        except Exception as e:
                print(f"Error loading model: {e}")
        while (1):
                try:
                        # call take pic method to capture current frame of rpi
                        take_pic()
                        print("image taken")
                        #results = model('/home/parkings/parking-availability-system/Desktop/dataset-card.jpg')
                        results = model('/home/pi/parking-availability-system/Desktop/image.jpg')
                        #results = model('/home/parkings/car_noplate.jpg')
                        #results = model('/home/parkings/car.jpg')

                        for result in results:
                                names = model.names
                                detections = result.boxes
                                print(result.boxes.data.shape[0])
                                if result.boxes.data.shape[0] > 0:
                                        print("THERE IS A LICENSE PLATE!!!! UPDATE THE DATABASE!!!!")
                                        # update the database
                                else:
                                        print("This license plate is not bussin!")

                                result.save(filename='result.jpg')
                        userResp = input("Would you like to continue? (True/False)")
                        if (userResp == "False"):
                                break
                except Exception as e:
                        print(e)

if __name__ == "__main__":
        main()



