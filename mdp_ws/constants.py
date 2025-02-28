from enum import Enum, auto

class TaskMode(Enum):
    MANUAL = 1
    TASK1 = 2
    TASK2 = 3
    BULLEYE = 4

class CarDirection(Enum):
    STOP = 0
    FORWARD = 1
    REVERSE = 2
    LEFT = 3
    RIGHT = 4

class CarCommandType(Enum):
    MOVE_CMD = CarDirection.STOP


class AndriodCommandType(Enum):
    MODE_CHANGE = 1
    MOVE_CMD = 2
