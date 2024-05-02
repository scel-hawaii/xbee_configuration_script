
import serial
ser = serial.Serial('COM6', 9600)           # open serial port, 
print(ser.name)                             # check which port was really used
ser.write(b'+++')    
reply =  ser.read_until(b'\r')
print(reply)
 
# Reset the xbee to factory defaults:
ser.write(b'ATRE\r')
reply = ser.read_until(b'\r')
print(reply)
 
 
# pan_id = input("Enter PAN ID: ")
response = ser.read_until("ATID" + '1234' + "\r")
print("PAN ID set:", response)

# Exit command mode
ser.write(b'ATCN\r')
reply =  ser.read_until(b'\r')
print(reply)
 
ser.close()