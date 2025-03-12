import logging
import serial
import bluetooth
import os
from protocol import Protocol
from communication import AbstractSerialInterface
from queue import Queue
from sharedResources import SharedRsc, sharedResources

import definitions


logger = logging.getLogger("AndriodApp")

class AppMessageProtocol():
    sharedResources: SharedRsc

    @classmethod
    def initSharedResource(cls):
        logger.debug("[AppMessageProtocol]: initSharedResource")
        
        cls.sharedResources.set("TASK.MODE.REQ", Queue(1))
        cls.sharedResources.set("TASK.STATUS.REQ", Queue(1))
        cls.sharedResources.set("APP.MOVE.REQ", Queue(1))

    @classmethod
    def setSharedResources(cls, sharedResources):
        cls.sharedResources = sharedResources

    @classmethod
    def decodeMessage(cls, msg: str):
        stripped = msg.strip()
        iscmd = stripped.startswith("/*") and stripped.endswith("*/")
        if not iscmd:
            return
        cmdstr = stripped.removeprefix("/*").removesuffix("*/")
        cmdarr = cmdstr.split("=")
        iscmd = len(cmdarr) == 2
        if not iscmd: 
            return
        cmd, val = cmdarr

        cls.callCmd(cmd, val)

    @classmethod
    def processTaskmode(cls, val):
        if val not in definitions.MODES:
            return

        cls.sharedResources.get("TASK.MODE.REQ").put_nowait(val)

        logger.info("Taskmode {val}")

    @classmethod
    def processTaskStatus(cls, val):
        if val not in definitions.TASKSTATUSES:
            return

        cls.sharedResources.get("TASK.STATUS.REQ").put_nowait(val)
        logger.info("TaskStatus {val}")

    @classmethod
    def processMMove(cls, val):
        if val not in definitions.MOVES:
            return

        cls.sharedResources.get("APP.MOVE.REQ").put_nowait(val)
        logger.info("MMove {val}")

    @classmethod
    def processMap(cls, val):
        "/*MAP=[(0, 00, 00, 1),(1, 00, 00, 2)]*/"

        # need to note on the task server end. if there is a change to this, algo will break if the movement is already in process.
        # on app side, will have to note to reject the order from the app side

        if cls.sharedResources.get("TASK.STATUS") == "IN-PROGRESS" and cls.sharedResources.get("TASK.MODE").startswith("TASK"):
            # need to reject this command.
            # stop the current execution first
            return

        cls.sharedResources.set("MAP.NEW.FLAG", 1)
        cls.sharedResources.set("MAP.STR", val)

        logger.info("Map {val}")

    @classmethod
    def callCmd(cls, cmd, val):
        possibleCmds = {
            "TASKMODE": cls.processTaskmode, 
            "TASKSTATUSREQ": cls.processTaskStatus, 
            "MMOVE": cls.processMMove, 
            "MAP": cls.processMap
        }

        if cmd not in possibleCmds.keys():
            return

        return possibleCmds[cmd](val)


class AppInterface(AbstractSerialInterface):
    sharedResources: SharedRsc
    msgProtocolCls: AppMessageProtocol
    
    def setupProtocol(self):
        self.msgProtocolCls = AppMessageProtocol()
        self.msgProtocolCls.setSharedResources(self.sharedResources)
        self.msgProtocolCls.initSharedResource()
    
    def setSharedResources(self, sharedResources):
        self.sharedResources = sharedResources

    def rx_callback(self, msg):
        logger.debug(f"rx: {msg}")
        self.msgDecodeFunction(msg, self.sharedResources)

    def setup_bluetooth(self, port = 1):
        self.btport = port

        os.system("sudo hciconfig hci0 piscan")
        os.system(f"sudo sdptool add --channel={self.btport} SP")
        os.system(f"sudo rfcomm listen 0 {self.btport} &")

        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        success = 0
        while not success:
            try:
                server_sock.bind(("", self.btport))
                server_sock.listen(self.btport)
                print("[BT] Bound to port %d" % self.btport)
                success = 1
            except Exception as e:
                print("[BT] Could not bind to port %d: %s" % (self.btport, e))

        if success:
            print("[BT] Waiting for connection on RFCOMM channel %d" % self.btport)
        else:
            print("[BT] Failed to bind after trying multiple ports.")


class AndriodApp:
    def __init__(self, port):
        self.interface = AppInterface(port=port, baudrate=115200)
        self.interface.setSharedResources(sharedResources)
        self.interface.setupProtocol()
    
    def txMapDets(self):
        pass
    
    def txBotLocation(self):
        pass


if __name__ == "__main__":
    instrs = [
        "/*MAP=[(0, 00, 00, 1),(1, 00, 00, 2)]*/",
        "/*TASKMODE=MANUAL*/",
        "/*TASKMODE=TASK1*/",
        "/*TASKMODE=TASK2*/",
        "/*TASKMODE=TASKB*/",
        "/*TASKSTATUSREQ=START*/",
        "/*TASKSTATUSREQ=PAUSE*/",
        "/*TASKSTATUSREQ=STOP*/",
        "/*MMOVE=F*/",
        "/*MMOVE=B*/",
        "/*MMOVE=L*/",
        "/*MMOVE=R*/",
    ]

    for instr in instrs:
        AppMessageProtocol.decodeMessage(instr)
