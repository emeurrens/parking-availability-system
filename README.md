# Parking Availability System (PAS)
The Parking Availability System (PAS) was inspired by the lack of easily available parking resources on campus and would promote quicker and more reliable transportation to and from campus. It represents a small-scale, hardware/software system providing a relatively low-cost solution for predicting parking availability accurately within parking garages on campus. 

## Audience & Use Case: 
Live parking data is only available at a select few locations on campus, making it difficult for those who must drive to campus to find parking during busy periods. This information would be beneficial for off-campus commuters and visitors, and can be used by UF Transit and Parking Services (UF TAPS) and the UF Transportation Institute (UFTI) for to improve parking facilities on campus. You don’t want to drive into a parking garage, realize there’s no parking, and fumble around on your phone, in the middle of the garage, for minutes trying to find another place to park. This product could reduce the stress of finding parking on campus.

## Comparable Solutions:
There are multiple comparable existing devices from various vendors used to monitor real-time parking information. Some solutions for determining parking availability include counting availability at every individual space, and then there are other, typically cheaper, solutions that count cars into and out of a parking facility. These solutions are then further split between visual and non-visual solutions. Non-visual solutions include in-ground induction loops, radar sensors, ultrasonic sensors, and magnetometer sensors.  Visual solutions involve using cameras to determine parking availability. The university currently employs Genetec's parking system, which is utilized on campus, requires a prohibitively expensive cost of $8000-11000 to set up per entrance/exit lane, with a recurring cost for the service of $6000 per year or $500 per month. The goal of this project is to develop a relatively low-cost solution to these alternatives that will have comparable accuracy without the prohibitive cost, so that it could be expanded to other parking facilities on campus.

## Core Features:
- Vehicle Detection
- Facility Parking Availability Prediction
  - Accessible via mobile app for users
- License Plate Recognition

## Completed Work:
- AWS
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

## Bugs:
- Raspberry Pi Waiting on I/O
  -   When downloading and installing packages with the `apt` package manager and when accessing Python libraries in a Python program, the Pi randomly seems to hang and the scheduler becomes populated by processes waiting for I/O (e.g. ~90% of processes are waiting when running the `top` command in Linux). The root cause is unknown. One hypothesis is that the SD card or the SD card reader may have some sort of defect or is damaged in some way, causing processes needing to access data from the card to wait.
- Device IP changes occasionally when connecting to the UF network.
  - When testing the Raspberry Pi in NEB, SSH-ing worked fine using the IP found when running `ifconfig` in the terminal on the UF network. When it came time to demo the SSH ability in the CpE Design Lab, it did not work. This was because the IP of the device changed. UF IT says they cannot assign a static IP to the device, so there is nothing we can do about this.
- Not receiving an HDMI signal from Pi to monitor
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
Effort is logged through GitHub using the repository commit history and the GitHub Kanban project linked to this repository. There is also a separate contribution log Excel file in the `ParkingAvailabilitySystem-Documents` folder for contributions that cannot be easily tracked through the aforementioned means.

