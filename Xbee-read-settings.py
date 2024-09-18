import serial
import time

def send_api_command(ser, at_command, parameter=None):
    # Start constructing the frame
    frame = bytearray()
    frame.append(0x7E)  # Start delimiter

    # Frame Data
    frame_data = bytearray()
    frame_data.append(0x08)  # Frame Type: AT Command
    frame_data.append(0x01)  # Frame ID
    frame_data.extend(at_command.encode('ascii'))  # AT Command
    if parameter is not None:
        frame_data.extend(parameter)

    # Length
    length = len(frame_data)
    frame.append((length >> 8) & 0xFF)  # MSB
    frame.append(length & 0xFF)         # LSB

    # Add frame data
    frame.extend(frame_data)

    # Calculate checksum
    checksum = 0xFF - (sum(frame_data) & 0xFF)
    frame.append(checksum)

    # Send frame
    ser.write(frame)
    print(f"Sent frame for command {at_command}: {frame.hex()}")

    # Read response
    response = read_api_response(ser)
    return response

def read_api_response(ser):
    # Read the start delimiter
    start_delimiter = ser.read(1)
    if start_delimiter != b'\x7E':
        print("Invalid start delimiter:", start_delimiter)
        return None

    # Read length
    length_bytes = ser.read(2)
    if len(length_bytes) < 2:
        print("Failed to read length bytes.")
        return None
    length = (length_bytes[0] << 8) | length_bytes[1]

    # Read frame data and checksum
    frame_data = ser.read(length + 1)
    if len(frame_data) < length + 1:
        print("Incomplete frame data.")
        return None

    # Extract frame data and checksum
    frame = frame_data[:-1]
    checksum = frame_data[-1]

    # Verify checksum
    calculated_checksum = 0xFF - (sum(frame) & 0xFF)
    if checksum != calculated_checksum:
        print("Checksum mismatch.")
        return None

    print(f"Received response frame: {frame_data.hex()}")
    return frame_data

def read_parameter(ser, at_command):
    response = send_api_command(ser, at_command)
    if response:
        # Extract the parameter value from the response
        # Frame data format: Frame Type (1 byte), Frame ID (1 byte), AT Command (2 bytes), Status (1 byte), Parameter Value (variable)
        frame_type = response[0]
        frame_id = response[1]
        at_cmd = response[2:4].decode('ascii')
        status = response[4]
        parameter_value = response[5:-1]  # Exclude checksum

        if status == 0x00:
            # Success
            print(f"{at_command} Response: {parameter_value.hex()}")

            # Convert parameter value to appropriate format
            if at_command in ['VR', 'HV', 'ID', 'SH', 'SL']:
                value = int.from_bytes(parameter_value, 'big')
                return value
            elif at_command == 'NI':
                value = parameter_value.decode('ascii')
                return value
            else:
                return parameter_value
        else:
            print(f"Failed to read {at_command}. Status: {status}")
            return None
    else:
        print(f"Failed to read {at_command}.")
        return None

def main():
    ser = serial.Serial('COM8', 9600, timeout=2)
    time.sleep(1)
    print(f"Using serial port: {ser.name}")

    # Read various settings from the XBee module
    firmware_version = read_parameter(ser, 'VR')
    hardware_version = read_parameter(ser, 'HV')
    serial_number_high = read_parameter(ser, 'SH')
    serial_number_low = read_parameter(ser, 'SL')
    pan_id = read_parameter(ser, 'ID')
    node_identifier = read_parameter(ser, 'NI')

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
