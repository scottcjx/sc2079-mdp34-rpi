from ObjectTypes.object_types import *
from PathFinding_task2.constants import *
from PathFinding_task2.game_solver import GameSolverTask2
from ComputerServer.data_manager import DataManager
import numpy as np


def point_to_segment_distance(px, py, x1, y1, x2, y2):
    # Convert points to numpy arrays for easier calculations
    P = np.array([px, py])
    A = np.array([x1, y1])
    B = np.array([x2, y2])

    # Vector AB
    AB = B - A
    # Vector AP
    AP = P - A
    # Vector BP
    BP = P - B

    # Calculate the squared length of AB
    AB_squared = np.dot(AB, AB)

    if AB_squared == 0:  # A and B are the same point
        return np.linalg.norm(AP)  # Distance from P to A (or 😎

    # Project point P onto the line defined by A and B
    t = np.dot(AP, AB) / AB_squared

    if t < 0:  # P projects out the line segment, nearest to A
        nearest_point = A
    elif t > 1:  # P projects out the line segment, nearest to B
        nearest_point = B
    else:  # P projects onto the line segment
        nearest_point = A + t * AB

    # Calculate the distance from P to the nearest point
    distance = np.linalg.norm(P - nearest_point)
    return distance

class Pathfinding_Task2_Manager:
    def __init__(self):
        self.data_manager = None
        self.game_solver = GameSolverTask2()
        self.parking_to_obstacle1_updated = False
        self.next_to_obstacle1_to_south_of_obstacle1_updated = False
        self.car_position = Position(x=TASK2_CAR_START_X,y=TASK2_CAR_START_Y,locationType=LocationType.empty)
        pass

    def set_data_manager(self, data_manager: DataManager):
        self.data_manager = data_manager

    def run(self):
        while True:
            self.update_path()

    def update_path(self):
        if self.data_manager is None:
            print("No data manager in Path Finding")
            return

        if self.data_manager.task2progress == Task2Progress.car_initial_parked and not self.parking_to_obstacle1_updated:
            if self.data_manager.obstacle1_distance_from_parking is None:
                print("Need distance to obstacle 1 first")
                return
            if self.data_manager.obstacle1_arrow == ArrowDirection.none:
                print("Need the direction of obstacle 1 first")
                return
            self.game_solver.obstacle.append(Position(x=TASK2_CAR_START_X, y=TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking, locationType = LocationType.obstacle))
            if self.data_manager.obstacle1_arrow == ArrowDirection.left:
                pos = Position(x=TASK2_CAR_START_X - TASK2_DISTANCE_NEXT_TO_OBSTACLE_1, y = TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking + GRID_SIZE // 2 + TASK2_CAR_ASS_OUTOFPARKING + 5, locationType = LocationType.landing)
                move_index = 1
            else:
                pos = Position(x=TASK2_CAR_START_X + TASK2_DISTANCE_NEXT_TO_OBSTACLE_1, y = TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking + GRID_SIZE // 2 + TASK2_CAR_ASS_OUTOFPARKING + 5, locationType = LocationType.landing)
                move_index = 3

            self.data_manager.add_task2_move(f"SF0{TASK2_CAR_ASS_OUTOFPARKING}")

            self.car_position.y += 20

            total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position, dest=pos)
            string_path = self.game_solver.convert_to_command(path)
            for item in string_path:
                self.data_manager.add_task2_move(item)

            self.data_manager.add_task2_move(f"{RCHED_LOC_TAG}{Task2Progress.next_to_obstacle_1.value}")
            self.parking_to_obstacle1_updated = True
            self.car_position = pos

        elif self.data_manager.task2progress == Task2Progress.next_to_obstacle_1 and not self.next_to_obstacle1_to_south_of_obstacle1_updated:
            if self.data_manager.obstacle2_distance_from_obstacle1 is None:
                print("Need to update distance from obstacle1 to obstacle2")
                return
            if self.data_manager.obstacle2_width is None:
                print("Need to update width of obstacle2")
                return
            if self.data_manager.obstacle2_arrow == ArrowDirection.none:
                print("Need to update direction of arrow 2")
                return

            y = self.car_position.y + self.data_manager.obstacle2_distance_from_obstacle1 + 25
            x_left_obstacle2 = TASK2_CAR_START_X - self.data_manager.obstacle2_width // 2 - CAR_TURNING_RADIUS
            x_right_obstacle2 = TASK2_CAR_START_X + self.data_manager.obstacle2_width // 2 + CAR_TURNING_RADIUS

            landing_left_obstacle2 = Position(y=y ,x=x_left_obstacle2,locationType=LocationType.landing)
            landing_right_obstacle2 = Position(y=y ,x=x_right_obstacle2,locationType=LocationType.landing)
            dest = None
            move_index = None
            if self.data_manager.obstacle2_arrow == ArrowDirection.left:
                dest = landing_left_obstacle2
            elif self.data_manager.obstacle2_arrow == ArrowDirection.right:
                dest = landing_right_obstacle2

            if self.data_manager.obstacle1_arrow == ArrowDirection.left:
                if self.data_manager.obstacle2_arrow == ArrowDirection.left:
                    move_index = 1
                elif self.data_manager.obstacle2_arrow == ArrowDirection.right:
                    move_index = 3
            elif self.data_manager.obstacle1_arrow == ArrowDirection.right:
                if self.data_manager.obstacle2_arrow == ArrowDirection.right:
                    move_index = 3
                elif self.data_manager.obstacle2_arrow == ArrowDirection.left:
                    move_index = 1

            if move_index is None or dest is None:
                print("Move index or Destination is none")
                return
            total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position, dest=dest)
            string_path = self.game_solver.convert_to_command(path)
            print(f"{string_path=}")
            for item in string_path:
                self.data_manager.add_task2_move(item)

            self.car_position = dest

            if self.data_manager.obstacle2_arrow == ArrowDirection.left:
                move_index = 4
                landing_right_obstacle2.facing = Facing.south
                total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position, dest=landing_right_obstacle2)
                self.car_position = landing_right_obstacle2
            elif self.data_manager.obstacle2_arrow == ArrowDirection.right:
                move_index = 0
                landing_left_obstacle2.facing = Facing.south
                total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position, dest=landing_left_obstacle2)
                self.car_position = landing_left_obstacle2

            string_path_1 = self.game_solver.convert_to_command(path)

            for item in string_path_1:
                self.data_manager.add_task2_move(item)

            distance = point_to_segment_distance(px=CAR_X_START_POS,
                                                 py=TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking + 5,
                                                 x1=self.car_position.x, y1=self.car_position.y, x2=CAR_X_START_POS,
                                                 y2=CAR_Y_START_POS + 15)

            distance_left_obs = point_to_segment_distance(px=CAR_X_START_POS - 30,
                                                 py=TASK2_CAR_START_Y,
                                                 x1=self.car_position.x, y1=self.car_position.y, x2=CAR_X_START_POS,
                                                 y2=CAR_Y_START_POS + 15)

            distance_right_obs = point_to_segment_distance(px=CAR_X_START_POS + 30,
                                                          py=TASK2_CAR_START_Y,
                                                          x1=self.car_position.x, y1=self.car_position.y,
                                                          x2=CAR_X_START_POS,
                                                          y2=CAR_Y_START_POS + 15)
            added_distance = 30
            print(distance)
            # TODO: HERE
            execute = True
            # execute = False
            if execute and (distance < 15 or distance_right_obs < 10 or distance_left_obs < 10):
                location_next_to_obstacle1 = None
                added_distance = 10
                if self.data_manager.obstacle2_arrow == ArrowDirection.left:
                    location_next_to_obstacle1 = Position(x=TASK2_CAR_START_X + TASK2_DISTANCE_NEXT_TO_OBSTACLE_1, y=TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking + 25, locationType=LocationType.landing, facing=Facing.south)
                    move_index = 3
                elif self.data_manager.obstacle2_arrow == ArrowDirection.right:
                    location_next_to_obstacle1 = Position(x=TASK2_CAR_START_X - TASK2_DISTANCE_NEXT_TO_OBSTACLE_1, y=TASK2_CAR_START_Y + self.data_manager.obstacle1_distance_from_parking + 25, locationType=LocationType.landing, facing=Facing.south)
                    move_index = 1
                if location_next_to_obstacle1 is None:
                    print("No landing next to obstacle 1")
                    return

                total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position,
                                                                             dest=location_next_to_obstacle1)
                self.car_position = location_next_to_obstacle1
                string_path = self.game_solver.convert_to_command(path)
                for item in string_path:
                    self.data_manager.add_task2_move(item)
                self.data_manager.add_task2_move(f"{RCHED_LOC_TAG}{Task2Progress.next_to_obstacle_1_on_return.value}")
            final_position = Position(x=TASK2_CAR_START_X, y=TASK2_CAR_START_Y + added_distance, locationType=LocationType.landing, facing=Facing.south)
            total_distance, path = self.game_solver.solve_move_safe_path(move_index, src=self.car_position,
                                                                         dest=final_position)
            self.car_position = final_position
            string_path = self.game_solver.convert_to_command(path)
            for index, item in enumerate(string_path):
                if index == len(string_path) - 1:
                    break
                self.data_manager.add_task2_move(item)
                self.data_manager.add_task2_move(f"{RCHED_LOC_TAG}{Task2Progress.parking_car.value}")

            self.next_to_obstacle1_to_south_of_obstacle1_updated = True
