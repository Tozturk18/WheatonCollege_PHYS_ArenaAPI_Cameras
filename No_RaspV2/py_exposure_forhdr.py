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
from arena_api.buffer import BufferFactory

'''
Exposure: For High Dynamic Range
	This example demonstrates dynamically updating the exposure time in order to
	grab images appropriate for high dynamic range (or HDR) imaging. HDR images
	can be created by combining a number of images acquired at various exposure
	times. This example demonstrates grabbing three images for this purpose,
	without the actual creation of an HDR image.
'''

'''
=-=-=-=-=-=-=-=-=-
=-=- SETTINGS =-=-
=-=-=-=-=-=-=-=-=-
'''
TAB1 = "  "
TAB2 = "    "
num_images = 1
exposure_h = 100000.0
#exposure_high = 0.001 * 1e6
exposure_m = 50000.0
exposure_l = 25000.0


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


def acquire_hdr_images(cameras, SETTINGS):
	'''
	demonstrates exposure configuration and acquisition for HDR imaging
	(1) Sets trigger mode
	(2) Disables automatic exposure
	(3) Sets high exposure time
	(4) Gets first image
	(5) Sets medium exposure time
	(6) Gets second image
	(7) Sets low exposure time
	(8) Gets third images
	(9) Copies images into object for later processing
	(10) Does NOT process copied images
	(11) Cleans up copied images
	'''

	'''
	Get exposure time and software trigger nodes
		The exposure time and software trigger nodes are retrieved beforehand in
		order to check for existance, readability, and writability only once
		before the stream.
	'''
	'''
	Setup stream values
	'''

	for camera in cameras:

		camera.device.start_stream()

	#for i in range(0, num_images):
		'''
		Get high, medium, and low exposure images
			This example grabs three examples of varying exposures for later
			processing. For each image, the exposure must be set, an image must
			be triggered, and then that image must be retrieved. After the
			exposure time is changed, the setting does not take place on the
			device until after the next frame. Because of this, two images are
			retrieved, the first of which is discarded.
		'''
		print(f'{TAB2}Getting HDR image {i}')

		# High exposure time
		camera.nodes['ExposureTime'].value = exposure_h
		#trigger_software_once_armed(nodes)
		image_pre_high = camera.device.get_buffer()
		#trigger_software_once_armed(nodes)
		image_high = camera.device.get_buffer()

	print(f"{TAB1}{TAB2}Image High Exposure {camera.nodes['ExposureTime'].value /  1e6}")

	for camera in cameras:

		# Medium exposure time
		camera.nodes['ExposureTime'].value = exposure_m
		#trigger_software_once_armed(nodes)
		image_pre_mid = camera.device.get_buffer()
		#trigger_software_once_armed(nodes)
		image_mid = camera.device.get_buffer()

	print(f"{TAB1}{TAB2}Image Mid Exposure {camera.nodes['ExposureTime'].value / 1e6}")

	for camera in cameras:

		# Low exposure time
		camera.nodes['ExposureTime'].value = exposure_l
		#trigger_software_once_armed(nodes)
		image_pre_low = camera.device.get_buffer()
		#trigger_software_once_armed(nodes)
		image_low = camera.device.get_buffer()

	print(f"{TAB1}{TAB2}Image Low Exposure {camera.nodes['ExposureTime'].value / 1e6}")

	'''
		Copy images for processing later
		Use the image factory to copy the images for later processing. Images
		are copied in order to requeue buffers to allow for more images to be
		retrieved from the device.
	'''

	'''
		print(f"{TAB2}Copy images for HDR processing later")

		i_high = BufferFactory.copy(image_high)
		hdr_images.append(i_high)
		i_mid = BufferFactory.copy(image_mid)
		hdr_images.append(i_mid)
		i_low = BufferFactory.copy(image_low)
		hdr_images.append(i_low)
	'''
		
	Save_Image.save_image(image_pre_high.pdata, image_pre_high.height, image_pre_high.width)
	Save_Image.save_image(image_high.pdata, image_high.height, image_high.width)
	Save_Image.save_image(image_pre_mid.pdata, image_pre_mid.height, image_pre_mid.width)
	Save_Image.save_image(image_mid.pdata, image_mid.height, image_mid.width)
	Save_Image.save_image(image_pre_low.pdata, image_pre_low.height, image_pre_low.width)
	Save_Image.save_image(image_low.pdata, image_low.height, image_low.width)

	for camera in cameras:
		# Requeue buffers
		camera.device.requeue_buffer(image_pre_high)
		camera.device.requeue_buffer(image_high)
		camera.device.requeue_buffer(image_pre_mid)
		camera.device.requeue_buffer(image_mid)
		camera.device.requeue_buffer(image_pre_low)
		camera.device.requeue_buffer(image_low)

		camera.device.stop_stream()

def restore_initials(cameras):

	print("\nRestoring Configuration to Initials...\n")

	# Restore initial values
	for camera in cameras:
		camera.restore_initials()


def example_entry_point():

	# Try to run the program
	try:
		# List the devices connected to the computer
		devices = Arena_Helper.update_create_devices()
		
		# Get the cameras and the SETTINGS to use from the user
		cameras, SETTINGS = link_cameras_to_devices(devices)

		# Configure the cameras
		Camera_Object.configure_cameras(cameras)

		input("Ready to initiate imaging.\nWaiting for User input...")

		# Record the initial start time in nanoseconds
		initial_time = time.time_ns()

		acquire_hdr_images(cameras, SETTINGS)

		# Calculate the total time this program took
		total_time = time.time_ns() - initial_time

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
