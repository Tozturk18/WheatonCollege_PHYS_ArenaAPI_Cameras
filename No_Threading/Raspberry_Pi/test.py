import serial
import sys

# Baud rate is 3M which means 333.33ns per letter
ser = serial.Serial('/dev/tty.usbserial-AB6ZS01F', 3000000, timeout=0.1)

while True:

  text = input("Please enter a text to send: ")
  
  ser.write(text.encode())

  if text == "q":
    ser.close()
    sys.exit("\nThe program ended successfully as requested by the user\n")

  line = ser.readline().decode()

  print(line)