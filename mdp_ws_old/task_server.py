from constants import CarMode
from handlers import ManualHandler, BulleyeHandler
from algo_server import AlgoServer
from instructions import Instructions
from car import Car

class TaskServer:
    def __init__(self, car: Car):
        self.car = car
        self.carMode = CarMode.MANUAL
        self.newCarMode = False
        self.instructions = Instructions()
        self.algoServer = AlgoServer()

    def changeCarMode(self, carMode: CarMode):
        self.carMode = carMode
        self.newCarMode = True

    def processInstructionsTask(self):
        if self.newCarMode:
            self.newCarMode = False
            # Clear and load instructions based on new mode.
            self.instructions.clear()
            if self.carMode == CarMode.MANUAL:
                self.instructions.load_instructions(["WAIT_FOR_ANDROID"])
            elif self.carMode == CarMode.BULLEYE:
                self.instructions.load_instructions(["BULLSEYE_DETECTION"])
        
        if self.carMode == CarMode.MANUAL:
            self.manualTask()
        elif self.carMode == CarMode.BULLEYE:
            self.bullseyeTask()
        else:
            print("Mode not implemented.")

    def manualTask(self):
        mh = ManualHandler(self.car)
        mh.handle()

    def bullseyeTask(self):
        bh = BulleyeHandler(self.car)
        bh.handle()

