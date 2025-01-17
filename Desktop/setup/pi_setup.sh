#!/bin/bash

# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 01/17/25
#
# Description:
#	Utilizing a fresh Raspberry Pi OS image installed onto a Raspberry Pi 3 Model B+ or greater,
# 	configures the development environment and installs dependencies and packages needed to
#	run the middleware developed in the GitHub repository.

setup() {
	# Configure the Pi to connect to the UF network
	echo "Attempting to connect to UF WiFi . . ."
	sh SecureW2_JoinNow.run
	
	# Install dependencies and packages
	echo "Updating package list . . ."
	sudo apt -y update
	echo "Updating existing packages . . . "
	sudo apt -y upgrade
	echo "Installing packages . . . "
	sudo apt -y install python3-numpy python3-matplotlib python3-opencv jupyter-notebook
	sudo apt -y install openconnect network-manager-openconnect-gnome
	echo "Cleaning up . . . "
	sudo apt -y autoremove 
	
	# Configuring Raspberry Pi settings
	# 1) Boot to console with password (removes GUI for better resources, password for security)
	# 2) Remove splash screen (faster start up)
	# 3) Activate SSH if it is not activated already
	# 4) Activate VNC if it is not activated already
	#
	# References:
	# https://github.com/raspberrypi-ui/rc_gui/blob/master/src/rc_gui.c#L23-L70
	# https://forums.raspberrypi.com/viewtopic.php?t=21632
	sudo raspi-config nonint do_boot_behaviour B1
	sudo raspi-config nonint do_boot_splash 0
	sudo raspi-config nonint do_ssh 1
	sudo raspi-config nonint do_vnc 1
	# TODO: Add additional settings from OS imager just in case
	# TODO: Add config file changes 
	# TODO: Test on virgin Pi
	
	# Add additional commands and behaviors below	
}

main() {
	echo "Running Pi setup script. This will restart the device when finished."
	# Run setup function
	setup
	# Restart for changes
	sudo shutdown -r now
}

main