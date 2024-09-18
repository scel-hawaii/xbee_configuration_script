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
    print("Sent frame:", frame.hex())

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

    print("Received response frame:", frame_data.hex())
    return frame_data

def read_ap_parameter(ser):
    # Send ATAP command to read API mode setting
    response = send_api_command(ser, 'AP')
    if response:
        # Extract the parameter value from the response
        # Frame data format: Frame Type (1 byte), Frame ID (1 byte), AT Command (2 bytes), Status (1 byte), Parameter Value (variable)
        frame_type = response[0]
        frame_id = response[1]
        at_command = response[2:4].decode('ascii')
        status = response[4]
        parameter_value = response[5:-1]  # Exclude checksum

        if status == 0x00:
            # Success
            ap_value = parameter_value[0]
            print(f"Current API Mode (AP) Value: {ap_value}")
            return ap_value
        else:
            print(f"Failed to read AP parameter. Status: {status}")
            return None
    else:
        print("Failed to read API mode.")
        return None

def main():
    ser = serial.Serial('COM8', 9600, timeout=2)
    time.sleep(1)
    print(f"Using serial port: {ser.name}")

    # Read current AP parameter
    ap_value = read_ap_parameter(ser)
    if ap_value is None:
        ser.close()
        return

    # Proceed with configuration using API frames
    print("Configuring module via API commands...")

    # Set PAN ID to 0x1234 via API command
    pan_id = 0x1234
    parameter = pan_id.to_bytes(2, 'big')  # 2 bytes, big-endian
    response = send_api_command(ser, 'ID', parameter)
    if response:
        # Check the status in the response
        status = response[4]
        if status == 0x00:
            print(f"Successfully set PAN ID to {hex(pan_id)}.")
        else:
            print(f"Failed to set PAN ID. Status: {status}")
            ser.close()
            return
    else:
        print("Failed to set PAN ID.")
        ser.close()
        return

    # Write settings to non-volatile memory
    response = send_api_command(ser, 'WR')
    if response:
        status = response[4]
        if status == 0x00:
            print("Settings written to non-volatile memory.")
        else:
            print(f"Failed to write settings. Status: {status}")
            ser.close()
            return
    else:
        print("Failed to write settings.")
        ser.close()
        return

    ser.close()

if __name__ == "__main__":
    main()
