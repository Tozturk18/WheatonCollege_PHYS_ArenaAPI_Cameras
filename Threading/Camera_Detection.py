import numpy as np
import argparse
import sys

import Arena_Helper
import Camera_Object

# Serial numbers of the cameras, in [r, g, b] order
rgbSerial = np.array([213301046, 211300110, 223200097])

def getSerial(devices):
	nDevFound = len(devices)
	detectedSerials = np.zeros(nDevFound, dtype=np.uint32)
	ii=0
	for device in devices:
		detectedSerials[ii] = device.nodemap.get_node("DeviceSerialNumber").value
		ii+=1

	return detectedSerials


def cameraToSerial(camName):
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


def serialToCamera(serial):
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
		gain in aaadB. \
		For example "python %(prog)s -c r -e 1.5 -o 200 -g 7" takes\
		a 1.5 second exposure with 200 ADU offset and 7 dB gain, using the\
		r camera.'
	parser = argparse.ArgumentParser(description=descr)
	requiredNamed = parser.add_argument_group('required named arguments')
	requiredNamed.add_argument('-c', 
		type=str.lower, 
		required=True,
		action = 'append', 
		nargs = '+',
		dest='cams',
		help="Camera name. Has to be either r/g/b/0/1/2.")
	'''requiredNamed.add_argument('-c2', 
		type=str.lower, 
		required=True, 
		dest='cam2',
		help="Camera name. Has to be either r/g/b/0/1/2.")'''
	requiredNamed.add_argument('-e', 
		type=float, 
		required=True, 
		dest='exp',
		help="Exposure time in seconds. A real number between [0.001 : 10]")
	requiredNamed.add_argument('-o', 
		type=int, 
		required=True, 
		dest='offset',
		help="Offset in ADU. An integer between [0 : 500]")
	requiredNamed.add_argument('-g', 
		type=float, 
		required=True, 
		dest='gain',
		help="Gain in dB. An integer between [0 : 24]")

	args = parser.parse_args(argv)

		# Some further sanity checks on inputs
	
	for cam in args.cams[0]:
		if cam != 'r' and cam != 'g' and cam != 'b' and cam != '0' and cam != '1' and cam != '2':
			Arena_Helper.safe_print('Camera has to be one of r/g/b/0/1/2.')
			Arena_Helper.safe_print(args.cams)
			sys.exit(0)

	
	if args.exp < 0.001 or args.exp > 10:
		Arena_Helper.safe_print('Exposure time has to be between 0.001 and 10 seconds.')
		sys.exit(0)
	if args.offset < 0 or args.offset > 500:
		Arena_Helper.safe_print('Offset has to be between 0 and 500 ADU.')
		sys.exit(0)
	if args.gain < 0 or args.gain > 24:
		Arena_Helper.safe_print('Gain has to be between 0 and 24 dB.')
		sys.exit(0)

	return args.cams[0], args.exp, args.offset, args.gain
