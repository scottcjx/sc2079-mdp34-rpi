from ObjectTypes.object_types import *
import math
import random
import asyncio
from queue import Queue
from collections import deque
from fastapi import BackgroundTasks
import time
import json
import os
import cv2
import numpy as np
from PathFinding_task1.game_solver import GameSolverTask1
from PathFinding_task1.visualiser import Visualiser
from PathFinding_task1.constants import *
from PathFinding_task2.constants import RCHED_LOC_TAG


def stitch_images(folder_path='./result_pics', output_name='STITCHED', images_per_row=3):
    images = []

    # Load all images from the specified folder
    for filename in os.listdir(folder_path):
        if filename.split('.')[0] == output_name:
            continue
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is not None:
                images.append(img)

    if not images:
        print("No images found in the specified folder.")
        return

    # Calculate grid dimensions
    num_images = len(images)
    if num_images < images_per_row:
        images_per_row = num_images
    rows = math.ceil(num_images / images_per_row)

    # Resize images to the same size (optional, but recommended for a grid)
    # height, width, _ = images[0].shape
    # resized_images = [cv2.resize(img, (width, height)) for img in images]

    # Create a blank canvas for the grid
    stitched_image = []

    # Create a blank image for padding
    padding_image = np.zeros(images[0].shape, dtype=np.uint8)

    for i in range(rows):
        row_images = images[i * images_per_row:(i + 1) * images_per_row]

        # Pad the last row if it has fewer images
        while len(row_images) < images_per_row:
            row_images.append(padding_image)

        stitched_row = cv2.hconcat(row_images)
        stitched_image.append(stitched_row)

    # Concatenate all rows vertically
    final_stitched_image = cv2.vconcat(stitched_image)

    # Save the stitched image
    output_image_path = os.path.join(folder_path, output_name + '.jpg')
    cv2.imwrite(output_image_path, final_stitched_image)
    print(f"[PC] DATA_MANAGER.PY: Stitched image saved at: {output_image_path}")

    return


