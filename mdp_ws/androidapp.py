import logging
import os
import bluetooth
import time
from queue import Queue, Empty

from protocol import Protocol
from communication import AbstractSerialInterface
from sharedResources import SharedRsc, sharedResources
import definitions

logger = logging.getLogger("AndroidApp")

class AppMessageProtocol:
    sharedResources: SharedRsc = None

    @classmethod
    def init_shared_resources(cls):
        logger.info("[AppMessageProtocol] Initializing shared resources")
        cls.sharedResources.set("TASK.MODE.REQ", Queue(1))
        cls.sharedResources.set("TASK.STATUS.REQ", Queue(1))
        cls.sharedResources.set("APP.MOVE.REQ", Queue(1))

    @classmethod
    def set_shared_resources(cls, shared_resources):
        cls.sharedResources = shared_resources

    @classmethod
    def decode_message(cls, msg: str):
        stripped = msg.strip()
        if not (stripped.startswith("/*") and stripped.endswith("*/")):
            logger.warning("Invalid message format: %s", msg)
            return
        cmdstr = stripped.removeprefix("/*").removesuffix("*/")
        parts = cmdstr.split("=")
        if len(parts) != 2:
            logger.warning("Malformed command: %s", msg)
            return
        cmd, val = parts
        cls.call_cmd(cmd, val)

    @classmethod
    def process_taskmode(cls, val):
        if val not in definitions.MODES:
            logger.warning("Invalid mode: %s", val)
            return
        try:
            cls.sharedResources.get("TASK.MODE.REQ").put_nowait(val)
            logger.info(f"Task mode set to {val}")
        except Exception as e:
            logger.error("Error setting task mode: %s", e)

    @classmethod
    def process_task_status(cls, val):
        if val not in definitions.TASKSTATUSES:
            logger.warning("Invalid task status: %s", val)
            return
        try:
            cls.sharedResources.get("TASK.STATUS.REQ").put_nowait(val)
            logger.info(f"Task status set to {val}")
        except Exception as e:
            logger.error("Error setting task status: %s", e)

    @classmethod
    def process_mmove(cls, val):
        if val not in definitions.MOVES:
            logger.warning("Invalid move command: %s", val)
            return
        try:
            cls.sharedResources.get("APP.MOVE.REQ").put_nowait(val)
            logger.info(f"Move command received: {val}")
        except Exception as e:
            logger.error("Error processing move command: %s", e)

    @classmethod
    def process_map(cls, val):
        if (cls.sharedResources.get("TASK.STATUS") == "IN-PROGRESS" and 
            str(cls.sharedResources.get("TASK.MODE")).startswith("TASK")):
            logger.warning("Map update rejected; task in progress.")
            return
        cls.sharedResources.set("MAP.NEW.FLAG", 1)
        cls.sharedResources.set("MAP.STR", val)
        logger.info(f"Map updated: {val}")

    @classmethod
    def call_cmd(cls, cmd, val):
        cmds = {
            "TASKMODE": cls.process_taskmode,
            "TASKSTATUSREQ": cls.process_task_status,
            "MMOVE": cls.process_mmove,
            "MAP": cls.process_map,
        }
        if cmd in cmds:
            cmds[cmd](val)
        else:
            logger.warning("Unknown command received: %s", cmd)

class AppInterface(AbstractSerialInterface):
    sharedResources: SharedRsc = None
    msg_protocol_cls = AppMessageProtocol

    def setup_protocol(self):
        self.msg_protocol_cls.set_shared_resources(self.sharedResources)
        self.msg_protocol_cls.init_shared_resources()

    def set_shared_resources(self, shared_resources):
        self.sharedResources = shared_resources

    def rx_callback(self, msg):
        # Automatically process the message via the protocol.
        logger.info(f"Android RX: {msg}")
        self.msg_protocol_cls.decode_message(msg)

    def setup_bluetooth(self, bt_port=1, bind_timeout=10):
        self.bt_port = bt_port
        logger.info("Setting up Bluetooth on port %d", bt_port)
        os.system("sudo hciconfig hci0 piscan")
        os.system(f"sudo sdptool add --channel={bt_port} SP")
        os.system(f"sudo rfcomm listen 0 {bt_port} &")
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        start_time = time.time()
        while True:
            try:
                server_sock.bind(("", bt_port))
                server_sock.listen(1)
                logger.info(f"[BT] Bound to port {bt_port}")
                break
            except Exception as e:
                logger.error("[BT] Could not bind to port %d: %s", bt_port, e)
                if time.time() - start_time > bind_timeout:
                    logger.error("Bluetooth bind timeout reached.")
                    break
                time.sleep(1)
        logger.info(f"[BT] Waiting for connection on RFCOMM channel {bt_port}")

class AndroidApp:
    def __init__(self, port):
        self.interface = AppInterface(port=port, baudrate=115200)
        self.interface.set_shared_resources(sharedResources)
        self.interface.setup_protocol()

    def connect(self):
        self.interface.connect()

    def disconnect(self):
        self.interface.disconnect()

    def send_command(self, command: str):
        """Standardized API to send any command from Android side."""
        self.interface.tx(command)
        logger.info(f"Sent command from Android: {command}")

    def transmit_map_details(self):
        """Sends map details using the standardized API."""
        command = "MAP_DETAILS"  # Placeholder for the actual command format.
        self.send_command(command)

    def transmit_bot_location(self):
        """Sends bot location using the standardized API."""
        command = "BOT_LOCATION"  # Placeholder for the actual command format.
        self.send_command(command)
