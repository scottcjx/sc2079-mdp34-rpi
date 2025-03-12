import time
# from car import Car
# from task_server import TaskServer

import constants
from communication import AppInterface, CarInterface

from cv import CVModel, CvVisualizer
from mt_cv import MultiThreadedObjectTracker


def main():
    carInterface = CarInterface(port='/dev/ttyUSB0', baudrate=115200)
    appInterface = AppInterface(port='/dev/rfcomm0', baudrate=9600)

    def rx_app_cmd(data: bytes):
        print(data.decode())
        if data.decode() == "/MOVE,F":
            carInterface.tx(b"SF005")
        elif data.decode() == "/MOVE,L":
            carInterface.tx(b"LF045")
        elif data.decode() == "/MOVE,R":
            carInterface.tx(b"RF045")

    appInterface.set_rx_callback(rx_app_cmd)

    cvmodel = CVModel("mdp-det-v0.pt")
    cvmodel.set_model()
    cvvisualizer = CvVisualizer(camera_port="/dev/video0")
    mtcv = MultiThreadedObjectTracker(cvmodel, cvvisualizer)

    def setup():
        appInterface.setup_bluetooth()

        mtcv.set_flags(read_stream=True, inference=True, show_raw_stream=False, show_labeled_stream=False)
        # mtcv.start()

    def loop():
        if not appInterface.is_connected:
            appInterface.connect()

        if not carInterface.is_connected:
            carInterface.connect()

        # send heartbeat
        # appInterface.tx(b'-')
        # carInterface.tx(b'SF100')
        # print(mtcv.cvmodel.inference_locations)

        # send buffer app
        # send buffer bot
        # update algo pathfinding
        # update image recog

    def end():
        carInterface.disconnect()
        appInterface.disconnect()

        # mtcv.stop()

    setup()
    time.sleep(0.1)
    try:
        while True:
            loop()
            time.sleep(1)
    except Exception as e:
        print(f"[main] {e}")
    finally:
        end()

if __name__ == '__main__':
    main()
