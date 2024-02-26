#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# File Title: External Triggering and Image Aquisition with Multiple Camera
# Author: Ozgur Tuna Ozturk 24', Sayed 25', Prof. Dr. Dipakar Maitra
# Description: This program uses arena_api to connect to multiple cameras 
# 	at the same time and take pictures at the same time using external trigger.
#	This program also buffers the images and slowly gets the images from the camers.
# -----------------------------------------------------------------------------


import Camera_Object
import Arena_Helper
import Camera_Detection
import Save_Image
import Parse_CSV
import threading
import time
import serial

from arena_api.system import system

# Number of buffers allocated for a device stream
NUMBER_OF_BUFFERS = 1
INDEX = 0

'''
	Take the user input and match them to the devices connected
	to the computer by mathing serial numbers to r, g, or b
'''
def link_cameras_to_devices(devices):

	# Get camera, set exposure time, offset, gain for the image
	#cams, myexptime_s, myoffset_adu, mygain_db = Camera_Detection.getArgs()
	

	SETTINGS = Parse_CSV.loadSettings("input.csv")

	cams 			= SETTINGS[INDEX].cameras
	myexptime_s 	= SETTINGS[INDEX].exposure
	myoffset_adu 	= SETTINGS[INDEX].offset
	mygain_db 		= SETTINGS[INDEX].gain
	

	# Get the devices currently connected to the computer
	devices = Arena_Helper.update_create_devices()
	# Get the serial numbers of the devices connected
	srlDetected = Camera_Detection.getSerial(devices)

	cameras = [None] * len(cams)

	# Go through each device and determine the camera
	for i, cam in enumerate(cams):
		# If the user entered the camera names according to colors
		if cam == 'r' or cam == 'g' or cam == 'b':
			# Get the camera serial number for the selected cam for device detection
			camSrl = Camera_Detection.cameraToSerial(cam)
			# Find which device it belongs to
			devNum = Camera_Detection.findCamInDetectedDeviceList(camSrl, srlDetected)
			# Create a new Camera object
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], myexptime_s, myoffset_adu, mygain_db, NUMBER_OF_BUFFERS)

		# If the user entered the camera names according to numbers
		elif cam == '0' or cam == '1' or cam == '2':
			# Get the device number
			devNum = int(cam)
			# Find which camera it belongs to
			camSrl = srlDetected[devNum]
			# Get the camera name
			cam = Camera_Detection.serialToCamera(camSrl)
			# Create a new Camera Object
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], myexptime_s, myoffset_adu, mygain_db, NUMBER_OF_BUFFERS)

		else:
			Arena_Helper.safe_print('Ill-defined cam. Quitting...')
			sys.exit(0)

	return cameras, SETTINGS

def get_multiple_image_buffers(camera, ser):
	'''
	This function demonstrates an acquisition on a device

	(1) Start stream with N buffers
	(2) Print each buffer info
	(3) Requeue each buffer
	'''

	# Print image buffer info
	for count in range(NUMBER_OF_BUFFERS):

		buffer = camera.device.get_buffer()

		Arena_Helper.safe_print(
				f'\tbuffer{count:{2}} received | '
				f'Width = {buffer.width} pxl, '
				f'Height = {buffer.height} pxl, '
				f'Pixel Format = {buffer.pixel_format.name}')

		''' Save Image '''
		Save_Image.save_image(camera, buffer.pdata, buffer.height, buffer.width, ser)
		Arena_Helper.safe_print("\nImage Saved\n")

		'''
		`Device.requeue_buffer()` takes a buffer or many buffers in a list or
		tuple
		'''
		camera.device.requeue_buffer(buffer)

def initiate_imaging(cameras, SETTINGS, INDEX, ser):

	for INDEX in range(len(SETTINGS['exp'])):
	
		Camera_Object.change_config(cameras, SETTINGS, INDEX)

		ser.write('a')

		Arena_Helper.safe_print("Ready!")

		for camera in cameras:
			get_multiple_image_buffers(camera, ser)

def restore_initials(cameras):

	Arena_Helper.safe_print("\nRestoring Configuration to Initials...\n")

	# Restore initial values
	for camera in cameras:
		camera.restore_initials()

def entry_point():

	devices = Arena_Helper.update_create_devices()
	
	cameras, SETTINGS = link_cameras_to_devices(devices)

	Camera_Object.configure_cameras(cameras)

	# Baud rate is 3M ~ 333.33ns per character
	ser = serial.Serial('/dev/tty.USB0', 3000000, timeout=0.1)

	initiate_imaging(cameras, SETTINGS, INDEX, ser)

	restore_initials(cameras)

if __name__ == "__main__":
	entry_point()
