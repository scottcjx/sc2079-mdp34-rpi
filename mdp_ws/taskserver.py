import threading
import time
import logging
from queue import Queue, Empty
from sharedResources import SharedRsc, sharedResources
from definitions import *
from car import Car
from androidapp import AndroidApp

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

        # Ensure mode request queue exists
        if not self.shared_resources.get("TASK.MODE.REQ"):
            self.shared_resources.set("TASK.MODE.REQ", Queue(1))

    def setup_manual(self):
        logger.info("[TaskServer] Setting up MANUAL mode")
        self.shared_resources.set("APP.MOVE.REQ", Queue(1))
    
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
        pass

    def loop_task1(self):
        logger.debug("[TaskServer] Loop TASK1 mode")
        # TODO: Add processing logic for TASK1.
        pass

    def setup_task2(self):
        logger.info("[TaskServer] Setting up TASK2 mode")
        # TODO: Initialize components specific to TASK2.
        pass

    def loop_task2(self):
        logger.debug("[TaskServer] Loop TASK2 mode")
        # TODO: Add processing logic for TASK2.
        pass

    def setup_taskB(self):
        logger.info("[TaskServer] Setting up TASKB mode")
        # TODO: Initialize components specific to TASKB.
        pass

    def loop_taskB(self):
        logger.debug("[TaskServer] Loop TASKB mode")
        # TODO: Add processing logic for TASKB.
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
