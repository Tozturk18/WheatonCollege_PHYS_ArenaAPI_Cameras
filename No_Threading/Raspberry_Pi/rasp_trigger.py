import serial
import RPi.GPIO as GPIO
import bme280
import smbus2
import time
import sys

port = 1
address = 0x77 # Adafruit BME280 address. Other BME280s may be different
bus = smbus2.SMBus(port)

bme280.load_calibration_params(bus,address)

# Set up the GPIO
GPIO.setmode(GPIO.BCM)  # Use physical pin numbering
GPIO.setup(5, GPIO.OUT, initial=GPIO.LOW)  # Set pin 5 to be an output pin and set initial value to low (off)

# Set up the serial port
ser = serial.Serial('/dev/ttyUSB0', 3000000, timeout=0.1)

try:

    while True:

        bme280_data = bme280.sample(bus,address)
        humidity  = bme280_data.humidity
        pressure  = bme280_data.pressure
        ambient_temperature = bme280_data.temperature

        line = '{"time": "' +  f"{time.time()}" + '", "temp": "' + str(ambient_temperature) + '", "pressure": "' + str(pressure*100) + '", "humid": "' + str(humidity) + '"}'
        
        if ser.in_waiting > 0:
            msg = ser.read()
            if msg == b'q':
                GPIO.cleanup()
                ser.close()
                sys.exit("\nThe program ended successfully as requested by the user\n")

            if msg:
                ser.write(line.encode())
                print(line)
                GPIO.output(5, GPIO.HIGH)  # Turn on pin 5
                time.sleep(0.001)   # Wait for 1 milliseconds
                GPIO.output(5, GPIO.LOW)  # Turn off pin 5
                time.sleep(0.001)   # Wait for 1 milliseconds


except KeyboardInterrupt:
    GPIO.cleanup()
    ser.close()