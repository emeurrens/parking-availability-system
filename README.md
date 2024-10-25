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
  - Raspberry Pi has been configured and setup to boot with the Raspbian OS
  - Individuals can SSH into the raspberry pi from the UF VPN
  - Connection has been established between the Raspberry Pi and the database
- Raspberry Pi Hardware
  - 
- Research efforts
  - 

## Architecture:

## Bugs:
