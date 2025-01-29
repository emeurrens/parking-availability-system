import torch
import ultralytics
import picamera

from ultralytics import YOLO

def take_pic():
    camera = picamera.PiCamera()
    camera.capture('/home/parkings/image.jpg')

def get_counter():
    print('get counter val from database')

def update_counter(val):
    print(val)
    # send the val to the DB

def main():
    try:
            model = YOLO('LPR_detector.pt')
            print("super awesome model loaded")
    except Exception as e:
            print(f"Error loading model: {e}")
    try:
            # call take pic method to capture current frame of rpi
            #take_pic()
            #results = model('/home/parkings/image.jpg')

            results = model('/home/parkings/car_noplate.jpg')
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

