import constants
    

# class CarState:
#     BOT_X = 0
#     BOT_Y = 0
#     BOT_HEADING = 0
#     ACK_FLAG = 0

# class AndriodState:
#     LAST_CMD = constants.AndriodCommandType.MODE_CHANGE

# class TaskState:
#     taskMode = constants.TaskMode.MANUAL


# carState = CarState()
# andriodState = AndriodState()
# taskState = TaskState()

from finiteStateMachine import *

carMovementFSM = FSM(carMovementStates)
carMovementFSM.setState(carMovementStates.WAITING)

fsm = 0
fsm2 = 0
arrow = -1
movementstatus = 0

mtcv_detections = None


