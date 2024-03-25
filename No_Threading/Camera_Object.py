import Arena_Helper
from arena_api.system import system
import math
import time

'''
Camera object
 - Description:
	This camera object contains all the device information
'''
class Camera:

	# Arrays needed for saving the image taken by the camera
	dev_serial = '' # Serial number of the camera
	dev_power = ''  # Power of the camera
	dev_model = ''  # Model number of the camera

	# Initialize the camera
	def __init__(self, name, device, exposure, offset, gain, buffers):

		# Save the name of the device (r, g, or b)
		self.name = name
		# Save the arena_api camera device
		self.device = device
		# Save the picture settings
		'''self.exposure = exposure
		self.offset = offset
		self.gain = gain'''
		self.buffers = buffers
		
		# Pull the nodemaps from device
		self.nodemap = self.device.nodemap
		self.tl_stream_nodemap = self.device.tl_stream_nodemap

		self.get_nodes()
		
		# Enable frame rate change, if needed
		if self.nodemap['AcquisitionFrameRateEnable'].value is False:
			self.nodemap['AcquisitionFrameRateEnable'].value = True

		# Set the camera settings
		# Set the exposure, offset, and gain only if they are different then previous
		self.__set_exposure(exposure)
		self.__set_offset(offset)
		self.__set_gain(gain)
		
		# Notify the user of new camera configuration
		print(
			'\nCamera: ', self.name,
			'\nImages:', self.nodes['Width'].value, 'x',  self.nodes['Height'].value, self.nodes['PixelFormat'].value,
			'\nTemperature (C)\t=', self.nodes['DeviceTemperature'].value, 
			'\nFramerate (Hz) \t=', self.nodes['AcquisitionFrameRate'].value, 
			'\nExptime (s)    \t=', self.exposure,
			'\nOffset (ADU)   \t=', self.offset,
			'\nGain (dB)      \t=', self.gain,
			'\nBuffer Number  \t=', self.buffers)

	def get_nodes(self):
		# Stores the nodes needed for setting up the camera settings
		self.nodes = self.nodemap.get_node(
							['TriggerSelector', 'TriggerMode','TriggerSource', 
							'TriggerActivation','Width', 'Height', 
							'PixelFormat', 'AcquisitionMode', 'AcquisitionStartMode', 'PtpEnable', 'PtpStatus','DeviceTemperature', 
							'AcquisitionFrameRate', 'ExposureTime', 'BlackLevelRaw', 
							'Gain', 'DeviceSerialNumber','DeviceModelName','DevicePower','GevSCPD', 'DeviceStreamChannelPacketSize']
							)

		# Set some initial values
		self.nodes['Width'].value = self.nodes['Width'].max
		self.nodes['Height'].value = self.nodes['Height'].max
		self.nodes['PixelFormat'].value = 'Mono12'

		self.__store_initials()

	def __store_initials(self):
		# Save initial values to restore them before ending the program
		self.initial_values  = [
			self.nodes['TriggerSelector'].value, self.nodes['TriggerMode'].value,
			self.nodes['TriggerSource'].value, self.nodes['TriggerActivation'].value,
			self.nodes['AcquisitionMode'].value, self.tl_stream_nodemap['StreamBufferHandlingMode'].value,
			self.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value, self.tl_stream_nodemap['StreamPacketResendEnable'].value,
			self.nodes['GevSCPD'].value,
			self.nodes['AcquisitionStartMode'].value, self.nodes['PtpEnable'].value,
			self.nodes['DeviceStreamChannelPacketSize'].value
			]

	def restore_initials(self):

		self.device.stop_stream()

		self.nodes['TriggerSelector'].value = self.initial_values[0]
		self.nodes['TriggerMode'].value = self.initial_values[1]
		self.nodes['TriggerSource'].value = self.initial_values[2]
		self.nodes['TriggerActivation'].value = self.initial_values[3]
		self.nodes['AcquisitionMode'].value = self.initial_values[4]
		self.tl_stream_nodemap['StreamBufferHandlingMode'].value = self.initial_values[5]
		self.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = self.initial_values[6]
		self.tl_stream_nodemap['StreamPacketResendEnable'].value = self.initial_values[7]
		self.nodes['GevSCPD'].value = self.initial_values[8]
		self.nodes['AcquisitionStartMode'].value = self.initial_values[9]
		self.nodes['PtpEnable'].value = self.initial_values[10]
		self.nodes['DeviceStreamChannelPacketSize'].value = self.initial_values[11]
		
		print("\nCamera: ", self.name,
			"\nTriggerSelector: ", self.nodes['TriggerSelector'].value,
			"\nTriggerMode: ", self.nodes['TriggerMode'].value,
			"\nTriggerSource: ", self.nodes['TriggerSource'].value,
			"\nTriggerActivation: ", self.nodes['TriggerActivation'].value,
			"\nAcquisitionMode: ", self.nodes['AcquisitionMode'].value,
			"\nStreamBufferHandlingMode: ", self.tl_stream_nodemap['StreamBufferHandlingMode'].value,
			"\nStreamAutoNegotiatePacketSize: ", self.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value,
			"\nStreamPacketResendEnable: ", self.tl_stream_nodemap['StreamPacketResendEnable'].value,
			"\nGevSCPD: ", self.nodes['GevSCPD'].value,
			"\nAcquisitionStartMode: ", self.nodes['AcquisitionStartMode'].value,
			"\nPtpEnable: ", self.nodes['PtpEnable'].value,
			"\nDeviceStreamChannelPacketSize: ", self.nodes['DeviceStreamChannelPacketSize'].value)

	def __set_framerate(self):
		# Make sure the framerate is such that an exposure can be taken
		# between two successive frames
		framerate = 0.90 / self.exposure

		# However don't go beyond the camera's maximum frame rate
		maxframerate = self.nodes['AcquisitionFrameRate'].max
		if framerate > maxframerate:
			framerate = maxframerate

		# Set camera's framerate
		self.nodes['AcquisitionFrameRate'].value = framerate

	def __set_exposure(self, exposure):

		# Set the exposure
		self.exposure = exposure

		# Adjust the framerate before changing the exposure
		self.__set_framerate()

		# Turn off auto exposure [possibilities are Continuous or Off]
		# And check to make sure we can change the exposure time
		if self.nodemap['ExposureAuto'].value == 'Continuous':
			self.nodemap['ExposureAuto'].value = 'Off'
		if self.nodemap['ExposureTime'] is None:
			raise Exception("ExposureTime node not found")
		if self.nodemap['ExposureTime'].is_writable is False:
			raise Exception("ExposureTime node is not writable")

		# Set the exposure time (internally in microseconds)
		self.nodes['ExposureTime'].value = self.exposure * 1e6

	def __set_offset(self, offset):

		# Set the offset
		self.offset = offset

		# Set the black level (offset) in ADU
		self.nodes['BlackLevelRaw'].value = self.offset

	def __set_gain(self, gain):

		# Set the gain
		self.gain = gain

		# Turn off automatic gain [possibilities are Continuous or Off]
		if self.nodemap['GainAuto'].value == 'Continuous':
			self.nodemap['GainAuto'].value = 'Off'
		
		# Change Gain levels
		self.nodes['Gain'].value = self.gain

	def _change_config(self, exposure, offset, gain, buffer_num):

		# Stop the stream to edit the camera configuration
		#self.device.stop_stream()
		
		# Set the exposure, offset, and gain only if they are different then previous
		if exposure != self.exposure:
			print("changing exposure!")
			self.__set_exposure(exposure)
		if offset != self.offset:
			print("changing offset!")
			self.__set_offset(offset)
		if gain != self.gain:
			print("changing gain!")
			self.__set_gain(gain)
		
		self.buffers = buffer_num
		
		# Notify the user of new camera configuration
		print(
			'\nCamera: ', self.name,
			'\nImages:', self.nodes['Width'].value, 'x',  self.nodes['Height'].value, self.nodes['PixelFormat'].value,
			'\nTemperature (C)\t=', self.nodes['DeviceTemperature'].value, 
			'\nFramerate (Hz) \t=', self.nodes['AcquisitionFrameRate'].value, 
			'\nExptime (s)    \t=', self.exposure,
			'\nOffset (ADU)   \t=', self.offset,
			'\nGain (dB)      \t=', self.gain,
			'\nBuffer Number  \t=', self.buffers)
		
		# Restart the after changing camera configuration
		#self.device.start_stream(self.buffers)


