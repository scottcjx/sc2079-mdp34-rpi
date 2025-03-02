import os
import time

def main():
    # Send the message 10 times, once per second
    for i in range(10):
        os.system('echo "HELLOOO" > /dev/rfcomm0')
        print("Sent: HELLOOO")
        time.sleep(1)  # wait for 1 second

if __name__ == "__main__":
    main()

"""
import os
import time

def main():
    try:
        while True:
            # Send a message to the serial device at /dev/rfcomm0
            os.system('echo "HELLOOO" > /dev/rfcomm0')
            print("Sent: HELLOOO")
            time.sleep(1)  # Wait 1 second
    except KeyboardInterrupt:
        print("\nScript stopped by user.")

if __name__ == "__main__":
    main()

"""