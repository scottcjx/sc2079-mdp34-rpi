from ObjectTypes.object_types import Position, Facing, LocationType, Car, GameTask1, Direction
from .constants import CAR_X_START_POS, CAR_Y_START_POS, OBSTACLE_COUNT, GRID_COUNT

import math
from typing import List, Type
import random
from pydantic import BaseModel
import json
from enum import Enum


class GameMaker:
    def __init__(self) -> None:
        self.car = Car(
            current_position=Position(
                y=CAR_Y_START_POS,
                x=CAR_X_START_POS,
                locationType=LocationType.empty,
                facing=Facing.north,
                result="Home",
            ),
            facing_radian=math.pi / 2,
        )

    def make_game(self):
        arena = [
            [
                Position(x=b, y=a, locationType=LocationType.empty)
                for b in range(GRID_COUNT)
            ]
            for a in range(GRID_COUNT)
        ]
        arena = self.randomly_place_obstacles(arena=arena)
        return arena
        # game = GameTask1(arena=arena, car=self.car)
        # return game

    def randomly_place_obstacles(self, arena: List[List[Position]]):
        obstacle_count = 0

        def check_possible_object_placement(
            x_potential: int, y_potential: int, facing_potential: Facing
        ) -> bool:
            nonlocal arena

            if facing_potential == Facing.east:
                if (
                    y_potential == 0
                    or y_potential == GRID_COUNT - 1
                    or x_potential > 15
                ):
                    return False
                for y in range(y_potential - 1, y_potential + 2):
                    for x in range(x_potential + 1, x_potential + 5):
                        if arena[y][x].locationType != LocationType.empty:
                            return False

            elif facing_potential == Facing.north:
                if (
                    x_potential == 0
                    or x_potential == GRID_COUNT - 1
                    or y_potential > 15
                ):
                    return False
                for y in range(y_potential + 1, y_potential + 5):
                    for x in range(x_potential - 1, x_potential + 2):
                        if arena[y][x].locationType != LocationType.empty:
                            return False

            elif facing_potential == Facing.west:
                if y_potential == 0 or y_potential == GRID_COUNT - 1 or x_potential < 4:
                    return False
                for y in range(y_potential - 1, y_potential + 2):
                    for x in range(x_potential - 4, x_potential):
                        if arena[y][x].locationType != LocationType.empty:
                            return False

            elif facing_potential == Facing.south:
                if x_potential == 0 or x_potential == GRID_COUNT - 1 or y_potential < 4:
                    return False
                for y in range(y_potential - 4, y_potential):
                    for x in range(x_potential - 1, x_potential + 2):
                        if arena[y][x].locationType != LocationType.empty:
                            return False

            return True

        while obstacle_count < OBSTACLE_COUNT:
            x_potential = random.randint(0, GRID_COUNT - 1)
            y_potential = random.randint(0, GRID_COUNT - 1)
            facing_potential = Facing(value=random.randint(0, 3))

            if x_potential < 5 and y_potential < 5:  ##In Start Box
                continue

            elif check_possible_object_placement(
                x_potential=x_potential,
                y_potential=y_potential,
                facing_potential=facing_potential,
            ):
                arena[y_potential][x_potential].locationType = LocationType.obstacle
                arena[y_potential][x_potential].facing = facing_potential
                arena[y_potential][x_potential].result = f"obstacle {obstacle_count}"
                obstacle_count += 1

        return arena


def save_pydantic_model_to_json(obj: BaseModel, file_path: str) -> None:
    def encode_enum(enum):
        if isinstance(enum, Enum):
            return enum.value
        raise TypeError(f"Object of type {type(enum)} is not serializable")

    def default_serializer(obj):
        if isinstance(obj, BaseModel):
            return obj.dict()
        if isinstance(obj, Enum):
            return encode_enum(obj)
        raise TypeError(f"Object of type {type(obj)} is not serializable")

    with open(file_path, "w") as file:
        json.dump(obj, file, default=default_serializer, indent=4)
