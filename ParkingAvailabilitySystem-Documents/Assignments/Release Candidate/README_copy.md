# Parking Availability System (PAS)
The Parking Availability System (PAS) was inspired by the lack of easily available parking resources on campus and would promote quicker and more reliable transportation to and from campus. It represents a small-scale, hardware/software system providing a relatively low-cost solution for predicting parking availability accurately within parking garages on campus. 

## Audience & Use Case: 
Live parking data is only available at a select few locations on campus, making it difficult for those who must drive to campus to find parking during busy periods. This information would be beneficial for off-campus commuters and visitors, and can be used by UF Transit and Parking Services (UF TAPS) and the UF Transportation Institute (UFTI) for to improve parking facilities on campus. You don’t want to drive into a parking garage, realize there’s no parking, and fumble around on your phone, in the middle of the garage, for minutes trying to find another place to park. This product could reduce the stress of finding parking on campus.

## Comparable Solutions:
There are multiple comparable existing devices from various vendors used to monitor real-time parking information. Some solutions for determining parking availability include counting availability at every individual space, and then there are other, typically cheaper, solutions that count cars into and out of a parking facility. These solutions are then further split between visual and non-visual solutions. Non-visual solutions include in-ground induction loops, radar sensors, ultrasonic sensors, and magnetometer sensors.  Visual solutions involve using cameras to determine parking availability. The university currently employs Genetec's parking system, which is utilized on campus, requires a prohibitively expensive cost of $8000-11000 to set up per entrance/exit lane, with a recurring cost for the service of $6000 per year or $500 per month. The goal of this project is to develop a relatively low-cost solution to these alternatives that will have comparable accuracy without the prohibitive cost, so that it could be expanded to other parking facilities on campus.

## Core Features:
- Vehicle Detection
- License Plate Recognition
- Compact, camera-based edge device 
- Real-time parking information on mobile app

## Release Candidate Completed Work ([Demo](https://youtu.be/xEtaFQUtrns)):
- Mobile Application
  - Refactored and updated database access functions to reflect latest changes to database and lot API
  - Added occupancy percentage indicator in lot details page to allow user to better view parking availability
  - Fixed bug where lot database would not be accessed immediately on app start
  - Resolved deprecated project and build configuration and settings
- Hardware Test Script
  - Polls Raspberry Pi CPU core for hardware values related to frequency, temperature, voltage, and throttle state and stores values in .csv
- Raspberry Pi Camera Tuning
  - Updated the raspberry pi camera configuration script to alter the exposure time / shutter speed, and the analogue gain. This feature is still in testing to determine the optimal configuration to capture moving images.
- ESP32 Configuration and Testing
  - Connected the ESP32 successfully to the UF network and to the Raspberry Pi. Tested the Raspberry Pi while connected to the ESP32 to ensure that the speeds were sufficient.
- Raspberry Pi Scanning and Frame Caching Script
  - Completed the script running locally on the Raspberry Pi hardware that will use YOLOv11 to scan for cars and save the frames locally. When a car enters the garage, the Raspberry Pi uses the native YOLOv11 tracking mechanics to assign a tracking ID for the vehicle. Once the vehicle is out of view of the camera for an adjustable period of time. The script will automatically process all detected frames and send the frame with the highest confidence of a license plate to the Lambda Pipeline
- Lambda Pipeline
  - Mimicked the preexisting Roboflow pipeline in the form of an AWS Lambda function that is accessible through an API Gateway POST request. This request accepts a lot_id and a base64 encoded image and processes the frame image in the same manner as the Roboflow pipeline, ultimately saving the car in the inputted image to the database. The migration was done to remove an unneeded external dependency, while also allowing finer control over the internal interactions of the pipeline.

## Beta Build Completed Work ([Demo](https://youtu.be/lcmvLULVxMY)):
- Configuration script
  - Added conditional branches to allow more user control of setup process
  - Added error control in case of failures in command execution
  - Sets up eduroam connection given UF credentials
  - Sets up USB WiFi drivers
  - Virtual environment and APT command changes
  - Testing
- Tested USB WiFi antenna vs on-board antenna performance metrics
- Tested inference speed of Raspberry Pi and real-world functionality 
- ESP32 access point configured, missing internet connection
- Raspberry Pi Housing v2

## Alpha Build Completed Work:
- Researched, Planned, and Decided on Solution to WiFi Coverage Sparsity
  - Identified potential solutions: LTE modem, LoRa, Repeater
  - Will design an ESP32 repeater to get Raspberry Pi modules onto the UF network for Beta Build
- Configuration script
  - All commands to download and install necessary APT packages to run Pi software
  - Virtual environment setup initialized
- Raspberry Pi Object Detection model
  - Connected to object detection pipeline to AWS backend, finally linking all components together via a shared connection to the backend
  - Still need to work on caching images, tracking, and testing performance

## Design Prototype Completed Work:
- AWS Backend
  - Lots/cars API implemented and functional
  - Functional OCR Pipeline implmenting YOLOv11 object detection and License Plate Recognition
