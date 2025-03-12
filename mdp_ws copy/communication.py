import serial
import threading
import time
from abc import ABC, abstractmethod
from collections import deque

class AbstractSerialInterface(ABC):
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_connected = False
        self._rx_thread = None
        self._tx_thread = None
        self._rx_callback = None
        self._tx_buffer = deque()  # TX buffer (FIFO queue)
        self._tx_lock = threading.Lock()  # Lock for thread-safe access to the TX buffer

    @abstractmethod
    def rx_callback(self, data):
        """
        Abstract method that will be called when data is received.
        This method should be implemented by subclasses to define
        how to handle the incoming data.
        """
        pass

    def connect(self):
        """
        Establish serial connection.
        """
        if not self.is_connected:
            try:
                self.serial_connection = serial.Serial(
                    self.port, baudrate=self.baudrate, timeout=self.timeout
                )
                self.is_connected = True
                print(f"{self.port} Connected; {self.baudrate} baud.")
                self._start_rx_thread()
                self._start_tx_thread()  # Start the TX thread when connected
            except Exception:
                pass

    def disconnect(self):
        """
        Close serial connection.
        """
        if self.is_connected:
            self.is_connected = False
            if self._rx_thread is not None:
                self._rx_thread.join()  # Wait for the RX thread to finish.
            if self._tx_thread is not None:
                self._tx_thread.join()  # Wait for the TX thread to finish.
            if self.serial_connection:
                self.serial_connection.close()
                print(f"{self.port} Disconnected")
        else:
            print(f"{self.port} No active connection to disconnect.")

    def _start_rx_thread(self):
        """
        Start a background thread to handle data reception.
        """
        def receive_data():
            while self.is_connected:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.read(self.serial_connection.in_waiting)
                    if self._rx_callback:
                        print(f"{self.port} Data received: {data}")
                        self._rx_callback(data)
                    else:
                        self.rx_callback(data)
                time.sleep(0.1)

        self._rx_thread = threading.Thread(target=receive_data)
        self._rx_thread.daemon = True
        self._rx_thread.start()

    def _start_tx_thread(self):
        """
        Start a background thread to handle data transmission from the TX buffer.
        """
        def transmit_data():
            while self.is_connected:
                with self._tx_lock:
                    if self._tx_buffer:
                        data = self._tx_buffer.popleft()  # Get data from TX buffer
                        self.serial_connection.write(data)
                        print(f"{self.port} tx: {data}")
                time.sleep(0.1)

        self._tx_thread = threading.Thread(target=transmit_data)
        self._tx_thread.daemon = True
        self._tx_thread.start()

    def set_rx_callback(self, callback):
        """
        Set a custom RX callback function.
        """
        self._rx_callback = callback

    def tx(self, data):
        """
        Add data to the TX buffer.
        """
        if self.is_connected:
            with self._tx_lock:
                self._tx_buffer.append(data)  # Add data to TX buffer
                # print(f"{self.port} Data added to TX buffer: {data}")
        else:
            print(f"{self.port} Not connected. Cannot transmit data.")

    def rx(self):
        """
        Return the latest data received from the serial port.
        """
        if self.is_connected:
            data = self.serial_connection.read(self.serial_connection.in_waiting)
            return data
        else:
            print(f"{self.port} Not connected. Cannot receive data.")
            return None

