import pygame
import math
from typing import List
import random
import numpy as np
from datetime import datetime, timedelta
import time

from ObjectTypes.object_types import (
    GameTask1,
    Position,
    LocationType,
    Facing,
    MinimumPath,
    Direction,
    Movement,
    TravelledSalesman,
)
from PathFinding_task1.constants import (
    WHITE,
    SCALE_FACTOR,
    START_BOX_SIZE,
    YELLOW,
    BLACK,
    GRID_COUNT,
    GRID_SIZE,
    RED,
    GREEN,
    BLUE1,
    CAR_SPEED,
    TURNING_RADIAN_INCREMENT,
    CAR_TURNING_RADIUS,
    RENDER_SPEED,
)

pygame.init()


class Visualiser:

    def __init__(self, width: int = 200, height: int = 200) -> None:
        self.width = width
        self.height = height
        self.display = pygame.display.set_mode(
            (self.width * SCALE_FACTOR, self.height * SCALE_FACTOR)
        )
        pygame.display.set_caption("Path Finding")
        self.car_image = pygame.image.load("car.png").convert_alpha()
        self.car_image = pygame.transform.scale(
            self.car_image, (15 * SCALE_FACTOR, 25 * SCALE_FACTOR)
        )
        self.colors = [self._random_color() for _ in range(10000)]
        self.font = pygame.font.Font(None, 4 * SCALE_FACTOR)

    def _random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def _display_vector(self, start_vector: Position, end_vector: Position, color):
        pygame.draw.line(
            self.display,
            color,
            (
                start_vector.x * SCALE_FACTOR,
                (self.width - start_vector.y) * SCALE_FACTOR,
            ),
            (end_vector.x * SCALE_FACTOR, (self.height - end_vector.y) * SCALE_FACTOR),
            width=3,
        )

    def _display_turn(self, movement: Movement, color):

        if movement.circle_center is None:
            return

        circle_center_to_start = [
            movement.start_position.x - movement.circle_center.x,
            movement.start_position.y - movement.circle_center.y,
        ]
        circle_center_to_end = [
            movement.end_position.x - movement.circle_center.x,
            movement.end_position.y - movement.circle_center.y,
        ]
        start_rad = np.arctan2(circle_center_to_start[1], circle_center_to_start[0]) % (
            2 * np.pi
        )
        end_rad = np.arctan2(circle_center_to_end[1], circle_center_to_end[0]) % (
            2 * np.pi
        )

        if (movement.direction == Direction.left and movement.distance_cm > 0) or (
            movement.direction == Direction.right and movement.distance_cm < 0
        ):
            rad_1 = start_rad
            rad_2 = end_rad
        else:
            rad_1 = end_rad
            rad_2 = start_rad

        pygame.draw.arc(
            self.display,
            color,
            pygame.Rect(
                (
                    movement.circle_center.x * SCALE_FACTOR
                    - CAR_TURNING_RADIUS * SCALE_FACTOR,
                    (self.height - movement.circle_center.y) * SCALE_FACTOR
                    - CAR_TURNING_RADIUS * SCALE_FACTOR,
                ),
                (
                    CAR_TURNING_RADIUS * SCALE_FACTOR * 2,
                    CAR_TURNING_RADIUS * SCALE_FACTOR * 2,
                ),
            ),
            rad_1,
            rad_2,
            CAR_TURNING_RADIUS * SCALE_FACTOR,
        )

    def _determine_car_position(
        self, sale_path: TravelledSalesman, distance_covered: float
    ):

        index = 0
        working_distance_covered = distance_covered
        while working_distance_covered > 0 and index < len(sale_path.movement_path):
            working_distance_covered -= abs(sale_path.movement_path[index].distance_cm)
            index += 1

        if index == len(sale_path.movement_path) and working_distance_covered > 0:
            self.running = False
        current_movement = sale_path.movement_path[index - 1]
        self._move_car(movement=current_movement)
        # print(f"Car is currently travelling {current_movement.direction}")

    def display_game_frame(
        self,
        distance_matrix: List[List[MinimumPath]],
        sale_path: TravelledSalesman,
    ):
        self.display.fill(WHITE)

        distance_covered = self.clock * CAR_SPEED
        self._determine_car_position(
            sale_path=sale_path, distance_covered=distance_covered
        )

        # print(time_since.seconds)
        ## Drawing Start Box
        pygame.draw.rect(
            self.display,
            YELLOW,
            pygame.Rect(
                0,
                (self.height - START_BOX_SIZE) * SCALE_FACTOR,
                START_BOX_SIZE * SCALE_FACTOR,
                START_BOX_SIZE * SCALE_FACTOR,
            ),
        )

        ## Drawing grid
        for i in range(GRID_COUNT):
            pygame.draw.line(
                self.display,
                BLACK,
                (0, i * GRID_SIZE * SCALE_FACTOR),
                (self.width * SCALE_FACTOR, i * GRID_SIZE * SCALE_FACTOR),
            )
            pygame.draw.line(
                self.display,
                BLACK,
                (i * GRID_SIZE * SCALE_FACTOR, 0),
                (i * GRID_SIZE * SCALE_FACTOR, self.height * SCALE_FACTOR),
            )

        seq_str = "5"
        for src_index in range(len(sale_path.obstacle_seq)):
            dest_index = (src_index + 1) % len(sale_path.obstacle_seq)
            y = sale_path.obstacle_seq[src_index]
            x = sale_path.obstacle_seq[dest_index]

            seq_str += f" -> {x}"
            if y == x:
                continue
            color = self.colors[y * GRID_COUNT + x]
            for path in distance_matrix[y][x].movements_to_take:
                start_pos = path.start_position
                end_pos = path.end_position
                movement_direction = path.direction

                if path.direction == Direction.straight:
                    self._display_vector(
                        start_vector=start_pos, end_vector=end_pos, color=color
                    )
                else:
                    self._display_turn(movement=path, color=color)
        for row in self.game.arena:
            for col in row:

                if col.locationType == LocationType.landing_padding:
                    # pygame.draw.rect(
                    #     self.display,
                    #     RED,
                    #     pygame.Rect(
                    #         (col.x * GRID_SIZE) * SCALE_FACTOR,
                    #         (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                    #         GRID_SIZE * SCALE_FACTOR,
                    #         GRID_SIZE * SCALE_FACTOR,
                    #     ),
                    # )
                    pass
                elif col.locationType == LocationType.obstacle:
                    pygame.draw.rect(
                        self.display,
                        BLUE1,
                        pygame.Rect(
                            (col.x * GRID_SIZE) * SCALE_FACTOR,
                            (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                            (GRID_SIZE) * SCALE_FACTOR,
                            (GRID_SIZE) * SCALE_FACTOR,
                        ),
                    )
                    text_surface = self.font.render(str(col.id), True, (255, 255, 255))
                    text_rect = text_surface.get_rect()
                    text_rect.center = (
                        (col.x * GRID_SIZE + GRID_SIZE / 2) * SCALE_FACTOR,
                        (self.height - (col.y + 1) * GRID_SIZE + GRID_SIZE / 2)
                        * SCALE_FACTOR,
                    )
                    self.display.blit(text_surface, text_rect)
                    if col.facing == Facing.east:
                        pygame.draw.rect(
                            self.display,
                            YELLOW,
                            pygame.Rect(
                                (col.x * GRID_SIZE + GRID_SIZE - 3) * SCALE_FACTOR,
                                (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                                (3) * SCALE_FACTOR,
                                (GRID_SIZE) * SCALE_FACTOR,
                            ),
                        )
                    elif col.facing == Facing.north:
                        pygame.draw.rect(
                            self.display,
                            YELLOW,
                            pygame.Rect(
                                (col.x * GRID_SIZE) * SCALE_FACTOR,
                                (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                                (GRID_SIZE) * SCALE_FACTOR,
                                (3) * SCALE_FACTOR,
                            ),
                        )
                    elif col.facing == Facing.west:
                        pygame.draw.rect(
                            self.display,
                            YELLOW,
                            pygame.Rect(
                                (col.x * GRID_SIZE) * SCALE_FACTOR,
                                (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                                (3) * SCALE_FACTOR,
                                (GRID_SIZE) * SCALE_FACTOR,
                            ),
                        )
                    elif col.facing == Facing.south:
                        pygame.draw.rect(
                            self.display,
                            YELLOW,
                            pygame.Rect(
                                (col.x * GRID_SIZE) * SCALE_FACTOR,
                                (self.height - (col.y + 1) * GRID_SIZE + GRID_SIZE - 3)
                                * SCALE_FACTOR,
                                (GRID_SIZE) * SCALE_FACTOR,
                                (3) * SCALE_FACTOR,
                            ),
                        )

                # elif col.locationType == LocationType.landing:
                #     color = GREEN
                #     pygame.draw.rect(
                #         self.display,
                #         color,
                #         pygame.Rect(
                #             (col.x * GRID_SIZE) * SCALE_FACTOR,
                #             (self.height - (col.y + 1) * GRID_SIZE) * SCALE_FACTOR,
                #             GRID_SIZE * SCALE_FACTOR,
                #             GRID_SIZE * SCALE_FACTOR,
                #         ),
                #     )
                #     text_surface = self.font.render(str(col.id), True, (0, 0, 0))
                #     text_rect = text_surface.get_rect()
                #     text_rect.center = (
                #         (col.x * GRID_SIZE + GRID_SIZE / 2) * SCALE_FACTOR,
                #         (self.height - (col.y + 1) * GRID_SIZE + GRID_SIZE / 2)
                #         * SCALE_FACTOR,
                #     )
                #     self.display.blit(text_surface, text_rect)

        rotated_image = pygame.transform.rotate(
            self.car_image, math.degrees(self.game.car.facing_radian - math.pi / 2)
        )
        # print(
        #     f"Car x: {self.game.car.current_position.x} Car y: {self.game.car.current_position.y}"
        # )
        rotated_rect = rotated_image.get_rect(
            center=(
                self.game.car.current_position.x * SCALE_FACTOR,
                (self.height - self.game.car.current_position.y) * SCALE_FACTOR,
            )
        )
        self.display.blit(rotated_image, rotated_rect.topleft)

        text_surface = self.font.render(str(seq_str), True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (100, 20)
        self.display.blit(text_surface, text_rect)

        pygame.display.update()  # Update the display after drawing
        self._increment_clock()

    def _increment_clock(self):
        time.sleep(RENDER_SPEED)
        self.clock += 1

    def _print_movement(self, movement: Movement):
        gear = "forward"
        if movement.distance_cm < 0:
            gear = "backward"
        print(f"Car moving {gear}, turning: {movement.direction.name} for distance: {movement.distance_cm} cm\tTurn by {movement.turning_radian}")

    def _move_car(self, movement: Movement):
        x = self.game.car.current_position.x
        y = self.game.car.current_position.y
        current_facing = self.game.car.facing_radian

        # self._print_movement(movement=movement)
        try:
            if movement.direction == Direction.straight and movement.distance_cm > 0:
                new_facing = self.game.car.facing_radian
                delta_x = np.cos(new_facing) * CAR_SPEED
                delta_y = np.sin(new_facing) * CAR_SPEED
                new_x = x + delta_x
                new_y = y + delta_y
            elif movement.direction == Direction.straight and movement.distance_cm < 0:
                new_facing = self.game.car.facing_radian
                delta_x = np.cos(new_facing) * CAR_SPEED
                delta_y = np.sin(new_facing) * CAR_SPEED
                new_x = x - delta_x
                new_y = y - delta_y
            elif movement.direction == Direction.left and movement.distance_cm > 0:
                new_facing = (current_facing + TURNING_RADIAN_INCREMENT) % (math.pi * 2)
                center_x = x - CAR_TURNING_RADIUS * np.sin(current_facing)
                center_y = y + CAR_TURNING_RADIUS * np.cos(current_facing)
                new_x = center_x + CAR_TURNING_RADIUS * np.sin(
                    current_facing + TURNING_RADIAN_INCREMENT
                )
                new_y = center_y - CAR_TURNING_RADIUS * np.cos(
                    current_facing + TURNING_RADIAN_INCREMENT
                )

            elif movement.direction == Direction.left and movement.distance_cm < 0:
                new_facing = (current_facing - TURNING_RADIAN_INCREMENT) % (math.pi * 2)
                center_x = x + CAR_TURNING_RADIUS * np.sin(current_facing)
                center_y = y - CAR_TURNING_RADIUS * np.cos(current_facing)
                new_x = center_x - CAR_TURNING_RADIUS * np.sin(
                    current_facing + TURNING_RADIAN_INCREMENT
                )
                new_y = center_y + CAR_TURNING_RADIUS * np.cos(
                    current_facing + TURNING_RADIAN_INCREMENT
                )

            elif movement.direction == Direction.right and movement.distance_cm > 0:
                new_facing = (current_facing - TURNING_RADIAN_INCREMENT) % (math.pi * 2)
                center_x = x + CAR_TURNING_RADIUS * np.sin(current_facing)
                center_y = y - CAR_TURNING_RADIUS * np.cos(current_facing)
                new_x = center_x - CAR_TURNING_RADIUS * np.sin(
                    current_facing - TURNING_RADIAN_INCREMENT
                )
                new_y = center_y + CAR_TURNING_RADIUS * np.cos(
                    current_facing - TURNING_RADIAN_INCREMENT
                )

            elif movement.direction == Direction.right and movement.distance_cm < 0:
                new_facing = (current_facing + TURNING_RADIAN_INCREMENT) % (math.pi * 2)
                center_x = x - CAR_TURNING_RADIUS * np.sin(current_facing)
                center_y = y + CAR_TURNING_RADIUS * np.cos(current_facing)
                new_x = center_x + CAR_TURNING_RADIUS * np.sin(
                    current_facing - TURNING_RADIAN_INCREMENT
                )
                new_y = center_y - CAR_TURNING_RADIUS * np.cos(
                    current_facing - TURNING_RADIAN_INCREMENT
                )

            self.game.car.current_position.x = new_x
            self.game.car.current_position.y = new_y
            self.game.car.facing_radian = new_facing
        except Exception as e:
            print(movement)

    def _print_movement_path(self, sale_path: TravelledSalesman):
        for move in sale_path.movement_path:
            print(f"Move {move.direction} in {move.distance_cm}cm")

    def display_game(
        self,
        game: GameTask1,
        distance_matrix: List[List[MinimumPath]],
        sale_path: TravelledSalesman,
            mapping: dict
    ):
        self.running = True
        self.clock = 0
        self.game = game
        self.mapping = mapping
        print("Starting pygame display")
        # self._print_movement_path(sale_path=sale_path)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.display_game_frame(
                distance_matrix=distance_matrix, sale_path=sale_path
            )

        pygame.quit()


# if __name__ == "__main__":
#     visualizer = Visualiser()
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False

#         visualizer.display_game()

#     pygame.quit()
