import sys
from threading import Thread 
import numpy as np
from camera import Camera
from detection import Detector

def main(argv):
    # Initialize necessary pipeline objects
    cam_interface = Camera()
    detector = Detector()
    
    # Initialize threads
    t_cam = Thread(target=cam_interface.mainThread)
    t_detect = Thread(target=detector.mainThread, 
                      args=[cam_interface.buffer_cv, cam_interface.numWriters, cam_interface.numReaders])
    t_stream = None
    threads = [
        t_cam,
        t_detect,
        t_stream
    ]

    # Start all threads
    for t in threads:
        t.start()

    for t in threads:
        t.join()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise TypeError("Missing single positional argument 'in' or 'out'. Example: \"python car_detector.py 'in'\"")
    else:
        main(sys.argv[1:])