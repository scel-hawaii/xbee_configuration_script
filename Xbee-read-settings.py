import serial
import time

def send_at_command(ser, command, parameter=None):
    # Ensure there's a guard time before sending '+++'
    ser.flushInput()
    ser.flushOutput()
    time.sleep(1)  # At least one second of silence

    # Enter command mode
    ser.write(b'+++')
    ser.flush()
    time.sleep(1)  # Wait for the module to enter command mode

    # Read response
    response = ser.read(ser.in_waiting).decode()
    if 'OK' not in response:
        print("Failed to enter command mode.")
        return None
    print("Entered command mode.")

    # Construct the command
    full_command = command
    if parameter is not None:
        full_command += str(parameter)
    full_command += '\r'

    # Send the command
    ser.write(full_command.encode())
    ser.flush()
    time.sleep(0.5)  # Short delay to wait for the response

    # Read the response
    response = ser.readline().decode().strip()
    print(f"Sent command '{full_command.strip()}'. Response: '{response}'")

    # Exit command mode
    ser.write(b'ATCN\r')
    ser.flush()
    time.sleep(0.5)
    ser.read(ser.in_waiting)  # Clear buffer
    print("Exited command mode.")

    return response

def read_parameter(ser, at_command):
    response = send_at_command(ser, at_command)
    if response:
        # Parse the response based on the command
        if at_command == 'ATNI':
            # Node Identifier is a string
            return response
        else:
            # Other parameters are hexadecimal numbers
            try:
                value = int(response, 16)
                return value
            except ValueError:
                print(f"Unable to parse response '{response}' as hexadecimal.")
                return None
    else:
        print(f"Failed to read {at_command}.")
        return None

def main():
    ser = serial.Serial('COM8', 9600, timeout=2)
    time.sleep(1)
    print(f"Using serial port: {ser.name}")

    # Read various settings from the XBee module
    firmware_version = read_parameter(ser, 'ATVR')
    hardware_version = read_parameter(ser, 'ATHV')
    serial_number_high = read_parameter(ser, 'ATSH')
    serial_number_low = read_parameter(ser, 'ATSL')
    pan_id = read_parameter(ser, 'ATID')
    node_identifier = read_parameter(ser, 'ATNI')

    # Print the settings
    if firmware_version is not None:
        print(f"Firmware Version: 0x{firmware_version:04X}")
    if hardware_version is not None:
        print(f"Hardware Version: 0x{hardware_version:04X}")
    if serial_number_high is not None:
        print(f"Serial Number High: 0x{serial_number_high:08X}")
    if serial_number_low is not None:
        print(f"Serial Number Low: 0x{serial_number_low:08X}")
    if pan_id is not None:
        print(f"PAN ID: 0x{pan_id:04X}")
    if node_identifier is not None:
        print(f"Node Identifier: {node_identifier}")

    ser.close()

if __name__ == "__main__":
    main()