def configure_cameras(cameras):
	''' Configure all the necessary settings for imaging '''

	# Iterate through each camera
	for cam, camera in enumerate(cameras):
	
		print("\n",camera,"\n")
		# Set acquisition mode to continuous
		camera.nodes["AcquisitionMode"].value = "Continuous"
		camera.nodes["AcquisitionStartMode"].value = "Normal"

		# Enable Ptp
		camera.nodes["PtpEnable"].value = True

		
		# Enable external trigger
		camera.nodes['TriggerSelector'].value = 'FrameStart'
		camera.nodes['TriggerActivation'].value = 'RisingEdge'
		camera.nodes['TriggerMode'].value = 'On'
		camera.nodes['TriggerSource'].value = 'Line0'

		''' Setup stream values'''

		# Set buffer handling mode to "Newest First"
		camera.tl_stream_nodemap["StreamBufferHandlingMode"].value = "NewestOnly"
		# Enable stream auto negotiate packet size
		camera.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value = True
		# Enable stream packet resend
		camera.tl_stream_nodemap['StreamPacketResendEnable'].value = True

		camera.nodes['DeviceStreamChannelPacketSize'].value = camera.nodes['DeviceStreamChannelPacketSize'].max
		
		total		= len(cameras)
		packetSize	= 9014		# Bytes
		devLink		= 125000000	# 1 Gbps
		a_buffer	= 0.1093	# 10.93%
		delay = packetSize * (10**9)/devLink
		
		delay = delay + (delay * a_buffer)
		
		camera.nodes['GevSCPD'].value = int( math.ceil( delay * (total - 1) / 10000) * 10000 )
		
		print('GevSCPD: ', camera.nodes['GevSCPD'].value)

		# store camera values
		camera.dev_serial   =  camera.nodes['DeviceSerialNumber'].value
		camera.dev_power    = camera.nodes['DevicePower'].value
		camera.dev_model    = camera.nodes['DeviceModelName'].value

	masterfound = False
	restartSyncCheck = True

	while restartSyncCheck and not masterfound:
		restartSyncCheck = False

		# Get the PTP status for all the cameras
		ptp_statuses = [camera.nodes['PtpStatus'].value for camera in cameras]

		# Check if there are any Masters in PTP_Statuses
		if any(status == "Master" for status in ptp_statuses):
			if masterfound:
				# There are still multiple masters, continue negotiating
				restartSyncCheck = True
			masterfound = True
		elif any(status != "Slave" for status in ptp_statuses):
			# There are still undefined cameras
			restartSyncCheck = True

	# Notify the user
	print("PTP sync check done!")

	for camera in cameras:
		# Start stream with the number of buffers
		camera.device.start_stream()

	# Wait until all cameras have the trigger armed
	while any(not bool(camera.nodemap['TriggerArmed'].value) for camera in cameras):
		pass


def change_config(cameras, SETTINGS, INDEX):

	cams 	    = SETTINGS[INDEX].cameras
	exposure 	= SETTINGS[INDEX].exposure
	offset      = SETTINGS[INDEX].offset
	gain 		= SETTINGS[INDEX].gain
	buffer_num	= SETTINGS[INDEX].number

	gen = (camera for camera in cameras if camera.name in cams)

	
	for camera in gen:
		print(camera.name)
		camera._change_config(exposure,offset,gain,buffer_num)