- Raspberry Pi Software
  - YOLOv11 nano model that can identify cars by license plates
  - Outputs live video stream on port
  - Function definitions to interface with AWS backend
- Raspberry Pi Hardware and Housing
  - First iteration of RPi housing to protect RPi and other hardware
  - Configured and interfaced RPi, sensor module, camera module, and replaceable power bank
- Mobile App
  - Wrapper functions to interact with AWS backend
  - App configured to poll parking location information from database and up date fields in real-time  

## Pre-Alpha Completed Work:
- AWS Backend
  - AWS PostgreSQL Database has been configured and setup to store vehicle information
- Raspberry Pi Software
  - Raspberry Pi has been configured and setup to boot with the Raspberry Pi OS
  - Individuals can SSH into the raspberry pi from the UF VPN
  - Connection has been established between the Raspberry Pi and the database
  - Camera method can take a photo when called upon and store it on the RPi
- Raspberry Pi Hardware
  - Camera module is configured
- Mobile App
  - Can establish a connection with PostgreSQL database from within app

## Bugs / Issues:
- **App - Geolocator service no longer works to identify device location** -- WORKING ON
- **App - Occupancy gauge crashes lot info screen when occupancy ratio exceeds 1.0 or falls below 0.0** -- WORKING ON
- **App - initial state displays subset of lots** -- WORKING ON
  - The app contains all lot data in memory, but only displays as subset in the map and list views. This is likely because the default filter setting applies a 'Visitor' DecalType, which restricts lots that can be displayed to those that can be accessed by that DecalType.
- **Blurry real-time photo quality on moving objects.** -- WORKING ON
  - Likely a product of overexposure from slow shutter speed
  - In the process of finding a good balance between gain and exposure time
- **Updates to Lot Entries are recorded in UTC+0 as opposed to UTC+5** -- IGNORED
  - Won't fix, but something to keep in mind.
- **Inconsistent start-up behavior on app** -- RESOLVED
  - During certain times, not all parking locations appear on the map. This is the most normal state of the app; however, during certain particular times, all locations appear, and is associated with unexpected behavior when retrieving data from the database. The resolution to this is not known, though one hypothesis is that the app's code for filtering parking locations from the map and list is somehow involved.
- **Camera turns people blue when viewing live feed** -- RESOLVED
  -  When viewing the camera feed live, red color channels and blue color channels appear to swap. This is evident when pointing the camera at exit signs or at people. This may be a product of the image sensor on the camera module being BGR as opposed to RGB. Despite this, this image bug was resolved by setting the feed configuration to `RGB888` in the script.
- **Raspberry Pi Waiting on I/O** -- IGNORED: Only applies to Raspberry Pi 3B+
  -   When downloading and installing packages with the `apt` package manager and when accessing Python libraries in a Python program, the Pi randomly seems to hang and the scheduler becomes populated by processes waiting for I/O (e.g. ~90% of processes are waiting when running the `top` command in Linux). The root cause is unknown. One hypothesis is that the SD card or the SD card reader may have some sort of defect or is damaged in some way, causing processes needing to access data from the card to wait.
  - This issue tends to be consistently replicated when using VS Code to connect to the RPi, possibly due to VS Code attempting to read the VS Code extension packages installed. This is mostly bypassed by using Jupyter Notebookt to access and program the RPi.
- **Device IP changes occasionally when connecting to the UF network.** -- IGNORED
  - When testing the Raspberry Pi in NEB, SSH-ing worked fine using the IP found when running `ifconfig` in the terminal on the UF network. When it came time to demo the SSH ability in the CpE Design Lab, it did not work. This was because the IP of the device changed. UF IT says they cannot assign a static IP to the device, so there is nothing we can do about this.
- **Not receiving an HDMI signal from Pi to monitor** -- RESOLVED
  - When installing the OS onto the Pi, we were not receiving an output from the HDMI port to a monitor in the NEB computer lab. We assumed we misinstalled the OS image, which resulted in about 3-4 hours of trying to debug the issue and come up with a solution. Upon giving up, the board was connected to a different monitor at home, and the output was received fine. The board was then retested in the NEB computer lab, and it would not output an HDMI signal. This was corrected by changing the boot config files on the Pi by adding the following lines of code.
```
# HDMI force hotplug forces the Pi to output video from HDMI 
# HDMI boost should be a value from 4-9, where 9 is stronger
# HDMI group = 1 should be set for desktop monitors; 2 for TVs
hdmi_force_hotplug=1
config_hdmi_boost=4
hdmi_group=1
```

## Effort
Effort is logged through GitHub using the repository commit history and the GitHub Kanban project linked to this repository. There is also a separate contribution log Excel file in the `ParkingAvailabilitySystem-Documents` folder for contributions that cannot be easily tracked through the aforementioned means. Additionally, work completed is also covered in the stakeholder check-in meeting sheets found in the `ParkingAvailabilitySystem-Documents\Meetings`.