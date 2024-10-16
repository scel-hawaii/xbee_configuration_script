import serial
from digi.xbee.devices import XBeeDevice

# XBee serial port configuration
PORT = "COM8"  # Change this to your XBee's serial port
BAUD_RATE = 9600  # Change if your XBee uses a different baud rate

def get_user_input(prompt, current_value):
    user_input = input(f"{prompt} (current: {current_value}, 'skip' to keep current): ").strip()
    return None if user_input.lower() == 'skip' else user_input

def set_parameter(xbee, param_name, value, formatter=None):
    if value is not None:
        if formatter:
            try:
                value = formatter(value)
            except ValueError as e:
                print(f"Error: {e}")
                return
        xbee.set_parameter(param_name, value)
        print(f"{param_name} set to: {value}")
    else:
        print(f"{param_name} unchanged")

def pan_id_formatter(value):
    try:
        pan_id = int(value, 16)
        # Assuming the PAN ID can be up to 8 bytes (64 bits) long
        if pan_id < 0 or pan_id > 0xFFFFFFFFFFFFFFFF:
            raise ValueError(f"PAN ID must be between 0x0000 and 0xFFFFFFFFFFFFFFFF. Got: {value}")
        # Convert to bytes, trim leading zeros, but ensure at least one byte
        return pan_id.to_bytes((pan_id.bit_length() + 7) // 8, byteorder='big') or b'\x00'
    except ValueError:
        raise ValueError(f"Invalid PAN ID format. Please enter a valid hexadecimal value. Got: {value}")

# Create and open the XBee device
xbee = XBeeDevice(PORT, BAUD_RATE)
xbee.open()

try:
    # Read current parameters
    current_pan_id = xbee.get_parameter("ID")
    current_dh = xbee.get_parameter("DH")
    current_dl = xbee.get_parameter("DL")
    current_sh = xbee.get_parameter("SH")
    current_sl = xbee.get_parameter("SL")

    # Convert current PAN ID from bytes to hex string
    current_pan_id_hex = current_pan_id.hex()

    # Get user input for each parameter
    new_pan_id = get_user_input("Enter new PAN ID (in hex)", current_pan_id_hex)
    new_dh = get_user_input("Enter new DH (Destination Address High)", current_dh.hex())
    new_dl = get_user_input("Enter new DL (Destination Address Low)", current_dl.hex())

    # Set parameters
    set_parameter(xbee, "ID", new_pan_id, pan_id_formatter)
    set_parameter(xbee, "DH", new_dh, bytes.fromhex)
    set_parameter(xbee, "DL", new_dl, bytes.fromhex)

    # Print current SH and SL (these are typically read-only)
    print(f"SH (Serial Number High): {current_sh.hex()}")
    print(f"SL (Serial Number Low): {current_sl.hex()}")

    print("Parameter update complete.")

finally:
    # Close the device
    if xbee is not None and xbee.is_open():
        xbee.close()
