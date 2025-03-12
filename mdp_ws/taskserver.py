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
        sharedResources.set("APP.MOVE.REQ", Queue(1))

    def loopManual(self):
        if sharedResources.get("APP.MOVE.REQ").not_empty:
            # has new command request
            cmd = sharedResources.get("APP.MOVE.REQ").get()
            self.car.move_std(cmd)

    def setupTask1(self):
        pass

    def loopTask1(self):
        
        # if map not yet entered, wait for map entry

        # if map is entered, new flag up

        # process map, send map to algo, receive instructions from the algo
        # queue move instructions into cache

        # if pause & stop cmd in cmd queue, handle accordingly

        
        pass

    def setupTask2(self):
        pass

    def loopTask2(self):
        pass

    def setupTaskB(self):
        pass

    def loopTaskB(self):
        pass

    def setup(self):
        pass

    def loop(self):
        flag_newtask = 0
        #  if there is a new req for MODE, handle
        if self.sharedResource.get("TASK.MODE.REQ").not_empty:
            # clean up

            newmode = self.sharedResource.get("TASK.MODE.REQ").get()
            self.sharedResources.set("TASK.MODE", newmode)
            flag_newtask = 1

        self.taskmode = self.sharedResources.get("TASK.MODE")

        if (self.taskmode == "MANUAL"):
            if flag_newtask:
                self.setupManual()
            self.loopManual()
        elif (self.taskmode == "TASK1"):
            if flag_newtask:
                self.setupTask1()
            self.loopTask1()
        elif (self.taskmode == "TASK2"):
            if flag_newtask:
                self.setupTask2()
            self.loopTask2()
        elif (self.taskmode == "TASKB"):
            if flag_newtask:
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

    # def receive_commands(self):
    #     while True:
    #         command = input("Enter command (or type 'exit' to quit): ")
    #         if command.lower() == 'exit':
    #             break
    #         self.instruction_queue.put(command)

    # def process_instructions(self):
    #     while True:
    #         instruction = self.instruction_queue.get()
    #         if instruction is None:
    #             break
    #         self.car_interface.send_command(instruction)
    #         data = self.car_interface.receive_data()
    #         print("Received from car:", data)

    # def run(self):
    #     receive_thread = threading.Thread(target=self.receive_commands)
    #     process_thread = threading.Thread(target=self.process_instructions)

    #     receive_thread.start()
    #     process_thread.start()

    #     receive_thread.join()
    #     process_thread.join()

    # def close(self):
    #     self.car_interface.close()
    #     self.android_app_interface.close()