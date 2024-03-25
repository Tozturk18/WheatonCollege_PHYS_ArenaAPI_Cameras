import Arena_Helper
import Camera_Object

import ctypes
import numpy as np
from astropy.io import fits
from astropy.time import Time
import serial
import time

import json

def save_image(camera, pdata, height, width, data):

	pdata_as16 = ctypes.cast(pdata, ctypes.POINTER(ctypes.c_ushort))

	nparray_reshaped = np.ctypeslib.as_array(pdata_as16, (height, width))

	#line = '{"time": "' +  f"{time.time()}" + '", "temp": "21.2", "pressure": "1", "humid": "20"}'

	#print(line)

	#data = json.loads(line)

	t = Time(data["time"], format='unix_tai')

	print(f'UTC: {t.isot}')
	print(f'MJD: {t.mjd}')

	mjd_now = t.mjd
	utc_now = t.isot

	save2fits(camera, nparray_reshaped, utc_now, mjd_now, data)

def save2fits(camera, imgarray, utc_isot, mjd, data, imgtyp='LIGHT'):
	
	'''
	The goal is to write the FITS as quickly as possible, so we supply
	both UTC and MJD of observation.
	'''
		
	print(f'Saving Image')
		
	#The chip name is figured out from dev_model
	if camera.dev_model == "PHX050S-P":
		chip = "IMX250MZR"
	elif camera.dev_model == "PHX050S1-P":
		chip = "IMX264MZR"
	else:
		print('No good camera. Quitting...')
		sys.exit(0)
		
	opfile = 'images/p' + str(mjd) + '_' + camera.name + '.fits'  # Create output FITS filename

	medianADU = np.median(imgarray)

		# Force FITS scaling to be bscale=1 and bzero=0
	hdu = fits.PrimaryHDU(data=imgarray, do_not_scale_image_data=True)
	hdu.scale(bzero=0)

		# Create the header
	hdr = hdu.header
	hdr['BSCALE']   = 1
	hdr['BZERO']    = 0
	hdr['DATE-OBS'] = (utc_isot,       'UTC of exposure start')
	hdr['MJD']      = (mjd,            'MJD of exposure start')
	hdr['EXPTIME']  = (camera.exposure,      'Exposure time [s]')
	hdr['OFFSET']   = (camera.offset,     'Black-level offset [ADU]')
	hdr['GAIN']     = (camera.gain,        'Gain [dB]')
	hdr['DET-TEMP'] = (camera.nodes['DeviceTemperature'].value,    'Detector temperature [C]')
	hdr['ENV-TEMP']	= (data["temp"],	'Environmental Temperature [C]'),
	hdr['ENV-PRES'] = (data["pressure"],	'Environmental Pressure [Pa]'),
	hdr['ENV-HUMD']	= (data["humidity"],	'Environmental Humidity [%]'),
	hdr['DEV-PWR']  = (camera.dev_power,      'Device power [Watts]')
	hdr['DET-SRL']  = (camera.dev_serial,     'Serial number of detector')
	hdr['DET-MDL']  = (camera.dev_model,      'Model of device')
	hdr['CHIPNAME'] = (chip,           'Sony CMOS chip name')
	hdr['PIX-SIZE'] = (3.45,           'Detector pixel size [microns]')
	hdr['BITDEPTH'] = (12,             'Detector bit depth per pixel')
	hdr['SWCREATE'] = ('ArenaSDK',     'Software used for acquisition')
	hdr['TELESCOP'] = ('RedCat 51',    'Telescope name')
	hdr['APERTURE'] = (51,             'Telescope diameter [mm]')
	hdr['FOCALLEN'] = (250,            'Telescope focal length [mm]')
	hdr['FILTER']   = (camera.name,    'Chroma R/G/B filter')
	hdr['IMGTYP']   = (imgtyp,         'LIGHT/DARK/BIAS/FLAT')
	hdr['MEDN_ADU'] = (medianADU,      'Median pixel brightness [ADU]')
	hdr['PLATESCL'] = (2.85,           'Plate scale [arcsec/pixel]')
	hdr['HFOV']     = (1.94,           'Horizontal FOV [degrees]')
	hdr['VFOV']     = (1.62,           'Vertical FOV [degrees]')
	hdr['SITE-LAT'] = ('00.00000',     'Latitude of site [degrees]')
	hdr['SITE-LON'] = ('00.00000',     'Longitude of site [degrees]')
	hdr['SITE-ALT'] = ('00.00000',     'Altitude of site [meters]')

	hdu.writeto(opfile, overwrite=False)
