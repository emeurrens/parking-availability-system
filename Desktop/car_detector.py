import torch
import ultralytics
from picamera2 import Picamera2, Preview
from libcamera import controls

from ultralytics import YOLO

def take_pic():
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration(main={'size': (1920, 1080)})
        picam2.configure(camera_config)
        try:
                picam2.start()
        # time.sleep(2) # zzz
                picam2.capture_file("image.jpg")
                picam2.stop()
        except Exception as e:
                print(f"Camera smells like: {e}")

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
        try:
                # call take pic method to capture current frame of rpi
                take_pic()
                #results = model('/home/parkings/parking-availability-system/Desktop/dataset-card.jpg')
                results = model('/home/parkings/parking-availability-system/Desktop/image.jpg')
                #results = model('/home/parkings/car_noplate.jpg')
                #results = model('/home/parkings/car.jpg')

                for result in results:
                        names = model.names
                        detections = result.boxes
                        print(result.boxes.data.shape[0])
                        if result.boxes.data.shape[0] > 0:
                                print("THERE IS A LICENSE PLATE!!!! UPDATE THE DATABASE!!!!")
                                # update the data base
                        else:
                                print("This license plate is not bussin!")

                        result.save(filename='result.jpg')
        except Exception as e:
                print(e)

if __name__ == "__main__":
        main()



