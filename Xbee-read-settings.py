import serial
import time

def send_command(ser, command):
    ser.write(command.encode())
    ser.write(b'\r')

def read_response(ser):
    response = b''
    while True:
        char = ser.read()
        if char == b'\r':
            break
        response += char
    return response.decode()

def enter_command_mode(ser):
    ser.write(b'+++')
    time.sleep(1)  # Wait for command mode
    read_response(ser)  # Flush the response

def exit_command_mode(ser):
    send_command(ser, 'ATCN')
    time.sleep(1)  # Wait for exit command mode
    read_response(ser)  # Flush the response

def read_setting(ser, parameter):
    enter_command_mode(ser)
    send_command(ser, 'AT' + parameter)
    response = read_response(ser)
    exit_command_mode(ser)
    return response

def main():
    # Open serial port, change the port and baud rate according to your setup
    ser = serial.Serial('COM6', 9600, timeout=1)
    time.sleep(2)  # Wait for the serial connection to be established

    if ser.is_open:
        print("Serial port opened successfully.")
    else:
        print("Failed to open serial port.")
        return

    try:
        # Read various settings from the XBee module
        firmware_version = read_setting(ser, 'VR')
        hardware_version = read_setting(ser, 'HV')
        serial_number = read_setting(ser, 'SH')
        pan_id = read_setting(ser, 'ID')
        node_identifier = read_setting(ser, 'NI')

        # Print the settings
        print("Firmware Version:", firmware_version)
        print("Hardware Version:", hardware_version)
        print("Serial Number:", serial_number)
        print("PAN ID:", pan_id)
        print("Node Identifier:", node_identifier)

    except Exception as e:
        print("Error:", e)

    # Close serial port
    ser.close()

if __name__ == "__main__":
    main()