import re
import threading
import time
import logging
from queue import Queue, Empty
from sharedResources import SharedRsc, sharedResources
from definitions import *
from car import Car
from androidapp import AndroidApp

#####
from ComputerServer.main import AlgoMain
from ComputerServer.data_manager import DataManager
from PathFinding_task2.Task2_Pathfinding_Manager import Pathfinding_Task2_Manager
from ObjectTypes.object_types import *
#####

logger = logging.getLogger("TaskServer")

class TaskServer:
    def __init__(self, car: Car, android_app: AndroidApp, shared_resources: SharedRsc):
        self.car = car
        self.android_app = android_app
        self.shared_resources = shared_resources
        self.current_mode = "MANUAL"
        self.mode_changed = False
        self._running = False
        self.loop_thread = None

        #####
        # Task-specific components
        self.algo_main = AlgoMain()
        self.data_manager = DataManager()
        self.task2_manager = Pathfinding_Task2_Manager()
        self.task2_manager.set_data_manager(self.data_manager)
        
        # Status tracking
        self.task_status = "STOP"
        self.current_command_index = 0
        self.commands = []
        #####

        # Ensure mode request queue exists
        if not self.shared_resources.get("TASK.MODE.REQ"):
            self.shared_resources.set("TASK.MODE.REQ", Queue(1))

    def setup_manual(self):
        logger.info("[TaskServer] Setting up MANUAL mode")
        self.shared_resources.set("APP.MOVE.REQ", Queue(1))
        #####
        self.shared_resources.set("TASK.STATUS", "STOP")
        self.task_status = "STOP"
        #####
    
    def loop_manual(self):
        logger.debug("[TaskServer] Loop MANUAL mode")
        try:
            move_cmd = self.shared_resources.get("APP.MOVE.REQ").get_nowait()
            # Use standardized API: move_standard for Car.
            self.car.move(move_cmd)
        except Empty:
            pass

    def setup_task1(self):
        logger.info("[TaskServer] Setting up TASK1 mode")
        # TODO: Initialize components specific to TASK1.
        #####
        # if self.data_manager:
        #     self.data_manager.update_mode(SessionMode.task1)
        
        # Reset status
        self.shared_resources.set("TASK.STATUS", "STOP")
        self.task_status = "STOP"
        self.current_command_index = 0
        self.commands = []

        # Setup required queues
        if not self.shared_resources.get("MAP.NEW.FLAG"):
            self.shared_resources.set("MAP.NEW.FLAG", 0)
        
        # Check if map data is available
        map_str = self.shared_resources.get("MAP.STR")
        if map_str:
            processed_map_str = self._process_map_data(map_str)

        try:
            self.algo_main.main(processed_map_str)
            logger.info("algo main successful")

        except:
            logger.error("algo main failed")
        #####
        pass

    def loop_task1(self):
        logger.debug("[TaskServer] Loop TASK1 mode")
        # TODO: Add processing logic for TASK1.
        #####
        # Check for map updates
        if self.shared_resources.get("MAP.NEW.FLAG") == 1:
            map_str = self.shared_resources.get("MAP.STR")
            if map_str:
                self._process_map_data(map_str)
            self.shared_resources.set("MAP.NEW.FLAG", 0)
        
        # Check for status change
        self._check_task_status_change()
        
        # Check car response
        car_status = self.shared_resources.get("CAR.STATUS")
        if car_status == "IDLE" and self.task_status == "IN-PROGRESS":
            self._handle_car_response('A')
        #####
        pass

    def setup_task2(self):
        logger.info("[TaskServer] Setting up TASK2 mode")
        # TODO: Initialize components specific to TASK2.
        #####
        if self.data_manager:
            self.data_manager.update_mode(SessionMode.task2)
        
        # Reset status
        self.shared_resources.set("TASK.STATUS", "STOP")
        self.task_status = "STOP"
        self.current_command_index = 0
        self.commands = []
        #####
        pass

    def loop_task2(self):
        logger.debug("[TaskServer] Loop TASK2 mode")
        # TODO: Add processing logic for TASK2.
        #####
        # Check for status change
        self._check_task_status_change()
        
        # Check car response
        car_status = self.shared_resources.get("CAR.STATUS")
        if car_status == "IDLE" and self.task_status == "IN-PROGRESS":
            self._handle_car_response('A')
        
        # Check for ultrasonic distance updates
        car_range = self.shared_resources.get("CAR.RANGE")
        if car_range is not None and self.task_status == "IN-PROGRESS":
            self.data_manager.handle_ultrasonic(str(car_range))
        #####
        pass

    def setup_taskB(self):
        logger.info("[TaskServer] Setting up TASKB mode")
        # TODO: Initialize components specific to TASKB.
        #####
        # Initialize components specific to TASKB (obstacle scanning)
        if self.data_manager:
            self.data_manager.update_mode(SessionMode.obstacle_scanning)
        
        # Reset status
        self.shared_resources.set("TASK.STATUS", "STOP")
        self.task_status = "STOP"
        self.current_command_index = 0
        self.commands = []
        #####
        pass

    def loop_taskB(self):
        logger.debug("[TaskServer] Loop TASKB mode")
        # TODO: Add processing logic for TASKB.
        #####
        # Check for status change
        self._check_task_status_change()
        
        # Check car response
        car_status = self.shared_resources.get("CAR.STATUS")
        if car_status == "IDLE" and self.task_status == "IN-PROGRESS":
            self._handle_car_response('A')
        #####
        pass

    def setup(self):
        logger.info("[TaskServer] Setup")
        self.shared_resources.set("TASK.MODE", "MANUAL")
        self.setup_manual()

    def _handle_mode_change(self):
        try:
            mode_queue = self.shared_resources.get("TASK.MODE.REQ")
            new_mode = mode_queue.get_nowait()
            self.shared_resources.set("TASK.MODE", new_mode)
            self.current_mode = new_mode
            self.mode_changed = True
            logger.info(f"Switched to mode: {new_mode}")
        except Empty:
            pass

    def loop(self):
        self._running = True
        while self._running:
            self.mode_changed = False
            self._handle_mode_change()
            mode = self.shared_resources.get("TASK.MODE")
            if mode is None:
                mode = "MANUAL"
                self.shared_resources.set("TASK.MODE", mode)
            if mode == "MANUAL":
                if self.mode_changed:
                    self.setup_manual()
                self.loop_manual()
            elif mode == "TASK1":
                if self.mode_changed:
                    self.setup_task1()
                self.loop_task1()
            elif mode == "TASK2":
                if self.mode_changed:
                    self.setup_task2()
                self.loop_task2()
            elif mode == "TASKB":
                if self.mode_changed:
                    self.setup_taskB()
                self.loop_taskB()
            else:
                logger.warning("Unknown mode: %s", mode)
            time.sleep(0.05)

    def _process_map_data(self, map_str):
        """
        Process a map string in the format MAP=[[0,06,12,0],[1,10,19,2],[2,14,15,1]]
        
        Args:
            map_str (str): A string representing map data
        
        Returns:
            list: A list of dictionaries representing obstacle data
        """
        # Extract the map data using regex
        match = re.search(r'MAP=\[\[(.*?)\]\]', map_str)
        if not match:
            raise ValueError("Invalid map string format")
        
        # Extracted content inside MAP=[[]]
        map_data_str = match.group(1)

        # Convert the string to a list of lists
        map_data = [item.strip().split(',') for item in map_data_str.split('],[')]

        # Convert to the required format
        processed_data = []
        facing_map = {0: 'N', 1: 'S', 2: 'E', 3: 'W'}

        for obstacle in map_data:
            processed_obstacle = {
                "dir": facing_map[int(obstacle[3])],  # Convert facing index to direction
                "x": int(obstacle[1]),  # Convert X coordinate
                "y": int(obstacle[2]),  # Convert Y coordinate
                "id": int(obstacle[0])  # Convert ID
            }
            processed_data.append(processed_obstacle)

        return processed_data
    
    def start(self):
        if self.loop_thread is None or not self.loop_thread.is_alive():
            self.loop_thread = threading.Thread(target=self.loop, daemon=True)
            self.loop_thread.start()
            logger.info("TaskServer started.")

    def stop(self):
        self._running = False
        if self.loop_thread:
            self.loop_thread.join()
            logger.info("TaskServer stopped.")
