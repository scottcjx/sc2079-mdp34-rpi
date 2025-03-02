import time

def handle_command(cmd):
    """
    Handle the incoming command string from the Bluetooth connection.
    Replace these print statements with the actual logic for your robot.
    """
    if cmd == "/MOVE,F":
        print("Moving Forward!")
        # Add your forward-movement logic here
    elif cmd == "/MOVE,D":
        print("Moving Down!")
        # Add your downward-movement logic here
    elif cmd == "/MOVE,L":
        print("Moving Left!")
        # Add your left-movement logic here
    elif cmd == "/MOVE,R":
        print("Moving Right!")
        # Add your right-movement logic here
    else:
        # Handle any other arbitrary string from the Android side
        print(f"Received: {cmd}")

def main():
    # Continuously read from /dev/rfcomm0
    try:
        with open('/dev/rfcomm0', 'r') as rfcomm:
            while True:
                # Read one line of input
                line = rfcomm.readline()

                # If line is empty, it might mean no data or disconnected
                if not line:
                    time.sleep(0.1)  # Prevent busy waiting
                    continue

                # Strip newline characters or extra whitespace
                line = line.strip()

                # Pass the command to our handler
                handle_command(line)

    except FileNotFoundError:
        print("Error: /dev/rfcomm0 not found. Is your Bluetooth device connected?")
    except KeyboardInterrupt:
        print("Exiting script (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
