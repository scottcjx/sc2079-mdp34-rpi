import finiteStateMachine
import sharedResources

class ManualHandler:
    carInterface = None
    appInterface = None

    def __init__(self, carInterface, appInterface):
        self.carInterface = carInterface
        self.appInterface = appInterface

    def getNewAppMoveCmds(self):
        pass

    def handle(self):
        pass

#     def handle(self):
#         if BluetoothAPI.new_message():
#             rx_msg = BluetoothAPI.rx()
#             cmd = AndriodMsgProtocol.rx2cmd(rx_msg)
#             if cmd is not None:
#                 # Execute movement: for example, move 10mm @ 30mm/s.
#                 self.car.move(cmd, 10, 30)
#             else:
#                 print("Received invalid command.")
#         else:
#             print("No new Bluetooth message.")

class BulleyeHandler:

    cls_detector = None
    carInterface = None

    def __init__(self, cls_detector, carInterface):
        self.cls_detector = cls_detector
        self.carInterface = carInterface

    def begin():
        sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.WAITING)
        

    def bullseyeTask(self):
        det = self.cls_detector()
        if 0 in det:
            sharedResources.fsm = 1
            print("det 0")
        elif 3 in det:
            sharedResources.fsm = 2
            print("det 3")
        else:
            sharedResources.fsm = 0

        if sharedResources.fsm == 0:
            if sharedResources.carMovementFSM.getState == finiteStateMachine.carMovementStates.WAITING:
                self.carInterface.tx(b"SF005")
                sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.MOVING)
            elif sharedResources.carMovementFSM.getState() == finiteStateMachine.carMovementStates.MOVED:
                sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.WAITING)

        elif sharedResources.fsm == 1:

            if sharedResources.fsm2 == 0:
                if sharedResources.carMovementFSM.getState == finiteStateMachine.carMovementStates.WAITING:
                    self.carInterface.tx(b"TL045")
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.MOVING)
                if sharedResources.carMovementFSM.getState() == finiteStateMachine.carMovementStates.MOVED:
                    sharedResources.fsm2 = 1
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.WAITING)
                
            elif sharedResources.fsm2 == 1:
                if sharedResources.carMovementFSM.getState == finiteStateMachine.carMovementStates.WAITING:
                    self.carInterface.tx(b"SF010")
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.MOVING)
                if sharedResources.carMovementFSM.getState() == finiteStateMachine.carMovementStates.MOVED:
                    sharedResources.fsm2 = 2
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.WAITING)

            elif sharedResources.fsm2 == 2:
                if sharedResources.carMovementFSM.getState == finiteStateMachine.carMovementStates.WAITING:
                    self.carInterface.tx(b"TR045")
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.MOVING)
                if sharedResources.carMovementFSM.getState() == finiteStateMachine.carMovementStates.MOVED:
                    sharedResources.fsm2 = 0
                    sharedResources.carMovementFSM.setState(finiteStateMachine.carMovementStates.WAITING)
            sharedResources.fsm = 0
