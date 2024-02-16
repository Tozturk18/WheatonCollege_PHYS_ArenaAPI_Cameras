import serial
import time
import sys

# Baud rate is 3M which means 333.33ns per letter
ser = serial.Serial('/dev/tty.usbserial-AB6ZS01F', 3000000, timeout=0.1)

while True:

  text = input("Please enter a text to send: ")
  
  ser.write(f"{text}\n".encode())

  if text == "exit":
    ser.close()
    sys.exit("\nThe program ended successfully as requested by the user\n")

  line = ser.readline()

  print(line)


  #time.sleep(1)