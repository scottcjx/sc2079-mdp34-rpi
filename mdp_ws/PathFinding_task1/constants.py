from ObjectTypes.object_types import Direction

WHITE = (255, 255, 255)
RED = (252, 203, 199)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
DARK_RED = (139, 0, 0)
LIGHT_RED = (255, 102, 102)
DARK_BLUE = (0, 0, 139)
LIGHT_BLUE = (173, 216, 230)
DARK_GRAY = (169, 169, 169)
LIGHT_GRAY = (211, 211, 211)
GREEN = (217, 255, 230)
DARK_GREEN = (0, 100, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

SCALE_FACTOR = 4
START_BOX_SIZE = 30
GRID_COUNT = 20
CAR_X_START_POS = 15
CAR_Y_START_POS = 5
OBSTACLE_COUNT = 5
ARENA_SIZE = 200
REVERSE_STRAIGHT_DISTANCE = 15
CAR_SPEED = 1
CAR_TURNING_RADIUS = 31
RENDER_SPEED = 0.01
TURNING_RADIAN_INCREMENT = CAR_SPEED / CAR_TURNING_RADIUS
GRID_SIZE = ARENA_SIZE // GRID_COUNT
LOWER_GRID_BOUND = 5
HIGHER_GRID_BOUND = 195
CAR_BACK_TO_CENTER = 8

MOVING_TAG = "MOVING_TO:"
REACHED_TAG = "REACHED:"
SAFETY_DISTANCE_EDGE = 3
SAFETY_DISTANCE_OBSTACLE = 15
SAFETY_DISTANCE_TURNING_OBSTACLE = 45
SAFETY_DISTANCE_TURNING_EDGE = 30
LANDING_DISTANCE = 2
ANGLE_SUPPLEMENT = 0

TURNING_EDGE_DISTANCE_FROM_OBSTACLE = 15
LANDING_SUPPLEMENT = 10
LEGAL_MOVES = [
    [Direction.left, Direction.straight, Direction.left],  # Done 0
    [Direction.left, Direction.straight, Direction.right],  # Done 1
    [Direction.left, Direction.right, Direction.left], # 2
    [Direction.right, Direction.straight, Direction.left],  # Done 3
    [Direction.right, Direction.straight, Direction.right],  # Done 4
    [Direction.right, Direction.left, Direction.right], #5
    [Direction.reverse_right, Direction.straight, Direction.left], #6
    [Direction.reverse_right, Direction.straight, Direction.right], #7
    [Direction.reverse_left, Direction.straight, Direction.left], #8
    [Direction.reverse_left, Direction.straight, Direction.right] #9
]
