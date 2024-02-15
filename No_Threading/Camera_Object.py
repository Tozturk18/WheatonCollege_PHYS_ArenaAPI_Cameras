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
        self.exposure = exposure
        self.offset = offset
        self.gain = gain
        self.buffers = buffers
        
        # Pull the nodemaps from device
        self.nodemap = self.device.nodemap
        self.tl_stream_nodemap = self.device.tl_stream_nodemap

        self.get_nodes()
        

    def get_nodes(self):
        # Stores the nodes needed for setting up the camera settings
        self.nodes = self.nodemap.get_node(
                            ['TriggerSelector', 'TriggerMode','TriggerSource', 
                            'TriggerActivation','Width', 'Height', 
                            'PixelFormat', 'AcquisitionMode', 'AcquisitionStartMode', 'PtpEnable', 'PtpStatus','DeviceTemperature', 
                            'AcquisitionFrameRate', 'ExposureTime', 'BlackLevelRaw', 
                            'Gain', 'DeviceSerialNumber','DeviceModelName','DevicePower','GevSCPD','GevSCFTD']
                            )

        # Set some initial values
        self.nodes['Width'].value = self.nodes['Width'].max
        self.nodes['Height'].value = self.nodes['Height'].max
        self.nodes['PixelFormat'].value = 'Mono12'

        self.store_initials()

    def store_initials(self):
        # Save initial values to restore them before ending the program
        self.initial_values  = [
            self.nodes['TriggerSelector'].value, self.nodes['TriggerMode'].value,
            self.nodes['TriggerSource'].value, self.nodes['TriggerActivation'].value,
            self.nodes['AcquisitionMode'].value, self.tl_stream_nodemap['StreamBufferHandlingMode'].value,
            self.tl_stream_nodemap['StreamAutoNegotiatePacketSize'].value, self.tl_stream_nodemap['StreamPacketResendEnable'].value,
            self.nodes['GevSCPD'].value, self.nodes['GevSCFTD'].value,
            self.nodes['AcquisitionStartMode'].value, self.nodes['PtpEnable'].value
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
        self.nodes['GevSCFTD'].value = self.initial_values[9]
        self.nodes['AcquisitionStartMode'].value = self.initial_values[10]
        self.nodes['PtpEnable'].value = self.initial_values[11]
        
        Arena_Helper.safe_print("\nRestored back to initials",
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
        	"\nPtpEnable: ", self.nodes['PtpEnable'].value)

    def _change_config(self, exposure, offset, gain):

        self.device.stop_stream()
        
        self.exposure = exposure
        self.offset = offset
        self.gain = gain
        
        # Make sure the framerate is such that an exposure can be taken
        # between two succesive frames
        framerate = 0.90 / self.exposure

        # However don't go beyond the camera's maximum frame rate
        maxframerate = self.nodes['AcquisitionFrameRate'].max
        if framerate > maxframerate:
            framerate = maxframerate

        # Set camera's framerate
        self.nodes['AcquisitionFrameRate'].value = framerate
        
        # Turn off auto exposure [possibilities are Continuous or Off]
        # And check to make sure we can change the exposure time
        if self.nodemap['ExposureAuto'].value == 'Continuous':
            self.nodemap['ExposureAuto'].value = 'Off'
        if self.nodemap['ExposureTime'] is None:
            raise Exception("ExposureTime node not found")
        if self.nodemap['ExposureTime'].is_writable is False:
            raise Exception("ExposureTime node is not writable")
        
        ''' 1/frameaRate * 0.8 = exposure'''

        # Set the exposure time (internally in microseconds)
        self.nodes['ExposureTime'].value = self.exposure * 1e6

        # Set the black level (offset) in ADU
        self.nodes['BlackLevelRaw'].value = self.offset

        # Turn off automatic gain [possibilities are Continuous or Off]
        if self.nodemap['GainAuto'].value == 'Continuous':
            self.nodemap['GainAuto'].value = 'Off'
        
        # Change Gain levels
        self.nodes['Gain'].value = self.gain
        
        Arena_Helper.safe_print(
            '\nCamera: ', self.name,
            '\nImages:', self.nodes['Width'].value, 'x',  self.nodes['Height'].value, self.nodes['PixelFormat'].value,
            '\nTemperature (C)\t=', self.nodes['DeviceTemperature'].value, 
            '\nFramerate (Hz) \t=', self.nodes['AcquisitionFrameRate'].value, 
            '\nExptime (s)    \t=', self.exposure,
            '\nOffset (ADU)   \t=', self.offset,
            '\nGain (dB)      \t=', self.gain)
        
        self.device.start_stream(self.buffers)


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

        # Enable frame rate change, if needed
        if camera.nodemap['AcquisitionFrameRateEnable'].value is False:
            camera.nodemap['AcquisitionFrameRateEnable'].value = True
            
        '''
        # Make sure the framerate is such that an exposure can be taken
        # between two succesive frames
        framerate = 0.90 / camera.exposure

        # However don't go beyond the camera's maximum frame rate
        maxframerate = camera.nodes['AcquisitionFrameRate'].max
        if framerate > maxframerate:
            framerate = maxframerate

        # Set camera's framerate
        camera.nodes['AcquisitionFrameRate'].value = framerate

        # Turn off auto exposure [possibilities are Continuous or Off]
        # And check to make sure we can change the exposure time
        if camera.nodemap['ExposureAuto'].value == 'Continuous':
            camera.nodemap['ExposureAuto'].value = 'Off'
        if camera.nodemap['ExposureTime'] is None:
            raise Exception("ExposureTime node not found")
        if camera.nodemap['ExposureTime'].is_writable is False:
            raise Exception("ExposureTime node is not writable")

        # Set the exposure time (internally in microseconds)
        camera.nodes['ExposureTime'].value = camera.exposure * 1e6

        # Set the black level (offset) in ADU
        camera.nodes['BlackLevelRaw'].value = camera.offset

        # Turn off automatic gain [possibilities are Continuous or Off]
        if camera.nodemap['GainAuto'].value == 'Continuous':
            camera.nodemap['GainAuto'].value = 'Off'
        
        # Change Gain levels
        camera.nodes['Gain'].value = camera.gain
        '''
        
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
        
        '''
        # Double check and print exposure essentials
        exptime = camera.nodes['ExposureTime'].value/1e6
        offset  = camera.nodes['BlackLevelRaw'].value
        gain    = camera.nodes['Gain'].value
        devSrl  = camera.nodes['DeviceSerialNumber'].value
        devModel= camera.nodes['DeviceModelName'].value
        devPower= camera.nodes['DevicePower'].value
            
        Arena_Helper.safe_print(
            'Camera: ', camera.name,
            '\nImages:', camera.nodes['Width'].value, 'x',  camera.nodes['Height'].value, camera.nodes['PixelFormat'].value,
            '\nTemperature (C)\t=', camera.nodes['DeviceTemperature'].value, 
            '\nFramerate (Hz) \t=', camera.nodes['AcquisitionFrameRate'].value, 
            '\nExptime (s)    \t=', exptime,
            '\nOffset (ADU)   \t=', offset,
            '\nGain (dB)      \t=', gain)
            '''
        
        total		= len(cameras)
        packetSize	= 9014		# Bytes
        devLink		= 125000000	# 1 Gbps
        a_buffer	= 0.1093	# 10.93%
        delay = packetSize * (10**9)/devLink
        
        delay = delay + (delay * a_buffer)
        
        Arena_Helper.safe_print('GevSCPD: ', int( math.ceil( delay * (total - 1) / 10000) ) * 10000 )
        #Arena_Helper.safe_print('GevSCFTD: ', int( math.ceil( delay * cam / 10000 ) ) * 10000 )
        
        camera.nodes['GevSCPD'].value = int( math.ceil( delay * (total - 1) / 10000) * 10000 )
        #camera.nodes['GevSCFTD'].value = int( math.ceil( delay * cam / 10000 ) * 10000 )
        
        Arena_Helper.safe_print('GevSCPD2: ', camera.nodes['GevSCPD'].value)
        #Arena_Helper.safe_print('GevSCFTD2: ', camera.nodes['GevSCFTD'].value)
        
        devSrl  = camera.nodes['DeviceSerialNumber'].value
        devModel= camera.nodes['DeviceModelName'].value
        devPower= camera.nodes['DevicePower'].value

        # store camera values
        camera.dev_serial =  devSrl
        camera.dev_power = devPower
        camera.dev_model = devModel

    '''
        Wait until the PTP connection is established
        Start Sync Check
    '''

    masterfound = False
    restartSyncCheck = True

    ptpStatus = ""

    while (restartSyncCheck and not masterfound):

        restartSyncCheck = False

        for camera in cameras:

            ptpStatus = camera.nodes['PtpStatus'].value

            if (ptpStatus == "Master"):

                if (masterfound):
                    # There are still multiple masters, continue negotiating
                    restartSyncCheck = True

                masterfound = True

            elif (ptpStatus != "Slave"):
                # There are still undifined camers
                restartSyncCheck = True

    Arena_Helper.safe_print("PTP sync check done!")

    for camera in cameras:
        # Start stream with 25 buffers
        camera.device.start_stream(camera.buffers)

        trigger_armed = bool(camera.nodemap['TriggerArmed'].value)
        
        while trigger_armed is False:
            trigger_armed = bool(camera.nodemap['TriggerArmed'].value)

def change_config(cameras, data, index):

    cams        = data['cams'][index]
    exposure    = float(data['exp'][index])
    offset      = int(data['off'][index])
    gain        = float(data['gain'][index])

    gen = (camera for camera in cameras if camera.name in cams)

    for camera in gen:
        camera._change_config(exposure,offset,gain)