class DataManager:
    def __init__(self):
        self.visualiser = Visualiser()
        self.gametask1 = None
        self.gameobstaclescanning = None
        self.gameobstaclescanning_index = 0
        self.session_mode = None
        self.create_empty_gameobstaclescanning()
        self.websocket_manager = None
        self.image_id_queue = deque([], maxlen=5)
        self.counter = []
        self.task1_string_solution = None
        self.task1_index = 0
        self.sale_path = None
        self.obstacle_index = 0
        self.task1_target_id = None
        self.prev_image_update = None

        self.task2_manager = None
        self.task2_queue = []
        self.task2progress = Task2Progress.car_initial_parked
        self.obstacle1_distance_from_parking = None
        self.obstacle2_distance_from_obstacle1 = None
        self.obstacle2_width = None
        self.obstacle1_arrow = ArrowDirection.none
        self.obstacle2_arrow = ArrowDirection.none
        self.car_asked_for_next_move = False

    def set_websocket_manager(self, websocket_manager):
        self.websocket_manager = websocket_manager

    def check_if_all_same(self):
        target = None

        # print(self.image_id_queue)
        if len(self.image_id_queue) != 5:
            return False

        for item in self.image_id_queue:
            if target is None:
                target = item
            elif target != item:
                return False
        return True

    def create_empty_gameobstaclescanning(self):
        car = Car(
            current_position=Position(
                y=10,
                x=100,
                locationType=LocationType.empty,
                facing=Facing.north,
                result="Home",
            ),
            facing_radian=math.pi / 2,
        )
        obstacle_pos = Position(
            x=0,
            y=0,
            locationType=LocationType.obstacle,
            facing=Facing(value=random.randint(0, 3)),
            result="None",
        )
        self.gameobstaclescanning = GameObstacleScanning(
            obstacle_position=obstacle_pos, car=car
        )

    def update_mode(self, new_mode: SessionMode):
        print(f"Data Manager mode: {new_mode}")
        self.session_mode = new_mode
        if self.session_mode == SessionMode.task2:
            self.send_message_sync(str('TTTTT'), WebsocketMessageType.stm_instr_set)

    def update_id(self, image_id):
        if self.session_mode is None:
            raise Exception("Session mode not set")
        elif self.session_mode == SessionMode.obstacle_scanning:

            self.image_id_queue.append(image_id)

            if self.check_if_all_same():
                print(f"ID has been updated {image_id}")
                self.gameobstaclescanning.obstacle_position.result = str(image_id)
                return True

        elif self.session_mode == SessionMode.task1:
            if self.task1_target_id is None:
                print(f"[PC] DATA_MANAGER.PY: Inferred {image_id} but no target id")
                return False

            self.image_id_queue.append(image_id)

            if not self.check_if_all_same():
                # print(self.image_id_queue)
                return False

            for row in self.gametask1.arena:
                for pos in row:
                    if pos.id == self.task1_target_id:
                        pos.result = str(image_id)
                        # print(f"Updated {pos.id} to {image_id}")
                        temp = f'{pos.id}->{image_id}'
                        if self.prev_image_update == temp:
                            pass
                        else:
                            self.prev_image_update = temp
                            self.send_message_sync(f"{pos.id}->{image_id}", WebsocketMessageType.obstacle_result)
                        return True

        elif self.session_mode == SessionMode.task2:
            self.image_id_queue.append(image_id)
            if self.check_if_all_same():
                return True
        return False

    async def send_message_async(self, res_str, message_type):
        # from ComputerServer.initializer import websocket_manager
        print("[PC to RPI] Websocket Sending: ", res_str)
        message = WebsocketMessage(message_type=message_type, value=str(res_str))
        if self.websocket_manager is None:
            print("Websocket is None")
            return
        await self.websocket_manager.send_message(message=message)

    def send_message_sync(self, res_str, message_type):
        try:
            loop = asyncio.get_event_loop()
            loop_bool = loop.is_running()
        except:
            # print("[PC] DATA_MANAGER.PY: loop failed")
            loop_bool = False
            pass
        if loop_bool:
            loop.create_task(self.send_message_async(res_str, message_type))
        else:
            asyncio.run(self.send_message_async(res_str, message_type))

    def update_obstaclescanning_reached_obstacle(self, fromRPI=False):
        if self.session_mode == SessionMode.obstacle_scanning:
            if (
                self.gameobstaclescanning_index
                >= len(self.gameobstaclescanning.solution_str)
                or self.gameobstaclescanning.obstacle_position.result != "No result"
            ):
                print(self.gameobstaclescanning.obstacle_position.result)
                self.gameobstaclescanning_index = 0
                return
            res = self.gameobstaclescanning.solution_str[
                self.gameobstaclescanning_index
            ]
            self.gameobstaclescanning_index += 1
            self.send_message_sync(res, WebsocketMessageType.stm_instr_set)

        elif self.session_mode == SessionMode.task1:
            # if len(self.task1_string_solution) - 1== 0:
            #     stitch_images('./result_pics/task1')

            if self.task1_index >= len(self.task1_string_solution):
                print("[PC] DATA_MANAGER.PY: Done With Task 1")
                self.task1_index = 0
                stitch_images('./result_pics/task1')
                return

            res = str(self.task1_string_solution[self.task1_index])
            if res.startswith(MOVING_TAG):
                if self.task1_index != 0:
                    time.sleep(2)
                self.task1_target_id = int(res.strip(MOVING_TAG))
                self.image_id_queue.clear()
                self.task1_index += 1
                res = str(self.task1_string_solution[self.task1_index])
            self.task1_index += 1
            self.send_message_sync(res, WebsocketMessageType.stm_instr_set)
        # return res

        elif self.session_mode == SessionMode.task2:
            if len(self.task2_queue) > 0 and self.task2_queue[0].startswith(RCHED_LOC_TAG):
                status = self.task2_queue.pop(0).strip(RCHED_LOC_TAG)
                self.task2progress = Task2Progress(value=int(status))
                # if self.task2progress == Task2Progress.next_to_obstacle_1:
                #     self.send_message_sync("TTTTT", WebsocketMessageType.stm_instr_set)
                #     pass
                if self.task2progress == Task2Progress.parking_car:
                    stitch_images('./result_pics/task2')
            # while len(self.task2_queue) == 0:
            #     pass

            if len(self.task2_queue) <= 0:
                self.car_asked_for_next_move = True
                return
            res = self.task2_queue.pop(0)

            message = str({'command': res}).replace("'", '"')
            self.send_message_sync(message, WebsocketMessageType.stm_instr_set)

    def handle_ultrasonic(self, dist):
        if 'r' in dist:
            return
        dist = int(dist)
        if self.obstacle1_distance_from_parking is None:
            self.obstacle1_distance_from_parking = dist
        else:
            self.obstacle2_distance_from_obstacle1 = dist

        self.task2_manager.update_path()

    def add_task2_move(self, move: str):
        if len(self.task2_queue) > 0:
            last_item = self.task2_queue[-1]
            if last_item[:2] == move[:2]:
                distance = int(last_item[-3:]) + int(move[-3:])
                # if distance < 100:
                #     distance = f"0{distance}"
                last_item = f"{self.task2_queue[-1][:2]}{distance:03}"
                self.task2_queue[-1] = last_item
                return
        self.task2_queue.append(move)
        if self.car_asked_for_next_move:
            self.car_asked_for_next_move = False
            self.update_obstaclescanning_reached_obstacle()

    def create_game(self, obstacle_positions: str):
        self.session_mode = SessionMode.task1
        print(obstacle_positions)
        obstacle_positions = obstacle_positions.replace("'", '"')
        data = json.loads(obstacle_positions)
        positions = []
        car = Car(
            current_position=Position(
                y=CAR_Y_START_POS,
                x=CAR_X_START_POS,
                locationType=LocationType.empty,
                facing=Facing.north,
                result="Home",
            ),
            facing_radian=math.pi / 2,
        )

        arena = [
            [
                Position(x=b, y=a, locationType=LocationType.empty)
                for b in range(GRID_COUNT)
            ]
            for a in range(GRID_COUNT)
        ]

        for obstacle in data:
            # print(obstacle)
            facing = None
            if obstacle["dir"] == "N":
                facing = Facing.north
            elif obstacle["dir"] == "S":
                facing = Facing.south
            elif obstacle["dir"] == "W":
                facing = Facing.west
            else:
                facing = Facing.east
            x = int(obstacle["x"])
            y = int(obstacle["y"])
            id = int(obstacle["id"])
            print(id)
            arena[y][x].locationType = LocationType.obstacle
            arena[y][x].facing = facing
            arena[y][x].id = id

        game = GameTask1(arena=arena, car=car)
        self.gametask1 = game
        # print(game)
        self.solve_game_task1()

    def solve_game_task1(self):
        if self.gametask1 is None:
            print("WTF MAN")
            return

        game_solver = GameSolverTask1(game=self.gametask1)
        game, distance_matrix, sale_path, mapping = game_solver.solve()
        print(game)
        print(distance_matrix)
        print(sale_path.movement_string)
        print(mapping)
        self.sale_path = sale_path

        try:
            # self.visualiser.display_game(game=game, distance_matrix=distance_matrix, sale_path=sale_path, mapping=mapping)
            pass
        except:
            pass
        self.task1_string_solution = sale_path.movement_string
        self.task1_index = 0
        self.update_obstaclescanning_reached_obstacle()
