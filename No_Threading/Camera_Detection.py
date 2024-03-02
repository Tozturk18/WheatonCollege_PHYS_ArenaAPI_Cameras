import numpy as np
import argparse
import sys

import Arena_Helper
import Camera_Object

# Serial numbers of the cameras, in [r, g, b] order
rgbSerial = np.array([213301046, 211300110, 223200097])

def getSerial(devices):
	nDevFound: int = len(devices)
	detectedSerials = np.zeros(nDevFound, dtype=np.uint32)
	ii=0
	for device in devices:
		detectedSerials[ii] = device.nodemap.get_node("DeviceSerialNumber").value
		ii+=1

	return detectedSerials


def cameraToSerial(camName: str):
	# Given camera name (r or g or b),
	# return the serial number of that camera.
	if camName == 'r':
		serial = rgbSerial[0]
	elif camName == 'g':
		serial = rgbSerial[1]
	elif camName == 'b':
		serial = rgbSerial[2]
	else:
		Arena_Helper.safe_print('This should not happen. Quitting')
		sys.exit(0)

	return serial


def serialToCamera(serial: int):
	# Given camera's serial number, return the camera name
	if serial == rgbSerial[0]:
		name = 'r'
	elif serial == rgbSerial[1]:
		name = 'g'
	elif serial == rgbSerial[2]:
		name = 'b'
	else:
		Arena_Helper.safe_print('This should not happen. Quitting')
		sys.exit(0)

	return name
		
		
def findCamInDetectedDeviceList (camSrl, detectedDeviceList):
	'''
	Search for camera with serial number camSrl in the list of detected
	devices. Note that np.where returns a tuple, hence the [0] at end.
	'''

	devNum = np.where(detectedDeviceList == camSrl)[0]

	# A couple of sanity checks
	if len(devNum) == 0:
		Arena_Helper.safe_print('Specified camera not detected. Quitting...')
		sys.exit(0)
	if len(devNum)  > 1:
		Arena_Helper.safe_print('Multiple cameras with same serial. Quitting...')
		sys.exit(0)

	return devNum[0]


def getArgs(argv=None):
	descr='Take an image with the PHX050S camera, given \
		exposure time in seconds, offset in ADUs, and the   \
		gain in dB. \
		For example "python %(prog)s -i input.csv" uses the input.csv\
		file to take multiple photos with varying exposure, offset and gain levels, using the\
		cameras defined in the input.csv file'
	parser = argparse.ArgumentParser(description=descr)
	requiredNamed = parser.add_argument_group('required named arguments')
	requiredNamed.add_argument('-i', 
		type=str.lower, 
		required=False,
		default="input.csv",
		dest='CSV',
		help="Input file containing the camera names, exposure, offset, gain data")

	args = parser.parse_args(argv)

		# Some further sanity checks on inputs
	

	return args.CSV