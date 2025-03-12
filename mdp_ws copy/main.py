from car import Car
from andriodapp import AndriodApp
from taskserver import TaskServer
from sharedResources import SharedRsc, sharedResources
import definitions
import time
import logging

logging.basicConfig(level=logging.DEBUG)

def main():
    try:
        car = Car(port='/dev/ttyUSB0')
        andriodApp = AndriodApp(port='/dev/rfcomm0')
        
        task_server = TaskServer(car, andriodApp, sharedResources)
        task_server.setup()
        
        if not andriodApp.interface.is_connected:
            andriodApp.interface.connect()

        if not car.interface.is_connected:
            car.interface.connect()

        while 1:
            task_server.loop()
            pass
        
    except KeyboardInterrupt:
        # task_server.stop()
        pass
    finally:
        andriodApp.interface.disconnect()
        car.interface.disconnect()
        pass

if __name__ == "__main__":
    main()

