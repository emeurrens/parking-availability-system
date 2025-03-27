#!/bin/bash

# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 03/27/25
#
# Description:
#	Utilizing a fresh Raspberry Pi OS image installed onto a Raspberry Pi 3 Model B+ or greater,
# 	configures the network connection to UF WiFi, the development environment, and installs dependencies and packages 
#	needed to run the middleware developed in the Parking Availability System GitHub repository.
#
# Resources:
# - Very useful bash scripting guide: https://mywiki.wooledge.org/BashGuide
# - Realtek 8821cu WiFi chipset driver: https://github.com/morrownr/8821cu-20210916

REPO_NAME="parking-availability-system"
LOCAL_PATH="$HOME/$REPO_NAME/Desktop/setup"

# LMAO something went wrong. IDIOT! Now you die HAHA! (Please don't take this personally)
# In all seriousness, if you reach this point, you need to rerun the script
die() {
	# Print provided argument for error string and 
	# exit with error code 1 (number is arbitrary; 0 means success, anything else is failure)
	echo $1
	exit 1
}

# Pre-reboot setup function
setup_1() {
	# Set current working directory
	cd $LOCAL_PATH

	###############################################
	# Configure the Pi to connect to the UF network
	###############################################
	echo "Attempting to connect to UF WiFi . . . "
	sudo nmcli device wifi rescan ifname wlan0
	
	# Check if there already exists an eduroam connection
	if nmcli connection show | grep --silent "eduroam"
	then
		echo "Connection profile for 'eduroam' already exists."
	else
		# Attempt to connect Pi to the ufgetonline network, kill script on failure
		sudo nmcli device wifi connect ufgetonline
		if [[ $? -ne 0 ]]
		then
			echo
			die "ERROR: Failed to connect to 'ufgetonline' network. Killing script."
		fi

		# Attempt to connect to eduroam, kill script on failure
		echo
		echo "Please enter your ONE.UF credentials" 
		read -p "Username: " username
		read -s -p "Password: " password
		echo
		sudo nmcli connection add \
			type wifi \
			ifname wlan0 \
			con-name eduroam \
			ssid eduroam \
			wifi-sec.key-mgmt wpa-eap \
			ipv4.method auto \
			802-1x.eap peap \
			802-1x.phase2-auth mschapv2 \
			802-1x.identity "${username}@ufl.edu" \
			802-1x.password "$password" \
			802-1x.ca-cert "$LOCAL_PATH/2b8f1b57330dbba2d07a6c51f70ee90ddab9ad8e.cer"
		unset password		
		sudo nmcli connection modify eduroam connection.autoconnect yes
		sudo nmcli connection up eduroam
		if [[ $? -ne 0 ]]
		then
			sudo nmcli connection delete eduroam
			die "ERROR: Failed to connect to 'eduroam' network. Killing script."
		fi	 
	fi
	
	###############################################################
	# Install dependencies and packages through APT package manager
	###############################################################
	echo
	echo "Updating package list . . ." && \
	sudo apt -y -o Acquire::ForceIPv4=true update && \
	echo && \
	echo "Upgrading existing packages . . . " && \
	sudo apt -y -o Acquire::ForceIPv4=true upgrade && \
	echo && \
	echo "Installing packages . . . " && \
	sudo apt -y -o Acquire::ForceIPv4=true install python3-numpy python3-matplotlib python3-pandas jupyter-notebook && \
	sudo apt -y -o Acquire::ForceIPv4=true install openconnect network-manager-openconnect-gnome && \
	sudo apt -y -o Acquire::ForceIPv4=true install libcap-dev libcamera-dev && \
	echo && \
	echo "Cleaning up . . . " && \
	sudo apt -y -o Acquire::ForceIPv4=true autoremove
	if [[ $? -ne 0 ]]
	then
		die "ERROR: Failed to install dependencies and packages through APT package manager"
	fi
}

