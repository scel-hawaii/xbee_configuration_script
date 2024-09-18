import serial
import time

def send_at_command(ser, command, parameter=None):
    # Enter command mode
    ser.write(b'+++')
    time.sleep(1)  # Wait for the module to enter command mode
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
    time.sleep(1)
    response = ser.read(ser.in_waiting).decode()
    print(f"Sent command '{full_command.strip()}'. Response: '{response.strip()}'")

    # Exit command mode
    ser.write(b'ATCN\r')
    time.sleep(1)
    ser.read(ser.in_waiting)  # Clear buffer
    print("Exited command mode.")

    return response.strip()

def main():
    ser = serial.Serial('COM8', 9600, timeout=2)
    time.sleep(1)
    print(f"Using serial port: {ser.name}")

    # Read current PAN ID
    pan_id = send_at_command(ser, 'ATID')
    print(f"Current PAN ID: {pan_id}")

    # Set PAN ID to 0x1234
    send_at_command(ser, 'ATID', '12345')
    print("Set PAN ID to 0x12345.")

    # Write settings to non-volatile memory
    send_at_command(ser, 'ATWR')
    print("Settings written to non-volatile memory.")

    ser.close()

if __name__ == "__main__":
    main()
