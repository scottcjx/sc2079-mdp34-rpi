import logging
from communication import AbstractSerialInterface
from sharedResources import SharedRsc, sharedResources
from queue import Queue
import definitions

logger = logging.getLogger("Car")

class CarMessageProtocol:
    sharedResources = None

    @classmethod
    def init_shared_resources(cls):
        logger.info("[CarMessageProtocol] Initializing shared resources")
        cls.sharedResources.set("CAR.MOVE.REQ", Queue(1))
        cls.sharedResources.set("CAR.STATUS", "IDLE")

    @classmethod
    def set_shared_resources(cls, shared_resources):
        cls.sharedResources = shared_resources

    @classmethod
    def decode_message(cls, msg):
        try:
            decoded_msg = msg.decode('utf-8').strip()
            logger.debug(f"Car RX Decoded: {decoded_msg}")
            
            # Processing incoming messages from the car
            if decoded_msg.startswith("RANGE"):
                parts = decoded_msg.split()
                if len(parts) >= 2:
                    try:
                        range_value = float(parts[1])
                        cls.sharedResources.set("CAR.RANGE", range_value)
                        logger.info(f"Updated car range: {range_value}")
                    except ValueError:
                        logger.warning(f"Invalid range value: {parts[1]}")
            
            elif decoded_msg.startswith("GYRO:"):
                # Process GYRO data - z-bearing only
                try:
                    # Extract the value after "GYRO: "
                    gyro_str = decoded_msg.replace("GYRO:", "").strip()
                    z_bearing = float(gyro_str)
                    cls.sharedResources.set("CAR.GYRO.Z", z_bearing)
                    logger.debug(f"Updated car z-bearing: {z_bearing}")
                except ValueError:
                    logger.warning(f"Invalid GYRO value: {decoded_msg}")
            
            elif decoded_msg.startswith("STATUS"):
                parts = decoded_msg.split()
                if len(parts) >= 2:
                    status = parts[1]
                    cls.sharedResources.set("CAR.STATUS", status)
                    logger.info(f"Updated car status: {status}")
            
            else:
                logger.debug(f"Unhandled car message: {decoded_msg}")
                
        except Exception as e:
            logger.error(f"Error decoding car message: {e}")

    @classmethod
    def encode_move(cls, direction: str, distance: int = 10):
        """
        Encodes a movement command according to the car's protocol.
        
        Args:
            direction: Direction to move ('F', 'B', 'L', 'R')
            distance: Distance value or angle (depends on direction)
            
        Returns:
            Formatted command string for the car
        """
        if direction not in definitions.MOVES:
            logger.warning(f"Invalid direction: {direction}")
            return None
            
        # Format commands according to car's protocol
        if direction == "F":
            return f"SF{str(distance).zfill(3)}"
        elif direction == "B":
            return f"SB{str(distance).zfill(3)}"
        elif direction == "L":
            return f"TL{str(distance).zfill(3)}"
        elif direction == "R":
            return f"TR{str(distance).zfill(3)}"
        
    @classmethod
    def encode_stop(cls):
        """Encodes a stop command for the car."""
        return "STOP"

class CarInterface(AbstractSerialInterface):
    def __init__(self, port, baudrate=115200, timeout=1):
        super().__init__(port, baudrate, timeout)
        self.msg_protocol_cls = CarMessageProtocol
        
    def set_shared_resources(self, shared_resources):
        self.sharedResources = shared_resources
        self.msg_protocol_cls.set_shared_resources(shared_resources)
        
    def setup_protocol(self):
        """Initialize protocol and shared resources"""
        self.msg_protocol_cls.init_shared_resources()
        
    def rx_callback(self, data):
        """Process received data using the protocol decoder"""
        logger.debug(f"Car RX: {data}")
        self.msg_protocol_cls.decode_message(data)

class Car:
    def __init__(self, port):
        self.interface = CarInterface(port=port, baudrate=115200)
        self.interface.set_shared_resources(sharedResources)
        self.interface.setup_protocol()

    def connect(self):
        """Connect to the car hardware"""
        self.interface.connect()

    def disconnect(self):
        """Disconnect from the car hardware"""
        self.interface.disconnect()

    def send_command(self, command: str):
        """
        Standardized API to send any command to the car.
        
        Args:
            command: The formatted command string to send
        """
        if isinstance(command, str):
            command = command.encode('utf-8')
        self.interface.tx(command)
        logger.info(f"Sent command to Car: {command}")

    def move(self, direction: str, distance: int = 10):
        """
        Sends a move command to the car using the standardized protocol.
        
        Args:
            direction: Direction to move ('F', 'B', 'L', 'R')
            distance: Distance value or angle (depends on direction)
        """
        command = CarMessageProtocol.encode_move(direction, distance)
        if command:
            self.send_command(command)
        else:
            logger.error(f"Failed to generate move command for direction: {direction}")

    def stop(self):
        """Sends a stop command to the car."""
        command = CarMessageProtocol.encode_stop()
        self.send_command(command)