# Post-reboot setup function
setup_2() {
	####################################
	# Configure USB wifi antenna adapter
	####################################
	echo
	read -p "Should a USB WiFi antenna be configured? [y/N]: " ant_response
	if [[ $ant_response = "y" ]]
	then 
		echo "Configuring USB WiFi antenna adapter . . ."

		# Verify USB WiFi adapter is plugged in
		read -p "Press 'Enter' key to confirm USB WiFi adapter is plugged into a USB 2.0 port before proceeding: "

		device=$(lsusb | grep --color=never "Realtek" || lsusb | grep --color=never "802.11")
		if [[ $device != "" ]]
		then
			device_id=$(echo $device | grep -o -E "ID.{0,10}")
			echo "Identified USB WiFi device:"
			echo $device
			echo
		else
			die "ERROR: Failed to identify a USB WiFi device"	
		fi

		# Verify default drivers are installed
		sudo apt -y -o Acquire::ForceIPv4=true install --reinstall firmware-realtek
		
		#
		# Depending on the chipset, there are specific drivers available
		# The below commands installs the drivers for USB WiFi adapters
		# 	based on the RTL8811CU, RTL8821CU, RTL8821CUH, and RTL8731AU chipsets
		# Driver repository link: https://github.com/morrownr/8821cu-20210916
		#
		sudo apt -y -o Acquire::ForceIPv4=true install raspberrypi-kernel-headers build-essential bc dkms git
		git clone https://github.com/morrownr/8821cu-20210916.git
		cd 8821cu-20210916
		# If current device is in list of devices, install drivers, otherwise don't bother
		if cat ./supported-device-IDs | grep -i --silent "$device_id"
		then 
			echo
			sudo ./install-driver.sh
			cd .. 
		else
			cd ..
			sudo rm -rf 8821cu-20210916
		fi
		sudo apt -y -o Acquire::ForceIPv4=true autoremove
	else
		echo "Skipping USB WiFi antenna adapter configuration"
	fi
	
	###########################################################################################
	# Configuring Raspberry Pi settings
	# 1) Boot to console with password (removes GUI for better resources, password for security)
	# 2) Remove splash screen (faster start up)
	# 3) Activate SSH if it is not activated already
	# 4) Activate VNC if it is not activated already
	# 5) Disable bluetooth module (Don't need it running)
	#
	# References:
	# https://github.com/raspberrypi-ui/rc_gui/blob/master/src/rc_gui.c#L23-L70
	# https://forums.raspberrypi.com/viewtopic.php?t=21632
	###########################################################################################
	echo 
	echo "Configuring Raspberry Pi settings . . . "
	sudo raspi-config nonint do_boot_behaviour B1
	sudo raspi-config nonint do_boot_splash 1
	sudo raspi-config nonint do_ssh 0
	sudo raspi-config nonint do_vnc 0
	if ! grep --silent "dtoverlay=disable-bt" /boot/firmware/config.txt
	then
		sudo bash -c "echo "dtoverlay=disable-bt" >> /boot/firmware/config.txt"
	fi
	if ! grep --silent "dtoverlay=disable-wifi" /boot/firmware/config.txt && [[ $ant_response = "y" ]]
	then
		sudo bash -c "echo "dtoverlay=disable-wifi" >> /boot/firmware/config.txt"
	fi

	###################################################
	# Creating virtual environment for Python libraries
	###################################################
	cd ..
	echo
 	echo "Creating virtual environment . . ."
  	python -m venv --system-site-packages car_detection
   	echo "Activating virtual environment . . ."
   	cd car_detection
    	. bin/activate 
	echo "Installing necessary packages to make inferences on camera feed . . ."
	pip install opencv-python torchvision torch git+https://github.com/ultralytics/ultralytics.git@main 
}

main() {
	echo
	echo "Running Pi setup script . . . "

	# Run setup function
	if [ -f "$LOCAL_PATH/setup_checkpoint" ]
	then
		echo
		read -p "A checkpoint from a previous setup session was detected. Would you like to continue? [Y/n]: " cont_response
		if [[ $cont_response != "n" ]]
		then
			setup_2
			echo
			echo "Restarting device to complete setup . . . "
			echo
			sudo rm -f "$LOCAL_PATH/setup_checkpoint" 
		else
			sudo rm -f "$LOCAL_PATH/setup_checkpoint"
			die "User chose to terminate setup script prior to completion"
		fi
	else
		echo "This will require multiple restarts."
		echo 
		setup_1
		echo
		echo "Restarting device to apply updated packages. Please rerun the script when the device restarts to continue . . . "
		echo
		echo "$(date)" > $LOCAL_PATH/setup_checkpoint
	fi

	# Restart for changes
	sudo reboot
}

main
exit 0