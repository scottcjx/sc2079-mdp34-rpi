import logging
import time
import threading
from car import Car
from androidapp import AndroidApp
from taskserver import TaskServer
from sharedResources import sharedResources
import definitions

# Set logging level to INFO
logging.basicConfig(level=logging.INFO)

# Mapping of option numbers to command strings.
COMMAND_OPTIONS = {
    "1": "/*TASKMODE=MANUAL*/",
    "2": "/*TASKMODE=TASK1*/",
    "3": "/*TASKMODE=TASK2*/",
    "4": "/*TASKMODE=TASKB*/",
    "5": "/*TASKSTATUSREQ=START*/",
    "6": "/*TASKSTATUSREQ=PAUSE*/",
    "7": "/*TASKSTATUSREQ=STOP*/",
    "8": "/*MMOVE=F*/",
    "9": "/*MMOVE=B*/",
    "10": "/*MMOVE=L*/",
    "11": "/*MMOVE=R*/",
    "12": "/*MAP=[(0, 00, 00, 1),(1, 00, 00, 2)]*/"
}

def display_menu():
    menu = """
Choose a command to send (simulating Android sending to your app):
 1: Set TASKMODE to MANUAL
 2: Set TASKMODE to TASK1
 3: Set TASKMODE to TASK2
 4: Set TASKMODE to TASKB
 5: Set TASKSTATUSREQ to START
 6: Set TASKSTATUSREQ to PAUSE
 7: Set TASKSTATUSREQ to STOP
 8: Send MMOVE command: F
 9: Send MMOVE command: B
10: Send MMOVE command: L
11: Send MMOVE command: R
12: Send MAP update command
Type 'exit' to quit.
"""
    print(menu)

def terminal_interface(android_app: AndroidApp, stop_event: threading.Event):
    """
    Terminal-based input loop that simulates incoming messages from the Android app.
    Instead of sending commands out, it passes them to the Android interface's rx_callback,
    so the message is processed by the app and ultimately by the TaskServer.
    """
    logging.info("Terminal interface started. Use the menu options to send commands.")
    while not stop_event.is_set():
        try:
            display_menu()
            choice = input("Enter option number: ").strip()
            if choice.lower() == "exit":
                stop_event.set()
                break
            command = COMMAND_OPTIONS.get(choice)
            if command:
                logging.info(f"Simulating reception of command: {command}")
                # Simulate the Android interface receiving the command.
                android_app.interface.rx_callback(command)
            else:
                print("Invalid option. Please try again.")
        except Exception as e:
            logging.error("Error in terminal input: %s", e)
            stop_event.set()

def main():
    # Instantiate devices using the standardized APIs.
    car = Car(port='/dev/ttyUSB0')
    android_app = AndroidApp(port='/dev/rfcomm0')
    
    # Create and set up the TaskServer.
    task_server = TaskServer(car, android_app, sharedResources)
    task_server.setup()

    stop_event = threading.Event()
    terminal_thread = threading.Thread(target=terminal_interface, args=(android_app, stop_event), daemon=True)

    try:
        # Connect devices using their public methods.
        if not car.interface.is_connected:
            car.connect()
        if not android_app.interface.is_connected:
            android_app.connect()

        # Start the TaskServer loop in its own thread.
        task_server.start()

        # Start the terminal interface thread.
        terminal_thread.start()

        # Keep the main thread active until "exit" is entered.
        while not stop_event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received. Shutting down...")
        stop_event.set()

    finally:
        # Cleanly stop the TaskServer and disconnect devices.
        task_server.stop()
        car.disconnect()
        android_app.disconnect()
        logging.info("Shutdown complete.")

if __name__ == "__main__":
    main()
