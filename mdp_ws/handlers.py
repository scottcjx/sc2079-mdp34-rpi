from communication import BluetoothAPI
from protocol import AndriodMsgProtocol
from constants import CarDirection
from car import Car

class ManualHandler:
    def __init__(self, car: Car):
        self.car = car

    def handle(self):
        if BluetoothAPI.new_message():
            rx_msg = BluetoothAPI.rx()
            cmd = AndriodMsgProtocol.rx2cmd(rx_msg)
            if cmd is not None:
                # Execute movement: for example, move 10mm @ 30mm/s.
                self.car.move(cmd, 10, 30)
            else:
                print("Received invalid command.")
        else:
            print("No new Bluetooth message.")

class BulleyeHandler:
    def __init__(self, car: Car):
        self.car = car
        self.fsm = 0

    def handle(self):
        if self.car.hasValidDet():
            self.car.Stop()
            self.fsm = 3
        elif self.fsm == 0:
            # Move forward slightly.
            self.car.move(CarDirection.FORWARD, 10, 30)
            if self.car.hasBulleyeDet():
                self.fsm = 1
        elif self.fsm == 1:
            # Once detected, move away.
            self.car.move(CarDirection.LEFT, 50, 30)
            self.car.move(CarDirection.FORWARD, 100, 30)
            self.car.move(CarDirection.RIGHT, 50, 30)
            self.fsm = 0
        elif self.fsm == 3:
            if not self.car.hasValidDet():
                self.fsm = 0
