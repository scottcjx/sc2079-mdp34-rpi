from constants import CarDirection

class CarMsgProtocol:
    @classmethod
    def cmd2stm(cls, cmd, dist, spd):
        # Format a command to send to the STM32.
        # Example: "CMD:FORWARD:10:30"
        return f"CMD:{cmd.name}:{dist}:{spd}"


class CarProtocol:
    pass


class AndriodMsgProtocol:
    COMMAND_HEADER = "/"
    COMMAND_SPLIT1 = ","
    COMMAND_SPLIT2 = ";"

    @classmethod
    def rx2cmd(cls, msg):
        # Convert a received string (from the Android app via Bluetooth)
        # to a CarDirection. We assume the msg is something like "FORWARD".
        try:
            return CarDirection[msg.upper()]
        except KeyError:
            print("Invalid command received from Android.")
            return None
    
    def decode_cmd(cls, msg: str):
        msg_trim = msg.strip()
        if not msg_trim.beginswith(cls.COMMAND_HEADER):
            return None
        
        cmd = msg_trim.removeprefix(cls.COMMAND_HEADER)
        if cmd == "MOVE,F":
            pass
        elif cmd == "MOVE,B":
            pass
        elif cmd == "MOVE,L":
            pass
        elif cmd == "MOVE,R":
            pass
        elif cmd == "MODE,M":
            pass
        elif cmd == "MODE,T1":
            pass
        elif cmd == "MODE,T2":
            pass
        elif cmd == "BEGIN":
            pass

    def encode_cmd(cls, msg: str):
        pass

    def process_move_cmd():
        pass


from enum import Enum, auto
import ctypes


class MoveMode(Enum):
    stop = auto()
    velMode = auto()
    absPosMode = auto()
    relPosMode = auto()

class CarMoveProtocolStruct(ctypes.Structure):

    acked = 0
    completed = 0
    
    _fields_ = [
        ("msgId", ctypes.c_uint8),
        ("moveMode", ctypes.c_uint8),
        ("dir", ctypes.c_int8),
        ("steering_angle", ctypes.c_uint8),
        ("target_dist", ctypes.c_uint32)
    ]

    def __init__(self, 
                 msgId=0,
                 moveMode=0, 
                 target_dist=0,
                 speed=0,
                 steering_angle=0
                 ):
        self.msgId = msgId
        self.moveMode = moveMode
        self.target_dist = target_dist
        self.speed = speed
        self.steering_angle = steering_angle

    def serialized(self):
        self.serialized(self)

    def getCarMsg(self):
        # msgid:moveMode:steeringAngle:speed:[dist]

        self.carMsg = f"{self.msgId:.2d}"
        self.carMsg += f":{self.moveMode:.1d}"
        self.carMsg += f":{self.steering_angle:.3d}"
        self.carMsg += f":{self.speed:.3d}"

        if (self.moveMode == MoveMode.absPosMode) or (self.moveMode == MoveMode.velMode):
            self.carMsg += f":{self.target_dist}"

        return self.carMsg