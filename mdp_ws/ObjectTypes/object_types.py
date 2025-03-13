from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

# from PathFinding_task2.constants import TASK2_CAR_START_X, TASK2_CAR_START_Y


class Facing(Enum):
    east = 0
    north = 1
    west = 2
    south = 3


class LocationType(Enum):
    empty = 0
    obstacle = 1
    landing = 2
    landing_cleared = 3
    landing_padding = 4
    parking_barrier = 5


class Position(BaseModel):
    x: float
    y: float
    locationType: LocationType
    facing: Facing = Facing.north
    result: Optional[str] = "No result"
    id: Optional[int] = -1


class Direction(Enum):
    right = 1
    straight = 2
    left = 3
    reverse = 4
    reverse_right = 5
    reverse_left = 6


class Vector(BaseModel):
    x: float
    y: float


class Movement(BaseModel):
    distance_cm: float
    turning_radian: float
    direction: Direction
    start_position: Position 
    end_position: Position 
    circle_center: Optional[Position] = None


class MinimumPath(BaseModel):
    distance: float
    movements_to_take: List[Movement]


class Car(BaseModel):
    current_position: Position
    facing_radian: float


class GameObstacleScanning(BaseModel):
    obstacle_position: Position
    # path: List[Movement] = None
    car: Car
    landing_positions: List[Position] = None
    solution: List[MinimumPath] = []
    solution_str: List[str] = "No solution"

class GameTask1(BaseModel):
    arena: List[List[Position]]
    # path: List[Movement] = None
    car: Car
    solution: List[MinimumPath] = []

class TravelledSalesman(BaseModel):
    total_distance: float
    obstacle_seq: List[int]
    movement_path: List[Movement]
    movement_string: List[str]


class WebsocketMessageType(Enum):
    change_mode = 1
    obstacle_result = 2
    reached_obstacle = 3
    stm_instr_set = 4
    obstacle_positions = 5
    ultrasonic_dist = 6

class WebsocketMessage(BaseModel):
    message_type: WebsocketMessageType
    value: str


class SessionMode(Enum):
    task1 = 0
    task2 = 1
    obstacle_scanning = 2


class Task2Progress(Enum):
    car_initial_parked = 0
    next_to_obstacle_1 = 1
    next_to_obstacle_1_on_return = 2
    parking_car = 4


class ArrowDirection(Enum):
    left = 1
    right = 2
    none = 3

# class GameTask2(BaseModel):
#     obstacle_1_landing: Optional[Position] = None
#     obstacle_1: Optional[Position] = None
#     car_start_location: Position = Position(x=TASK2_CAR_START_X, y=TASK2_CAR_START_Y, locationType = LocationType.landing)
