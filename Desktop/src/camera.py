from picamera2 import Picamera2
from libcamera import controls
from threading import Condition, current_thread
import numpy as np
import cv2

# Initialize and configure camera settings for optimal motion 
class Camera:
    def __init__(self):
        try:
            self.cam, self.config = Camera._camConfig()
            self.cam_buffer = np.zeros(( # Create a buffer using np.zero of frame size
                                self.cam.camera_properties['PixelArraySize'][1],        # Width
                                self.cam.camera_properties['PixelArraySize'][0],        # Height
                                3                                                       # 3 color channels
                            )) 
        except Exception as e:
            print (e)
            print(f"[{current_thread()}]: CAM_THREAD - Failed to initialize camera")
            if self.cam != None:
                self.cam.close()
            self.cam_buffer = np.zeros((480,640,3))
        finally:
            self.numReaders, self.numWriters = 0,0
            self.buffer_cv = Condition()

    def _camConfig() -> tuple[Picamera2, dict]:
        cam = Picamera2()

        # Configure camera 
        cam_config = cam.create_still_configuration(
            main={
                'size': cam.camera_properties['PixelArraySize'],    # max resolution
                'format': 'RGB888'
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
            }
        )

        # Aligns desired configuration with closest available mode
        cam.align_configuration(cam_config) 
        # Apply configuration and control settings
        cam.configure(cam_config)

        return cam, cam_config

    # Any necessary software preprocessing steps, if deemed necessary
    def _cvPreprocessing(img):
        return img

    # Main camera thread
    def mainThread(self):
        # Initiate camera
        self.cam.start()
        
        # Capture image and send to buffer to be read by another thread
        # Block until buffer is read from, then repeat
        while True:
            if self.cam != None:
                with self.buffer_cv:
                    while self.numReaders > 0:
                        self.buffer_cv.wait()
                    self.numWriters+=1
                    self.cam_buffer = Camera._cvPreprocessing(self.cam.capture_array('main'))
                    # cv2.imwrite('test.jpg', self.cam_buffer, [cv2.IMWRITE_JPEG_QUALITY, 100])
                    print(f"[{current_thread()}]: CAM_THREAD - Captured image")
                    self.numWriters-=1
                    self.buffer_cv.notify_all()