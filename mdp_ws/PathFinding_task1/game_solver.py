import json

from ObjectTypes.object_types import (
    GameTask1,
    Position,
    LocationType,
    Facing,
    Direction,
    MinimumPath,
    Movement,
    TravelledSalesman,

)
from PathFinding_task1.constants import *
import math
from typing import List
import numpy as np


class GameSolverTask1:

    def __init__(self, game: GameTask1) -> None:
        self.game = game
        self._initialize()
        self.edges = [[Position(x=0,y=0, locationType = LocationType.empty), Position(x=0,y=200, locationType = LocationType.empty)],
                 [Position(x=0,y=200, locationType = LocationType.empty), Position(x=200,y=200, locationType = LocationType.empty)],
                 [Position(x=0,y=0, locationType = LocationType.empty), Position(x=200,y=0, locationType = LocationType.empty)],
                 [Position(x=200,y=0, locationType = LocationType.empty), Position(x=200,y=200, locationType = LocationType.empty)]]
        self.landing_supplement = LANDING_SUPPLEMENT
        self.safety_distance_obstacle = SAFETY_DISTANCE_OBSTACLE
        self.safety_distance_edge = SAFETY_DISTANCE_EDGE
        self.safety_distance_turning_edge = SAFETY_DISTANCE_TURNING_EDGE
        self.safety_distance_turning_obstacle = SAFETY_DISTANCE_TURNING_OBSTACLE
    def _initialize(self):
        self.goals = []
        self.sale_path = None
        self.goals_to_id_mapping = {}
        self.shortest_distance_matrix = None
        self.check_edge = True
        self.obstacle = []
        for y in range(len(self.game.arena)):
            for x in range(len(self.game.arena[y])):
                if self.game.arena[y][x].locationType == LocationType.obstacle:
                    self.obstacle.append(self.game.arena[y][x])

    def _find_obstacle_locations(self):
        self.obstacle = []
        for y in range(len(self.game.arena)):
            for x in range(len(self.game.arena[y])):
                if self.game.arena[y][x].locationType == LocationType.obstacle:
                    self.obstacle.append(self.game.arena[y][x])

    def solve(self):

        self._plan_landing_zones()
        # print(self.game, "is Game")
        if self.game is None:
            return self.game, None, None
        self.goals.append(
            Position(
                x=CAR_X_START_POS, y=CAR_Y_START_POS, locationType=LocationType.empty
            )
        )


        self._populate_matrix()
        self._let_salesman_travel()
        # self._label_obstacles()
        if self.sale_path is None:
            if self.landing_supplement >= 15:
                self.landing_supplement *= 0.75
            elif self.safety_distance_obstacle >= 20:
                self.safety_distance_obstacle *= 0.75


            elif self.safety_distance_turning_edge >= 30:
                self.safety_distance_turning_edge *= 0.9
            elif self.safety_distance_turning_obstacle >= 45:
                self.safety_distance_turning_obstacle *= 0.9
            elif self.check_edge:                  
                self.check_edge = False            
            else:
                raise Exception("Really no solution possible")
            # print(f"{self.game=}")
            return self.solve()
        return (
            self.game,
            self.shortest_distance_matrix,
            self.sale_path,
            self.goals_to_id_mapping,
        )


    def _populate_matrix(self):
        for y in range(len(self.shortest_distance_matrix)):
            for x in range(len(self.shortest_distance_matrix)):
                if y == x:
                    continue
                src_initial = self.goals[y]
                dest = self.goals[x]
                value = self._solve_pair(src_initial, dest)
                self.shortest_distance_matrix[y][x] = value
        # self._print_matrix()
        pass

    def _solve_pair(self, src: Position, dest: Position):

        # print(f"Source: x= {src.x} y={src.y} facing={src.facing}")
        min_distance = math.inf
        min_move = []

        for index, move in enumerate(LEGAL_MOVES):
            for reverse_dir in [Direction.straight, Direction.right, Direction.left]:
                after_reverse_src, circle_center = self._find_reverse_dir(
                    pos=src, direction=reverse_dir
                )

                if src.x == CAR_X_START_POS and src.y == CAR_Y_START_POS:
                    moves_to_make = []
                else:
                    if reverse_dir == Direction.straight:
                        moves_to_make = [
                            Movement(
                                distance_cm=-REVERSE_STRAIGHT_DISTANCE,
                                turning_radian=0,
                                direction=reverse_dir,
                                start_position=src,
                                end_position=after_reverse_src,
                            ),
                        ]
                    else:
                        moves_to_make = [
                            Movement(
                                distance_cm=-(math.pi * CAR_TURNING_RADIUS * 2) / 4,
                                turning_radian=math.pi / 2,
                                direction=reverse_dir,
                                start_position=src,
                                end_position=after_reverse_src,
                                circle_center=circle_center,
                            ),
                        ]

                working_distance, working_movement = self._solve_move_safe_path(
                    move_index=index,
                    src=after_reverse_src,
                    dest=dest,
                    moves_to_make=moves_to_make,
                )

                if working_movement is None:
                    continue

                # print("Valid")

                if working_distance < min_distance:

                    min_distance = working_distance
                    min_move = working_movement

        try:
            minimum_path = MinimumPath(
                distance=min_distance, movements_to_take=min_move
            )
            return minimum_path
        except:
            return None

    def _print_matrix(self):

        def print_movement(min_path: MinimumPath):
            print(
                f"Distance: {min_path.distance:.2f}",
                end="\t",
            )

        for y in range(len(self.shortest_distance_matrix)):
            print(f"{y}: ", end=" -> ")
            for x in range(len(self.shortest_distance_matrix)):
                try:
                    print_movement(min_path=self.shortest_distance_matrix[y][x])

                except:
                    print(None, end=" ")

            print("\n")

    def _vector_properties(self, vector):
        length = np.linalg.norm(vector)
        angle_rad = np.arctan2(vector[1], vector[0]) % (2 * np.pi)
        return length, angle_rad

    def _find_reverse_dir(self, pos: Position, direction: Direction):

        if pos.x == CAR_X_START_POS and pos.y == CAR_Y_START_POS:
            new_x = pos.x
            new_y = pos.y
            cirle_x = 0
            circle_y = 0
            new_facing = Facing.north
        else:
            cirle_x, circle_y = self._get_circle_position(position=pos, move=direction)
            if cirle_x is None:
                cirle_x = 0
                circle_y = 0
            new_facing = None
            new_x = None
            new_y = None
            if direction == Direction.straight:
                if pos.facing == Facing.north:
                    new_y = pos.y - REVERSE_STRAIGHT_DISTANCE
                    new_x = pos.x

                elif pos.facing == Facing.east:
                    new_x = pos.x - REVERSE_STRAIGHT_DISTANCE
                    new_y = pos.y

                elif pos.facing == Facing.south:
                    new_y = pos.y + REVERSE_STRAIGHT_DISTANCE
                    new_x = pos.x

                elif pos.facing == Facing.west:
                    new_x = pos.x + REVERSE_STRAIGHT_DISTANCE
                    new_y = pos.y

                new_facing = pos.facing

            elif direction == Direction.right:
                if pos.facing == Facing.north:
                    new_facing = Facing.west
                    new_x = cirle_x
                    new_y = circle_y - CAR_TURNING_RADIUS

                elif pos.facing == Facing.east:
                    new_facing = Facing.north
                    new_y = circle_y
                    new_x = cirle_x - CAR_TURNING_RADIUS

                elif pos.facing == Facing.south:
                    new_facing = Facing.east
                    new_x = cirle_x
                    new_y = circle_y + CAR_TURNING_RADIUS

                elif pos.facing == Facing.west:
                    new_facing = Facing.south
                    new_y = circle_y
                    new_x = cirle_x + CAR_TURNING_RADIUS

            elif direction == Direction.left:
                if pos.facing == Facing.north:
                    new_facing = Facing.east
                    new_x = cirle_x
                    new_y = circle_y - CAR_TURNING_RADIUS

                elif pos.facing == Facing.east:
                    new_facing = Facing.south
                    new_x = cirle_x - CAR_TURNING_RADIUS
                    new_y = circle_y

                elif pos.facing == Facing.south:
                    new_facing = Facing.west
                    new_x = cirle_x
                    new_y = circle_y + CAR_TURNING_RADIUS

                elif pos.facing == Facing.west:
                    new_facing = Facing.north
                    new_x = cirle_x + CAR_TURNING_RADIUS
                    new_y = circle_y

            else:
                raise Exception("No appropriate direction")

        try:
            new_pos = Position(
                x=new_x, y=new_y, locationType=pos.locationType, facing=new_facing
            )
            # print(cirle_x, circle_y)
            cirlce_pos = Position(
                x=cirle_x, y=circle_y, locationType=LocationType.empty
            )
            return new_pos, cirlce_pos

        except Exception as e:
            print(e)
            raise e

    def _angle_between_vectors(self, v1, v2):
        v1 = np.array(v1)
        v2 = np.array(v2)

        if v1.shape[0] != 2 or v2.shape[0] != 2:
            raise ValueError("The function currently supports only 2D vectors.")

        dot_product = np.dot(v1, v2)

        mag_v1 = np.linalg.norm(v1)
        mag_v2 = np.linalg.norm(v2)

        cos_theta = dot_product / (mag_v1 * mag_v2)

        cos_theta = np.clip(cos_theta, -1.0, 1.0)

        angle_rad = np.arccos(cos_theta)

        cross_product_z = v1[0] * v2[1] - v1[1] * v2[0]

        if cross_product_z < 0:
            angle_rad = 2 * np.pi - angle_rad

        return angle_rad

    def _compute_arc_length(self, angle_rad):
        arc_length = CAR_TURNING_RADIUS * angle_rad
        return abs(arc_length)

    def _compute_arccos(self, value):
        value = np.clip(value, -1.0, 1.0)
        return np.arccos(value)

    def _rotate_vector(self, vector, radians):
        rotation_matrix = np.array(
            [[np.cos(radians), -np.sin(radians)], [np.sin(radians), np.cos(radians)]]
        )
        v_rotated = np.dot(rotation_matrix, vector)

        return v_rotated

    def _normalize_vector(self, vector):
        return vector / np.linalg.norm(vector)

    def _solve_move_safe_path(
        self, move_index: int, src: Position, dest: Position, moves_to_make: List
    ):
        move = LEGAL_MOVES[move_index]
        total_distance = math.inf

        dest_circle_x, dest_circle_y = self._get_circle_position(
            position=dest, move=move[2]
        )


        src_circle_x, src_circle_y = self._get_circle_position(
            position=src, move=move[0]
        )

        distance = math.sqrt(
            (dest_circle_x - src_circle_x) ** 2 + (dest_circle_y - src_circle_y) ** 2
        )

        if move_index == 0:  # [Direction.left, Direction.straight, Direction.left],
            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            v1_normal = np.array([v1[1], -v1[0]])

            v1_normal = self._normalize_vector(v1_normal)

            c1_tangent_point = (
                np.array([src_circle_x, src_circle_y]) + CAR_TURNING_RADIUS * v1_normal
            )
            c2_tangent_point = c1_tangent_point + v1
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(v1)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = self._angle_between_vectors(c1_to_src_vector, v1_normal)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(v1_normal, c2_to_dest_vector)

            total_distance = (
                straighline_distance
                + self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
            )

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.left,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            left_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.left,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_2)

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Left by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Left by: {angle_c2}
            #       """)

        elif move_index == 1:  # [Direction.left, Direction.straight, Direction.right],
            if distance < CAR_TURNING_RADIUS * 2:
                # #print("Edge Case: Distance cannot be less than 2 * r")
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = CAR_TURNING_RADIUS
            h_length = distance / 2
            anticlockwise_rotation_radians = -self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=anticlockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c1_tangent_point = (
                np.array([src_circle_x, src_circle_y])
                + CAR_TURNING_RADIUS * c1_normal_vector
            )
            c2_tangent_point = (
                np.array([dest_circle_x, dest_circle_y])
                - CAR_TURNING_RADIUS * c1_normal_vector
            )

            straight_line_vector = c2_tangent_point - c1_tangent_point
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(straight_line_vector)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = self._angle_between_vectors(c1_to_src_vector, c1_normal_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                c2_to_dest_vector, c1_normal_vector * -1
            )

            total_distance = (
                straighline_distance
                + self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
            )

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.left,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.right,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Left by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Right by: {angle_c2}
            #       """)

        elif move_index == 2:
            if distance > CAR_TURNING_RADIUS * 4:
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = distance / 2
            h_length = CAR_TURNING_RADIUS * 2
            clockwise_rotation_radians = -self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=clockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c3_center = (
                np.array([src_circle_x, src_circle_y])
                + 2 * CAR_TURNING_RADIUS * c1_normal_vector
            )

            c2_normal_vector = c3_center - np.array([dest_circle_x, dest_circle_y])
            c2_normal_vector = self._normalize_vector(vector=c2_normal_vector)

            c1_center_to_start = np.array([src.x - src_circle_x, src.y - src_circle_y])
            c1_center_to_end = (
                np.array([src_circle_x, src_circle_y])
                + CAR_TURNING_RADIUS * c1_normal_vector
            )
            angle_c1 = self._angle_between_vectors(
                v1=c1_center_to_start, v2=c1_normal_vector
            )

            c3_start = c1_normal_vector
            c3_end = c3_center - CAR_TURNING_RADIUS * c2_normal_vector
            angle_c3 = self._angle_between_vectors(
                v1=-c2_normal_vector, v2=-c1_normal_vector
            )

            c2_start = (
                np.array([dest_circle_x, dest_circle_y])
                + CAR_TURNING_RADIUS * c2_normal_vector
            )
            c2_center_to_end = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                v1=c2_normal_vector, v2=c2_center_to_end
            )

            total_distance = (
                self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
                + self._compute_arc_length(angle_rad=angle_c3)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Left by: {angle_c1}
            #       2. Right by: {angle_c3}
            #       3. Left by: {angle_c2}
            #       """)

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.left,
                start_position=src,
                end_position=Position(
                    x=c1_center_to_end[0],
                    y=c1_center_to_end[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c3),
                turning_radian=angle_c3,
                direction=Direction.right,
                start_position=Position(
                    x=c1_center_to_end[0],
                    y=c1_center_to_end[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c3_end[0], y=c3_end[1], locationType=LocationType.empty
                ),
                circle_center=Position(
                    x=c3_center[0], y=c3_center[1], locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            left_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.left,
                start_position=Position(
                    x=c3_end[0], y=c3_end[1], locationType=LocationType.empty
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_2)

        elif move_index == 3:  # [Direction.right, Direction.straight, Direction.left],

            if distance < CAR_TURNING_RADIUS * 2:
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = CAR_TURNING_RADIUS
            h_length = distance / 2
            anticlockwise_rotation_radians = self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=anticlockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c1_tangent_point = (
                np.array([src_circle_x, src_circle_y])
                + CAR_TURNING_RADIUS * c1_normal_vector
            )
            c2_tangent_point = (
                np.array([dest_circle_x, dest_circle_y])
                - CAR_TURNING_RADIUS * c1_normal_vector
            )

            straight_line_vector = c2_tangent_point - c1_tangent_point
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(straight_line_vector)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = self._angle_between_vectors(c1_normal_vector, c1_to_src_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                c1_normal_vector * -1, c2_to_dest_vector
            )

            total_distance = (
                straighline_distance
                + self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Right by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Left by: {angle_c2}
            #       """)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.right,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.left,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

        elif move_index == 4:  # [Direction.right, Direction.straight, Direction.right]
            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            v1_normal = np.array([-v1[1], v1[0]])

            v1_normal = self._normalize_vector(vector=v1_normal)

            c1_tangent_point = (
                np.array([src_circle_x, src_circle_y]) + CAR_TURNING_RADIUS * v1_normal
            )
            c2_tangent_point = c1_tangent_point + v1
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(v1)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = self._angle_between_vectors(v1_normal, c1_to_src_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(c2_to_dest_vector, v1_normal)

            total_distance = (
                straighline_distance
                + self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Right by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Right by: {angle_c2}
            #       """)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.right,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            right_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.right,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_2)

        elif move_index == 5:

            if distance > CAR_TURNING_RADIUS * 4:
                return total_distance, moves_to_make
            elif distance < CAR_TURNING_RADIUS * 2:
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = distance / 2
            h_length = CAR_TURNING_RADIUS * 2
            anticlockwise_rotation_radians = self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=anticlockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c3_center = (
                np.array([src_circle_x, src_circle_y])
                + 2 * CAR_TURNING_RADIUS * c1_normal_vector
            )

            c2_normal_vector = c3_center - np.array([dest_circle_x, dest_circle_y])
            c2_normal_vector = self._normalize_vector(vector=c2_normal_vector)

            c1_center_to_start = np.array([src.x - src_circle_x, src.y - src_circle_y])
            c1_end = (
                np.array([src_circle_x, src_circle_y])
                + CAR_TURNING_RADIUS * c1_normal_vector
            )
            angle_c1 = self._angle_between_vectors(
                v1=c1_normal_vector, v2=c1_center_to_start
            )

            c3_start = c1_end
            c3_end = c3_center - CAR_TURNING_RADIUS * c2_normal_vector
            angle_c3 = self._angle_between_vectors(
                v1=-c1_normal_vector, v2=-c2_normal_vector
            )

            c2_start = (
                np.array([dest_circle_x, dest_circle_y])
                + CAR_TURNING_RADIUS * c2_normal_vector
            )
            c2_center_to_end = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                v1=c2_center_to_end, v2=c2_normal_vector
            )

            total_distance = (
                self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
                + self._compute_arc_length(angle_rad=angle_c3)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Right by: {angle_c1}
            #       2. Left by: {angle_c3}
            #       3. Right by: {angle_c2}
            #       """)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.right,
                start_position=src,
                end_position=Position(
                    x=c1_end[0],
                    y=c1_end[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c3),
                turning_radian=angle_c3,
                direction=Direction.left,
                start_position=Position(
                    x=c1_end[0],
                    y=c1_end[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_start[0],
                    y=c2_start[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=c3_center[0], y=c3_center[1], locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            right_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.right,
                start_position=Position(
                    x=c2_start[0],
                    y=c2_start[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_2)

        elif move_index == 6:
            if distance < CAR_TURNING_RADIUS * 2:
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = CAR_TURNING_RADIUS
            h_length = distance / 2
            anticlockwise_rotation_radians = self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=anticlockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c1_tangent_point = (
                    np.array([src_circle_x, src_circle_y])
                    + CAR_TURNING_RADIUS * c1_normal_vector
            )
            c2_tangent_point = (
                    np.array([dest_circle_x, dest_circle_y])
                    - CAR_TURNING_RADIUS * c1_normal_vector
            )

            straight_line_vector = c2_tangent_point - c1_tangent_point
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(straight_line_vector)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = 2 * math.pi - self._angle_between_vectors(c1_normal_vector, c1_to_src_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                c1_normal_vector * -1, c2_to_dest_vector
            )

            total_distance = (
                    straighline_distance
                    + self._compute_arc_length(angle_rad=angle_c1)
                    + self._compute_arc_length(angle_rad=angle_c2)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Right by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Left by: {angle_c2}
            #       """)

            right_turn_1 = Movement(
                distance_cm=-self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.right,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            left_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.left,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)
        elif move_index == 7:
            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            v1_normal = np.array([-v1[1], v1[0]])

            v1_normal = self._normalize_vector(vector=v1_normal)

            c1_tangent_point = (
                    np.array([src_circle_x, src_circle_y]) + CAR_TURNING_RADIUS * v1_normal
            )
            c2_tangent_point = c1_tangent_point + v1
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(v1)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = 2 * math.pi - self._angle_between_vectors(v1_normal, c1_to_src_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(c2_to_dest_vector, v1_normal)

            total_distance = (
                    straighline_distance
                    + self._compute_arc_length(angle_rad=angle_c1)
                    + self._compute_arc_length(angle_rad=angle_c2)
            )

            # #print(f"""
            #       Travel total: {total_distance}
            #       1. Right by: {angle_c1}
            #       2. Straight by: {straighline_distance}
            #       3. Right by: {angle_c2}
            #       """)

            right_turn_1 = Movement(
                distance_cm=-self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.right,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            right_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.right,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_2)
        elif move_index == 8:
            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            v1_normal = np.array([v1[1], -v1[0]])

            v1_normal = self._normalize_vector(v1_normal)

            c1_tangent_point = (
                    np.array([src_circle_x, src_circle_y]) + CAR_TURNING_RADIUS * v1_normal
            )
            c2_tangent_point = c1_tangent_point + v1
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(v1)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = 2 * math.pi - self._angle_between_vectors(c1_to_src_vector, v1_normal)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(v1_normal, c2_to_dest_vector)

            total_distance = (
                    straighline_distance
                    + self._compute_arc_length(angle_rad=angle_c1)
                    + self._compute_arc_length(angle_rad=angle_c2)
            )

            left_turn_1 = Movement(
                distance_cm=-self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.left,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            left_turn_2 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.left,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_2)
        elif move_index == 9:
            if distance < CAR_TURNING_RADIUS * 2:
                # #print("Edge Case: Distance cannot be less than 2 * r")
                return total_distance, moves_to_make

            v1 = np.array([dest_circle_x - src_circle_x, dest_circle_y - src_circle_y])
            a_length = CAR_TURNING_RADIUS
            h_length = distance / 2
            anticlockwise_rotation_radians = -self._compute_arccos(a_length / h_length)

            c1_normal_vector = self._rotate_vector(
                vector=v1, radians=anticlockwise_rotation_radians
            )
            c1_normal_vector = self._normalize_vector(vector=c1_normal_vector)

            c1_tangent_point = (
                np.array([src_circle_x, src_circle_y])
                + CAR_TURNING_RADIUS * c1_normal_vector
            )
            c2_tangent_point = (
                np.array([dest_circle_x, dest_circle_y])
                - CAR_TURNING_RADIUS * c1_normal_vector
            )

            straight_line_vector = c2_tangent_point - c1_tangent_point
            straighline_distance, straight_line_angle_of_travel = (
                self._vector_properties(straight_line_vector)
            )

            c1_to_src_vector = np.array([src.x - src_circle_x, src.y - src_circle_y])
            angle_c1 = 2 * math.pi -  self._angle_between_vectors(c1_to_src_vector, c1_normal_vector)

            c2_to_dest_vector = np.array(
                [dest.x - dest_circle_x, dest.y - dest_circle_y]
            )
            angle_c2 = self._angle_between_vectors(
                c2_to_dest_vector, c1_normal_vector * -1
            )

            total_distance = (
                straighline_distance
                + self._compute_arc_length(angle_rad=angle_c1)
                + self._compute_arc_length(angle_rad=angle_c2)
            )

            left_turn_1 = Movement(
                distance_cm=-self._compute_arc_length(angle_rad=angle_c1),
                turning_radian=angle_c1,
                direction=Direction.left,
                start_position=src,
                end_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                circle_center=Position(
                    x=src_circle_x, y=src_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(left_turn_1)

            straight_1 = Movement(
                distance_cm=straighline_distance,
                turning_radian=0,
                direction=Direction.straight,
                start_position=Position(
                    x=c1_tangent_point[0],
                    y=c1_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
            )
            moves_to_make.append(straight_1)

            right_turn_1 = Movement(
                distance_cm=self._compute_arc_length(angle_rad=angle_c2),
                turning_radian=angle_c2,
                direction=Direction.right,
                start_position=Position(
                    x=c2_tangent_point[0],
                    y=c2_tangent_point[1],
                    locationType=LocationType.empty,
                ),
                end_position=dest,
                circle_center=Position(
                    x=dest_circle_x, y=dest_circle_y, locationType=LocationType.empty
                ),
            )
            moves_to_make.append(right_turn_1)
        # #print(f"{move_index=}")
        if self.is_safe_movement(moves_to_make) == False:
            total_distance = math.inf
        return total_distance, moves_to_make

    def _map_obstacle_to_actual_location(self, pos: Position):
        # x = (pos.x + 0.5) * GRID_SIZE
        # y = (pos.y + 0.5) * GRID_SIZE
        if pos.facing == Facing.east:
            x = (pos.x + 0.5) * GRID_SIZE - self.landing_supplement
            y = (pos.y + 0.5) * GRID_SIZE
        elif pos.facing == Facing.north:
            x = (pos.x + 0.5) * GRID_SIZE
            y = (pos.y+ 0.5) * GRID_SIZE - self.landing_supplement
        elif pos.facing == Facing.south:
            x = (pos.x + 0.5) * GRID_SIZE
            y = (pos.y + 0.5) * GRID_SIZE + self.landing_supplement
        elif pos.facing == Facing.west:
            x = (pos.x + 0.5) * GRID_SIZE + self.landing_supplement
            y = (pos.y + 0.5) * GRID_SIZE
        new_pos = Position(
            x=x,
            y=y,
            locationType=pos.locationType,
            facing=pos.facing,
        )
        return new_pos

    def _plan_landing_zones(self):
        for y in range(GRID_COUNT):
            for x in range(GRID_COUNT):
                position = self.game.arena[y][x]
                if position.locationType == LocationType.obstacle:

                    if position.facing == Facing.east:
                        self.game.arena[y][
                            x + LANDING_DISTANCE
                        ].locationType = LocationType.landing
                        self.game.arena[y][x + LANDING_DISTANCE].facing = Facing.west
                        self.game.arena[y][
                            x + LANDING_DISTANCE
                        ].result = position.result
                        self.game.arena[y][
                            x + LANDING_DISTANCE
                            ].id = position.id

                        new_goal = self._map_obstacle_to_actual_location(
                                self.game.arena[y][x + LANDING_DISTANCE]
                            )



                    elif position.facing == Facing.north:

                        self.game.arena[y + LANDING_DISTANCE][
                            x
                        ].locationType = LocationType.landing
                        self.game.arena[y + LANDING_DISTANCE][x].facing = Facing.south
                        self.game.arena[y + LANDING_DISTANCE][
                            x
                        ].result = position.result
                        self.game.arena[y + LANDING_DISTANCE][
                            x
                        ].id = position.id

                        new_goal=    self._map_obstacle_to_actual_location(
                                self.game.arena[y + LANDING_DISTANCE][x]
                            )


                    elif position.facing == Facing.west:

                        self.game.arena[y][
                            x - LANDING_DISTANCE
                        ].locationType = LocationType.landing
                        self.game.arena[y][x - LANDING_DISTANCE].facing = Facing.east
                        self.game.arena[y][
                            x - LANDING_DISTANCE
                        ].result = position.result
                        self.game.arena[y][
                            x - LANDING_DISTANCE
                            ].id = position.id
                        new_goal = self._map_obstacle_to_actual_location(
                                self.game.arena[y][x - LANDING_DISTANCE]
                            )


                    else:

                        self.game.arena[y - LANDING_DISTANCE][
                            x
                        ].locationType = LocationType.landing
                        self.game.arena[y - LANDING_DISTANCE][x].facing = Facing.north
                        self.game.arena[y - LANDING_DISTANCE][
                            x
                        ].result = position.result
                        self.game.arena[y - LANDING_DISTANCE][
                            x
                        ].id = position.id
                        new_goal = self._map_obstacle_to_actual_location(
                                self.game.arena[y - LANDING_DISTANCE][x]
                            )


                    self.goals.append(
                        new_goal
                    )
                    self.goals_to_id_mapping[len(self.goals_to_id_mapping.keys())] = position.id


        self.shortest_distance_matrix = [
            [math.inf for b in range(len(self.goals) + 1)]
            for a in range(len(self.goals) + 1)
        ]
        print(self.goals)
    # def _get_source_cirle_position(self, position: Position):

    def _get_circle_position(self, position: Position, move: Direction):
        x = position.x
        y = position.y
        if position.facing == Facing.east:
            if move == Direction.left or move == Direction.reverse_left:
                return x, y + CAR_TURNING_RADIUS
            elif move == Direction.right or move == Direction.reverse_right:
                return x, y - CAR_TURNING_RADIUS
        elif position.facing == Facing.north:
            if move == Direction.left or move == Direction.reverse_left:
                return x - CAR_TURNING_RADIUS, y
            elif move == Direction.right or move == Direction.reverse_right:
                return x + CAR_TURNING_RADIUS, y
        elif position.facing == Facing.west:
            if move == Direction.left or move == Direction.reverse_left:
                return x, y - CAR_TURNING_RADIUS
            elif move == Direction.right or move == Direction.reverse_right:
                return x, y + CAR_TURNING_RADIUS
        elif position.facing == Facing.south:
            if move == Direction.left or move == Direction.reverse_left:
                return x + CAR_TURNING_RADIUS, y
            elif move == Direction.right or move == Direction.reverse_right:
                return x - CAR_TURNING_RADIUS, y

        # #print(f"Error when getting circle position for {position} direction: {move}")
        return None, None

    def _let_salesman_travel(self):

        def is_home(pos: Position):
            return pos.x == CAR_X_START_POS and pos.y == CAR_Y_START_POS

        def recursion(
            obstacles_explored: List[int],
            total_cost_incurred: float,
            current_obstacle_id: int,
            moves: List[int],
        ):
            copy_moves = moves[:]
            copy_moves.append(current_obstacle_id)

            if len(obstacles_explored) == len(self.goals) - 1:
                # moves.append(len(self.shortest_distance_matrix) - 1)
                return (
                    total_cost_incurred,
                    copy_moves,
                )

            shortest_distance = math.inf
            min_moves = None

            for index in range(len(self.goals)):

                # if is_home(pos=obstacle):
                #     continue

                if (
                    index == len(self.goals) - 1 or index in obstacles_explored
                ):  ## Home or obstacle has already been explored
                    continue

                copy_obstacles_explored = obstacles_explored[:]
                copy_obstacles_explored.append(index)
                copy_distance = (
                    total_cost_incurred
                    + self.shortest_distance_matrix[current_obstacle_id][index].distance
                )
                working_distance, working_moves = recursion(
                    obstacles_explored=copy_obstacles_explored,
                    total_cost_incurred=copy_distance,
                    current_obstacle_id=index,
                    moves=copy_moves,
                )

                if working_distance < shortest_distance:
                    shortest_distance = working_distance
                    min_moves = working_moves

                # if len(obstacles_explored) == 0:
                #     print(f"Distance: {working_distance} Series: {working_moves}")

            return shortest_distance, min_moves

        shortest_distance, min_moves = recursion(
            obstacles_explored=[],
            total_cost_incurred=0,
            current_obstacle_id=len(self.goals) - 1,
            moves=[],
        )
        # print(shortest_distance, min_moves)

        if min_moves is None:
            # self.sale_path = None
            # self.go
            # self.game = None
            self._initialize()
            return

        movement_seq = []
        movement_string = []
        for src_index in range(len(min_moves) - 1):
            dest_index = (src_index + 1) % len(min_moves)
            y = min_moves[src_index]
            x = min_moves[dest_index]


            movement_seq += self.shortest_distance_matrix[y][x].movements_to_take
            movement_string += self.convert_to_command(self.shortest_distance_matrix[y][x].movements_to_take, self.goals_to_id_mapping[x])
            # movement_seq.append(
            #     Movement(
            #         distance_cm=0,
            #         turning_radian=0,
            #         direction=Direction.straight,
            #         start_position=Position(
            #             x=-1, y=-1, locationType=LocationType.empty
            #         ),
            #         end_position=Position(x=-1, y=-1, locationType=LocationType.empty),
            #     )
            # )
        # print(self.convert_to_command(movement_seq))

        self.sale_path = TravelledSalesman(
            total_distance=shortest_distance,
            obstacle_seq=min_moves,
            movement_path=movement_seq,
            movement_string=movement_string,
        )
        # self.string_solution = self.convert_to_command(movement_seq)

    def convert_to_array(self, val):
        return np.array([val.x, val.y], dtype=int)
    def closest_distance(self, start1, end1, start2, end2):

        p1 = self.convert_to_array(start1)
        p2 = self.convert_to_array(end1)
        p3 = self.convert_to_array(start2)
        p4 = self.convert_to_array(end2)

        d1 = p2 - p1  # Direction vector of line segment 1
        d2 = p4 - p3  # Direction vector of line segment 2
        r = p1 - p3

        a = np.dot(d1, d1)  # Length squared of segment 1
        b = np.dot(d1, d2)  # Dot product of the direction vectors
        c = np.dot(d2, d2)  # Length squared of segment 2
        e = np.dot(r, d1)  # Projection of r onto d1
        f = np.dot(r, d2)  # Projection of r onto d2

        # Solve for s and t
        denominator = a * c - b * b
        if denominator == 0:  # Parallel lines
            # Handle parallel case by finding distance to endpoints
            return np.min([
                np.linalg.norm(p1 - p3),
                np.linalg.norm(p1 - p4),
                np.linalg.norm(p2 - p3),
                np.linalg.norm(p2 - p4),
            ])

        # Calculate parameter values for the closest points
        s_numer = b * f - c * e
        t_numer = a * f - b * e

        s = s_numer / denominator
        t = t_numer / denominator

        # Check if the segments intersect
        if 0 <= s <= 1 and 0 <= t <= 1:
            return 0.0  # Segments intersect

        # Clamp the values of s and t to the range [0, 1]
        s = np.clip(s, 0, 1)
        t = np.clip(t, 0, 1)

        # Calculate the closest points
        closest_point1 = p1 + s * d1
        closest_point2 = p3 + t * d2

        # Return the distance between the closest points
        return np.linalg.norm(closest_point1 - closest_point2)

    def closest_distance_point_to_line(self, start, end, point):
        p1 = self.convert_to_array(start)
        p2 = self.convert_to_array(end)
        p = np.array([point.x * GRID_SIZE + GRID_SIZE // 2, point.y * GRID_SIZE + GRID_SIZE // 2], dtype=int)
        line_vector = p2 - p1  # Direction vector of the line segment
        point_vector = p - p1  # Vector from the start of the line segment to the point

        line_length_squared = np.dot(line_vector, line_vector)

        if line_length_squared == 0:  # The segment is just a point
            return np.linalg.norm(p - p1)

        # Projection factor
        t = np.dot(point_vector, line_vector) / line_length_squared
        t = np.clip(t, 0, 1)  # Clamp to the range [0, 1]

        # Find the closest point on the line segment
        closest_point = p1 + t * line_vector

        # Return the distance from the point to the closest point on the segment
        return np.linalg.norm(p - closest_point)

    def check_straight_movement(self, movement: Movement):
        start = movement.start_position
        end = movement.end_position


        for edge in self.edges:
            distance = self.closest_distance(start, end, edge[0], edge[1])
            if distance < self.safety_distance_edge:
                return False

        for obstacle in self.obstacle:
            distance = self.closest_distance_point_to_line(start, end, obstacle)
            if distance < self.safety_distance_obstacle:
                return False
        return True

    def check_turn_movement(self, movement: Movement):
        def calculate_angle(p1, p2):
            p1 = self.convert_to_array(p1)
            p2 = self.convert_to_array(p2)
            delta_x = p2[0] - p1[0]
            delta_y = p2[1] - p1[1]
            angle = np.arctan2(delta_y, delta_x)
            if angle < 0:
                angle += 2 * np.pi

            return angle

        def calculate_distance(p1, p2):
            p1 = self.convert_to_array(p1)
            p2 = self.convert_to_array(p2)

            distance = np.linalg.norm(p2 - p1)

            return distance

        def closest_point_on_segment(point, start, end):
            point = self.convert_to_array(point)
            start =  self.convert_to_array(start)
            end =  self.convert_to_array(end)
            segment = end - start
            segment_length_squared = np.dot(segment, segment)
            if segment_length_squared == 0:
                return start
            t = np.dot(point - start, segment) / segment_length_squared
            t = np.clip(t, 0, 1)
            closest_point = start + t * segment

            return closest_point

        def modulo_angle(angle):
            return angle % (2 * np.pi)

        for obstacle in self.obstacle:
            pos = Position(x=obstacle.x * GRID_SIZE + GRID_SIZE // 2, y=obstacle.y * GRID_SIZE + GRID_SIZE // 2, locationType=LocationType.empty)
            angle = calculate_angle(movement.circle_center, pos)
            start_angle = calculate_angle(movement.circle_center, movement.start_position)
            end_angle = calculate_angle(movement.circle_center, movement.end_position)

            if (movement.direction == Direction.left and movement.distance_cm > 0) or (movement.direction == Direction.right and movement.distance_cm <= 0):

                start_angle = modulo_angle(start_angle - ANGLE_SUPPLEMENT)
                end_angle = modulo_angle(end_angle + ANGLE_SUPPLEMENT)

                # if movement.start_position.x >= 77 and movement.start_position.x <= 78 and obstacle.id == 2:
                #     print(movement.circle_center, movement.start_position)
                #     print(movement.circle_center, movement.end_position)
                #     print(pos)
                #     print(f"Distance: {movement.distance_cm} cm")
                #     print(f"Start angle: {start_angle}")
                #     print(f"End angle: {end_angle}")
                #     print(angle)
                #     print((start_angle < end_angle and angle >= start_angle and angle <= end_angle) or (start_angle > end_angle and (angle >= start_angle or angle <= end_angle)))
                if (start_angle < end_angle and angle >= start_angle and angle <= end_angle) or (start_angle > end_angle and (angle >= start_angle or angle <= end_angle)):
                    distance = calculate_distance(movement.circle_center, pos)
                    if distance < self.safety_distance_turning_obstacle:
                        return False

            elif (movement.direction == Direction.right and movement.distance_cm > 0) or (movement.direction == Direction.left and movement.distance_cm <= 0):
                start_angle = modulo_angle(start_angle + ANGLE_SUPPLEMENT)
                end_angle = modulo_angle(end_angle - ANGLE_SUPPLEMENT)
                # print(angle,start_angle, end_angle)
                if (start_angle > end_angle and angle <= start_angle and angle >= end_angle) or (start_angle < end_angle and (angle <= start_angle or angle >= end_angle)):
                    distance = calculate_distance(movement.circle_center, pos)
                    # print(f"Distance: {distance}")
                    if distance < self.safety_distance_turning_obstacle:
                        return False

        # COMMENT THIS OUT IF CRASH
        if self.check_edge:
            for edge in self.edges:
                closest_point = closest_point_on_segment(movement.circle_center, edge[0], edge[1])
                closest_point = Position(x=closest_point[0], y=closest_point[1], locationType=LocationType.empty)
                distance = calculate_distance(closest_point, movement.circle_center)
                if distance < self.safety_distance_turning_edge:
                    return False



        return True
    def is_safe_movement(self, moves_to_make: List[Movement]):
        for move in moves_to_make:
            try:
                if move is None:
                    return False
                # print(f"{move=}")
                if move.start_position.x == CAR_X_START_POS and move.start_position.y == CAR_Y_START_POS:
                    continue
                if move.turning_radian != 0:
                    # print(f"Handling turn: {move}")
                    if self.check_turn_movement(move) is False:
                        return False
                if move.turning_radian == 0:
                    # print(f"Handle straight: {move}")
                    if self.check_straight_movement(move) is False:
                        return False
            except:
                return False
        return True


    def convert_to_command(self, movement_seq, dest):
        command_dict = {
            "straight": "S",
            "right": "R",
            "left": "L",
            "forward": "F",
            "backward": "B",
            "reset": "G",
        }

        def calculate_degree(distance):
            radian = distance / CAR_TURNING_RADIUS
            degree = radian * (180 / math.pi)
            return degree

        command_list = [f"{MOVING_TAG}{dest}"]

        for move in movement_seq:

            position_update = {}
            position_update["car_position"] = {"x": move.end_position.x,
                                               "y": move.end_position.y,
                                               "dir": move.end_position.facing.value}
            if move.distance_cm == 0:
                continue

            if move.start_position.x == -1:
                command = "G"
            else:
                distance = move.distance_cm
                backwards = False
                if distance < 0:
                    backwards = True
                    distance = -distance

                direction = move.direction
                if direction == Direction.right:
                    degree = calculate_degree(distance)
                    formatted_degree = f"{int(degree):03d}"
                    command = "R" + formatted_degree
                elif direction == Direction.straight:
                    formatted_distance = f"{int(distance):03d}"
                    command = "S" + formatted_distance
                elif direction == Direction.left:
                    degree = calculate_degree(distance)
                    formatted_degree = f"{int(degree):03d}"
                    command = "L" + formatted_degree

                if backwards:
                    command = command[:1] + "B" + command[1:]
                else:
                    command = command[:1] + "F" + command[1:]
            position_update['command'] = command
            command_list.append(position_update)

        command_list.append("--scan image--")

        
        return command_list






