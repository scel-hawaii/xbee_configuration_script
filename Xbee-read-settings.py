import serial
from digi.xbee.devices import XBeeDevice

# XBee serial port configuration
PORT = "COM8"  # Change this to your XBee's serial port (e.g., "COM3" for Windows)
BAUD_RATE = 9600  # Change if your XBee uses a different baud rate

# Create and open the XBee device
xbee = XBeeDevice(PORT, BAUD_RATE)
xbee.open()

try:
    # Read the parameters
    pan_id = xbee.get_parameter("ID")
    dh = xbee.get_parameter("DH")
    dl = xbee.get_parameter("DL")
    sh = xbee.get_parameter("SH")
    sl = xbee.get_parameter("SL")

    # Convert PAN ID from bytes to integer to remove leading zeros
    pan_id_int = int.from_bytes(pan_id, byteorder='big')
    pan_id_hex = f"{pan_id_int:X}"  # Format as uppercase hexadecimal without leading zeros

    # Alternatively, for lowercase hexadecimal:
    # pan_id_hex = f"{pan_id_int:x}"

    # Print the results
    print(f"PAN ID: {pan_id_hex}")
    print(f"DH (Destination Address High): {dh.hex()}")
    print(f"DL (Destination Address Low): {dl.hex()}")
    print(f"SH (Serial Number High): {sh.hex()}")
    print(f"SL (Serial Number Low): {sl.hex()}")

    # If you want to see the PAN ID as a decimal number, uncomment the next line
    # print(f"PAN ID (decimal): {pan_id_int}")

finally:
    # Close the device
    if xbee is not None and xbee.is_open():
        xbee.close()
