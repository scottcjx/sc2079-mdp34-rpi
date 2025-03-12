import logging

import serial
from protocol import Protocol
from communication import AbstractSerialInterface
from enum import Enum, auto

import definitions


logger = logging.getLogger("Car")

class CarInterface(AbstractSerialInterface):
    msgDecodeFunction = lambda x : None
    sharedResources = None

    def setMsgDecoder(self, msgDecodeFunction):
        self.msgDecodeFunction = msgDecodeFunction
    
    def setSharedResources(self, sharedResources):
        self.sharedResources = sharedResources

    def rx_callback(self, msg):
        logger.debug(f"rx: {msg}")
        self.msgDecodeFunction(msg, self.sharedResources)

class CarMessageProtocol():
    sharedResources = None

    @classmethod
    def setSharedResources(cls, sharedResources):
        cls.sharedResources = sharedResources

    @classmethod
    def decodeRange(cls, msg: str, update_sharedResources: bool = True):
        pass

    @classmethod
    def decodeImu(cls, msg: str, update_sharedResources: bool = True):
        pass

    @classmethod
    def encodeMove(cls, dist: int = 0, spd: int = 0, steering_angle: int = 0):
        return 
    
    @classmethod
    def encodeMoveStd(cls, dir: str, dist: int = 0):
        if dir not in definitions.MOVES:
            return 
        
        if (dir == "F"):
            return f"SF010"
        elif (dir == "B"):
            return f"SB010"
        elif (dir == "L"):
            return f"TL090"
        elif (dir == "R"):
            return f"TR090"

    @classmethod
    def encodeStop():
        return "STOP"

class Car:
    def __init__(self, port):
        self.interface = CarInterface(port=port, baudrate=115200)
    
    def move(self, dist: int = 0, spd: int = 0, steering_angle: int = 0):
        if dist == 0 and spd == 0:
            self.interface.tx(
                CarMessageProtocol.encodeStop()
            )
        else:
            self.interface.tx(
                CarMessageProtocol.encodeMove(dist, spd, steering_angle)
            )
    
    def move_std(self, direction):
        dist = 10
        self.interface.tx(
            CarMessageProtocol.encodeMoveStd(dir=direction, dist=dist)
        )
        

    

# CarData = {
#     "currentInstruction": None,
#     "pastInstruction": [],
#     "imuReadings": None,
#     "rangingReadings": None,
#     "encoderRelReadings": None,
#     "encoderAbsReadings": None,
#     "carVectorPosition": None
# }
