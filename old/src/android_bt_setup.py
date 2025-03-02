"""
import os
import time
import bluetooth

# Set up Bluetooth
os.system("sudo hciconfig hci0 piscan")
os.system("sudo sdptool add --channel=1 SP")
os.system("sudo rfcomm watch /dev/rfcomm0 1 &")

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port = 1
server_sock.bind(("", port))
server_sock.listen(1)

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

try:
    for i in range(10):
        client_sock.send("Hello")
        print("Sent 'Hello'")
        time.sleep(0.1)  # Delay for 100 ms
except Exception as e:
    print("Error: ", e)

client_sock.close()
server_sock.close()
"""

import os
import time
import bluetooth

# Set up Bluetooth
os.system("sudo hciconfig hci0 piscan")
os.system("sudo sdptool add --channel=1 SP")
os.system("sudo rfcomm watch /dev/rfcomm0 1 &")

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port = 1
success = False

while not success:
    try:
        server_sock.bind(("", port))
        server_sock.listen(1)
        print("Bound to port %d" % port)
        success = True
    except Exception as e:
        print("Could not bind to port %d: %s" % (port, e))
        port += 1  # Try a different port
        if port > 10:  # Just a limit for the example
            break

if success:
    print("Waiting for connection on RFCOMM channel %d" % port)
else:
    print("Failed to bind after trying multiple ports.")
