from enum import Enum

class carMovementStates(Enum):
    WAITING = 0
    MOVING = 1
    MOVED = 2

class bullseyeStates(Enum):
    SEE_NOTHING = 0
    SEEN_VALID = 1
    SEEN_BULLSEYE = 2

class FSM():
    states: Enum
    current_state = None

    def __init__(self, states = None):
        self.states = states

    def getState(self):
        return self.current_state

    def setState(self, state):
        self.current_state = state


