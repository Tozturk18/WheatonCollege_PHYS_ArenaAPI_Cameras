#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# File Title: External Triggering and Image Acquisition with Multiple Camera
# Author: Ozgur Tuna Ozturk 24', Sayed 25', Prof. Dr. Dipakar Maitra
# Description: This program uses arena_api to connect to multiple cameras 
# 	at the same time and take pictures at the same time using external trigger.
#	This program also buffers the images and slowly gets the images from the cameras.
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
	to the computer by mating serial numbers to r, g, or b
'''
def link_cameras_to_devices(devices):

	# Get the input file name
	INPUT_FILENAME = Camera_Detection.getArgs()

	# Get camera, set exposure time, offset, gain for the image
	SETTINGS = Parse_CSV.load_camera_settings(INPUT_FILENAME)

	cams 		= SETTINGS[INDEX].cameras
	exposure 	= SETTINGS[INDEX].exposure
	offset		= SETTINGS[INDEX].offset
	gain 		= SETTINGS[INDEX].gain
	

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
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], exposure, offset, gain, NUMBER_OF_BUFFERS)

		# If the user entered the camera names according to numbers
		elif cam == '0' or cam == '1' or cam == '2':
			# Get the device number
			devNum = int(cam)
			# Find which camera it belongs to
			camSrl = srlDetected[devNum]
			# Get the camera name
			cam = Camera_Detection.serialToCamera(camSrl)
			# Create a new Camera Object
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], exposure, offset, gain, NUMBER_OF_BUFFERS)

		else:
			Arena_Helper.safe_print('Ill-defined cam. Quitting...')
			sys.exit(0)

	return cameras, SETTINGS

def get_multiple_image_buffers(camera):
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
		Save_Image.save_image(camera, buffer.pdata, buffer.height, buffer.width)
		Arena_Helper.safe_print("\nImage Saved\n")

		'''
		`Device.requeue_buffer()` takes a buffer or many buffers in a list or
		tuple
		'''
		camera.device.requeue_buffer(buffer)

def initiate_imaging(cameras, SETTINGS, INDEX):

	for INDEX in range(len(SETTINGS)):
	
		Camera_Object.change_config(cameras, SETTINGS, INDEX)

		Arena_Helper.safe_print("Ready!")

		for camera in cameras:
			get_multiple_image_buffers(camera)

def restore_initials(cameras):

	Arena_Helper.safe_print("\nRestoring Configuration to Initials...\n")

	# Restore initial values
	for camera in cameras:
		camera.restore_initials()

def entry_point():

	try:

		initial_time = time.time_ns()

		devices = Arena_Helper.update_create_devices()
		
		cameras, SETTINGS = link_cameras_to_devices(devices)

		Camera_Object.configure_cameras(cameras)

		input("Waiting for user input...")

		initiate_imaging(cameras, SETTINGS, INDEX)

		restore_initials(cameras)

		total_time = time.time_ns() - initial_time

		Arena_Helper.safe_print("Total time: ", total_time)

	# Press CTRL+C to end the program early
	except KeyboardInterrupt:
		# Restore the cameras to their initials
		restore_initials(cameras)

if __name__ == "__main__":
	entry_point()
