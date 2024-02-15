import serial

def trigger_camera():

    # Baud rate is 3M which means 333.33ns per letter
    ser = serial.Serial('/dev/ttyUSB0', 3000000, timeout=0.1)

    ser.write('\n')

    line = ser.readline()

    return line