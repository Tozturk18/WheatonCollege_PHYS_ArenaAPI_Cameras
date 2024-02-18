from arena_api.system import system
import threading
import time

def safe_print(*args, **kwargs):
	'''
	This function ensures resource access is locked to a single thread
	'''
	with threading.Lock():
		print(*args, **kwargs)

def update_create_devices():
	'''
	Waits for the user to connect a device before
		raising an exception if it fails
	'''
	tries: int = 0
	tries_max: int = 6
	sleep_time_secs: int = 10
	devices = None
	while tries < tries_max:  # Wait for device for 60 seconds
		devices = system.create_device()
		if not devices:
			print(
				f'Try {tries+1} of {tries_max}: waiting for {sleep_time_secs} '
				f'secs for a device to be connected!')
			for sec_count in range(sleep_time_secs):
				time.sleep(1)
				print(f'{sec_count + 1 } seconds passed ',
					'.' * sec_count, end='\r')
			tries += 1
		else:
			return devices
	else:
		raise Exception(f'No device found! Please connect a device and run '
						f'the example again.')
