from car import Car
from andriodapp import AndriodApp
from taskserver import TaskServer
from sharedResources import SharedRsc, sharedResources
import definitions


def main():
    try:
        car = Car(port='/dev/ttyUSB0')
        andriodApp = AndriodApp(port='/dev/rfcomm0')
        
        task_server = TaskServer(car, andriodApp)
        task_server.setup()

        task_server.start()
    except KeyboardInterrupt:
        pass
    finally:
        task_server.stop()

if __name__ == "__main__":
    main()

