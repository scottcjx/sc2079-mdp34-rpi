from communication import SerialAPI
from protocol import CarMsgProtocol
from constants import CarDirection

class Car:
    def __init__(self):
        # Assume the car is available unless otherwise set.
        self._available = True

    def avail(self):
        return self._available

    def move(self, cmd, dist, spd):
        if self.avail():
            self._move(cmd, dist, spd)
        else:
            print("Car not available to move")

    def _move(self, cmd, dist, spd):
        cmd_msg = CarMsgProtocol.cmd2stm(cmd, dist, spd)
        SerialAPI.tx(cmd_msg)

    @staticmethod
    def hasValidDet():
        # Simulate a sensor check: returns True if a valid detection is present.
        # Replace with real sensor code.
        return False

    @staticmethod
    def hasBulleyeDet():
        # Simulate bullseye detection.
        return True

    @staticmethod
    def Stop():
        print("Car stopped")

