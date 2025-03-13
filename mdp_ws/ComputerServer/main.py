from PathFinding_task1.game_solver import GameSolverTask1
from ObjectTypes.object_types import * 
from PathFinding_task1.constants import * 
import math 
import json 

class AlgoMain:
    def __init__(self, obstacle_pos: str):
        self.gametask1 = None 
        self.sale_path = None 
        self.obstacle_pos = obstacle_pos

    def main(self):
        print(self.obstacle_pos)
        obstacle_positions = self.obstacle_pos.replace("'", '"')
        # obstacle_positions = self.obstacle_pos
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
        commands = json_dump(self.sale_path.movement_string, indent=4)
        return commands

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


if __name__ == "__main__":
    print("main")
    def convert_to_command(movement_seq, dest):
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
    
    movement_seq = [
                    Movement(distance_cm=20.0, turning_radian=2.3, direction=Direction.right, 
                             start_position=Position(x=15, y=20, locationType=LocationType.landing), end_position=Position(x=15, y=20, locationType=LocationType.landing))
                            ,
                    Movement(distance_cm=20.0, turning_radian=2.3, direction=Direction.right, 
                             start_position=Position(x=15, y=20, locationType=LocationType.landing), end_position=Position(x=15, y=20, locationType=LocationType.landing))
                    ]
    movement_string = [] 
    movement_string += convert_to_command(movement_seq, 1)
    movement_string += convert_to_command(movement_seq, 2)
    json_dump = json.dumps(movement_string, indent=4)
    print(json_dump)