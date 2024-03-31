# -----------------------------------------------------------------------------
# Copyright (c) 2022, Lucid Vision Labs, Inc.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

import Camera_Object
import Arena_Helper
import Camera_Detection
import Save_Image
import Parse_CSV
import time
import sys
from arena_api.system import system


'''
	Take the user input and match them to the devices connected
	to the computer by mating serial numbers to r, g, or b
'''
def link_cameras_to_devices(devices):

	# Get the input file name
	INPUT_FILENAME = Camera_Detection.getArgs()

	# Get camera, set exposure time, offset, gain for the image
	SETTINGS = Parse_CSV.load_camera_settings(INPUT_FILENAME)

	# Load the settings to individual variables for code readability
	cams 		= SETTINGS[0].cameras
	exposure 	= SETTINGS[0].exposure
	offset		= SETTINGS[0].offset
	gain 		= SETTINGS[0].gain
	buffer_num	= SETTINGS[0].number

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
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], exposure, offset, gain, buffer_num)

		# If the user entered the camera names according to numbers
		elif cam == '0' or cam == '1' or cam == '2':
			# Get the device number
			devNum = int(cam)
			# Find which camera it belongs to
			camSrl = srlDetected[devNum]
			# Get the camera name
			cam = Camera_Detection.serialToCamera(camSrl)
			# Create a new Camera Object
			cameras[i] = Camera_Object.Camera(cam, devices[devNum], exposure, offset, gain, buffer_num)

		else:
			print('Ill-defined cam. Quitting...')
			sys.exit(0)

	return cameras, SETTINGS

def trig(cameras):
	while any(not bool(camera.nodemap['TriggerArmed'].value) for camera in cameras):
		pass

	for camera in cameras:
		# retrieve and execute software trigger node
		camera.nodemap['TriggerSoftware'].execute()


def acquire_hdr_images(cameras, SETTINGS, cam_buffer):

	for INDEX in range(len(SETTINGS)):

		if INDEX > 0:
			Camera_Object.change_config(cameras,SETTINGS,INDEX)
			trig(cameras)
			for camera in cameras:
				camera.device.get_buffer()

		for count in range(SETTINGS[INDEX].number):
			print(f"Buffer count: {count+1} / {SETTINGS[INDEX].number}")
			
			trig(cameras)
			for camera in cameras:
				buffer = camera.device.get_buffer()
				print(
					f'\tbuffer{count+1:{2}} received | '
					f'Width = {buffer.width} pxl, '
					f'Height = {buffer.height} pxl, '
					f'Pixel Format = {buffer.pixel_format.name}')
				cam_buffer[camera].append(buffer)
			
	return cam_buffer

def restore_initials(cameras):

	print("\nRestoring Configuration to Initials...\n")

	# Restore initial values
	for camera in cameras:
		camera.restore_initials()

def save_images(cam_buffer):
	for camera in cam_buffer:
		for buffer in cam_buffer[camera]:
			# Save the image
			Save_Image.save_image(camera, buffer.pdata, buffer.height, buffer.width)
			print("\nImage Saved\n")
			camera.device.requeue_buffer(buffer)

def example_entry_point():

	# Try to run the program
	try:
		# List the devices connected to the computer
		devices = Arena_Helper.update_create_devices()
		
		# Get the cameras and the SETTINGS to use from the user
		cameras, SETTINGS = link_cameras_to_devices(devices)

		# Configure the cameras
		Camera_Object.configure_cameras(cameras, SETTINGS)

		cam_buffer = {}
		for camera in cameras:
			cam_buffer[camera] = []

		input("Ready to initiate imaging.\nWaiting for User input...")

		# Record the initial start time in nanoseconds
		initial_time = time.time_ns()

		acquire_hdr_images(cameras, SETTINGS, cam_buffer)

		# Calculate the total time this program took
		total_time = time.time_ns() - initial_time

		save_images(cam_buffer)

		# Restore all the camera settings to initials
		restore_initials(cameras)

		# Print out the total time
		print("\nTotal time: ", total_time/6e10)

	# Press CTRL+C to end the program early
	except KeyboardInterrupt:
		# Restore the cameras to their initials
		restore_initials(cameras)


if __name__ == "__main__":
	print("Example Started\n")
	example_entry_point()
	print("\nExample Completed")
