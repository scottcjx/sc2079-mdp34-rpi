import threading
from queue import Queue

import logging
from sharedResources import SharedRsc, sharedResources
from definitions import *

from car import Car
from andriodapp import AndriodApp

logger = logging.getLogger("TaskServer")



# notes:
# taskServer needs to be in task1 to rx map
# taskServer will listen to andriod rx queue commands

class TaskServer:
    sharedResources: SharedRsc

    def __init__(self, car: Car, andriodApp: AndriodApp, sharedResources):
        self.car = car
        self.androidApp = andriodApp
        self.sharedResources = sharedResources

    def setupManual(self):
        logger.info("[setupManual] Setup")
        sharedResources.set("APP.MOVE.REQ", Queue(1))

    def loopManual(self):
        logger.info("[loopManual]")
        if sharedResources.get("APP.MOVE.REQ").qsize() > 0:
            # has new command request
            cmd = sharedResources.get("APP.MOVE.REQ").get()
            self.car.move_std(cmd)

    def setupTask1(self):
        logger.info("[setupTask1] Setup")
        pass

    def loopTask1(self):
        logger.info("[loopTask1]")
        
        # if map not yet entered, wait for map entry

        # if map is entered, new flag up

        # process map, send map to algo, receive instructions from the algo
        # queue move instructions into cache

        # if pause & stop cmd in cmd queue, handle accordingly

        
        pass

    def setupTask2(self):
        logger.info("[setupTask2] Setup")
        pass

    def loopTask2(self):
        logger.info("[loopTask2]")
        pass

    def setupTaskB(self):
        logger.info("[setupTaskB] Setup")
        pass

    def loopTaskB(self):
        logger.info("[loopTaskB]")
        pass

    def setup(self):
        logger.info("[TaskServer] Setup")
        self.sharedResources.set("TASK.MODE", "MANUAL")
        self.setupManual()

    def loop(self):
        logger.info("[loop]")
        self.flag_newtask = 0
        
        #  if there is a new req for MODE, handle
        if self.sharedResources.get("TASK.MODE.REQ").qsize() > 0:
            logger.info("new TASK.MODE.REQ")
            # clean up
            newmode = self.sharedResources.get("TASK.MODE.REQ").get()
            self.sharedResources.set("TASK.MODE", newmode)
            self.flag_newtask = 1

        self.taskmode = self.sharedResources.get("TASK.MODE")

        if (self.taskmode == "MANUAL"):
            if self.flag_newtask:
                self.setupManual()
            self.loopManual()
        elif (self.taskmode == "TASK1"):
            if self.flag_newtask:
                self.setupTask1()
            self.loopTask1()
        elif (self.taskmode == "TASK2"):
            if self.flag_newtask:
                self.setupTask2()
            self.loopTask2()
        elif (self.taskmode == "TASKB"):
            if self.flag_newtask:
                self.setupTaskB()
            self.loopTaskB()

    def start(self):
        self.loop_thread = threading.Thread(target=self.loop)
        self.loop_thread.daemon = True
        self.loop_thread.start()

    def stop(self):
        self.loop_thread.join()
    



# decide the runner based on the current mode of the task.
# this means that the mode of task needs to be requested and in a queue, this is because it takes time to process the request to trasnfer.
# we will also need to stop the current context of the app, transfer the context elsewhere and cleanup before switching contexts

# this is a rtos system, interrupt based?

    