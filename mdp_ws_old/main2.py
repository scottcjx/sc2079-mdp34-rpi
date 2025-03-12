import time
# from car import Car
# from task_server import TaskServer

import constants
import sharedResources
from communication import AppInterface, CarInterface

from cv import CVModel, CvVisualizer
from mt_cv import MultiThreadedObjectTracker


def main():
    cvmodel = CVModel("mdp-det-v0.pt")
    cvmodel.set_model()
    cvvisualizer = CvVisualizer(camera_port="/dev/video0")
    mtcv = MultiThreadedObjectTracker(cvmodel, cvvisualizer)

    carInterface = CarInterface(port='/dev/ttyUSB0', baudrate=115200)
    appInterface = AppInterface(port='/dev/rfcomm0', baudrate=9600)

    def cls_det():
        det = []
        if cvmodel.results_tensor is None:
            return []
        for box in cvmodel.results_tensor:
            x_center, y_center, width, height, conf, cls = box
            det.append(int(cls))
        return det

    def rx_app_cmd(data: bytes):
        datastr = data.decode()
        print(datastr)
        if datastr == "/MOVE,F":
            carInterface.tx(b"SF005")
        elif datastr == "/MOVE,L":
            carInterface.tx(b"TL045")
        elif datastr == "/MOVE,R":
            carInterface.tx(b"TR045")
    
    def rx_car_status(data: bytes):
        datastr = data.decode()
        print(datastr)
        if datastr == 'A':
            sharedResources.movementstatus = 2
        
    
    sharedResources.movementstatus = 0
    # 0 no movement
    # 1 moving
    # 2 complete

    def bullseyeTask():
        det = cls_det()
        if 0 in det:
            sharedResources.fsm = 1
            print("det 0")
        elif 3 in det:
            sharedResources.fsm = 2
            print("det 3")
        else:
            sharedResources.fsm = 0

        # default move fwd
        if sharedResources.fsm == 0:
            if sharedResources.movementstatus == 0:
                carInterface.tx(b"SF005")
                sharedResources.movementstatus = 1
            elif sharedResources.movementstatus == 2:
                print("compl move")
                sharedResources.movementstatus = 0

        elif sharedResources.fsm == 1:

            if sharedResources.fsm2 == 0:
                if sharedResources.movementstatus == 0:
                    carInterface.tx(b"TL045")
                    sharedResources.movementstatus = 1
                if sharedResources.movementstatus == 2:
                    print("compl move")
                    sharedResources.fsm2 = 1
                    sharedResources.movementstatus = 0
                
            elif sharedResources.fsm2 == 1:
                if sharedResources.movementstatus == 0:
                    carInterface.tx(b"SF010")
                    sharedResources.movementstatus = 1
                if sharedResources.movementstatus == 2:
                    print("compl move")
                    sharedResources.fsm2 = 2
                    sharedResources.movementstatus = 0

            elif sharedResources.fsm2 == 2:
                if sharedResources.movementstatus == 0:
                    carInterface.tx(b"TR045")
                    sharedResources.movementstatus = 1
                if sharedResources.movementstatus == 2:
                    print("compl move")
                    sharedResources.fsm2 = 0
                    sharedResources.movementstatus = 0
            sharedResources.fsm = 0

    appInterface.set_rx_callback(rx_app_cmd)
    carInterface.set_rx_callback(rx_car_status)

    def setup():
        # appInterface.setup_bluetooth()

        mtcv.set_flags(read_stream=True, inference=True, show_raw_stream=False, show_labeled_stream=False)
        mtcv.start()

    def loop():
        # if not appInterface.is_connected:
        #     appInterface.connect()

        if not carInterface.is_connected:
            carInterface.connect()
        
        sharedResources.mtcv_detections = mtcv.cvmodel.inference_locations
        bullseyeTask()

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
        # appInterface.disconnect()
        mtcv.stop()

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
