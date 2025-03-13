import re
from PathFinding_task1.game_solver import GameSolverTask1
from PathFinding_task1.game_maker import GameMaker
from ObjectTypes.object_types import * 
from PathFinding_task1.constants import * 
import math 
import json

from PathFinding_task1.visualiser import Visualiser 

class AlgoMain:
    def __init__(self):
        self.gametask1 = None 
        self.sale_path = None 

    def main(self, obstacle_pos):
        print(obstacle_pos)
        obstacle_positions = obstacle_pos.replace("'", '"')
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
        commands = json.dumps(self.sale_path.movement_string, indent=4)
        return commands

    def solve_game_task1(self):
        if self.gametask1 is None:
            print("WTF MAN")
            return

        game_solver = GameSolverTask1(game=self.gametask1)
        game, distance_matrix, sale_path, mapping = game_solver.solve()
        # visualiser_manager = Visualiser()
        # visualiser_manager.display_game(game=game, distance_matrix=distance_matrix, sale_path=sale_path)
        print(game)
        print(distance_matrix)
        print(sale_path.movement_string)
        print(mapping)
        self.sale_path = sale_path


if __name__ == "__main__":
    game_maker = GameMaker()
    arena = game_maker.make_game()

    # map_str = "MAP=[[0,06,12,0],[1,10,11,2],[2,14,15,1]]"
    
    def print_obstacles(arena):
        obstacles = "MAP=["
        id = 0
        obstacle_list = []  # Store formatted obstacle strings

        for row in arena:
            for pos in row:
                if pos.locationType == LocationType.obstacle:
                    id_string = f"{id:02d},"  # Ensure ID is always 2 digits
                    x = f"{int(pos.x):02d},"  # Ensure X is 2 digits
                    y = f"{int(pos.y):02d},"  # Ensure Y is 2 digits
                    facing_map = {"north": 0, "south": 1, "east": 2, "west": 3}

                    f = str(facing_map.get(pos.facing.name, 3))  # Convert Facing to int

                    # Append correctly formatted obstacle
                    obstacle_list.append(f"[{id_string}{x}{y}{f}]")
                    id += 1

        obstacles += ",".join(obstacle_list)  # Join obstacles with commas
        obstacles += "]"

        print(obstacles)  # Debugging: Print properly formatted MAP string
        return obstacles

    
    def process_map_data(obstacles):
        """
        Process a map string in the format MAP=[[0,06,12,0],[1,10,19,2],[2,14,15,1]]
        
        Args:
            map_str (str): A string representing map data
        
        Returns:
            list: A list of dictionaries representing obstacle data
        """
        # Extract the map data using regex
        match = re.search(r'MAP=\[\[(.*?)\]\]', obstacles)
        if not match:
            raise ValueError("Invalid map string format")
        
        # Extracted content inside MAP=[[]]
        map_data_str = match.group(1)

        # Convert the string to a list of lists
        map_data = [item.strip().split(',') for item in map_data_str.split('],[')]

        # Convert to the required format
        processed_data = []
        facing_map = {0: 'N', 1: 'S', 2: 'E', 3: 'W'}

        for obstacle in map_data:
            processed_obstacle = {
                "dir": facing_map[int(obstacle[3])],  # Convert facing index to direction
                "x": int(obstacle[1]),  # Convert X coordinate
                "y": int(obstacle[2]),  # Convert Y coordinate
                "id": int(obstacle[0])  # Convert ID
            }
            processed_data.append(processed_obstacle)

        return processed_data
    
    
    map_string = print_obstacles(arena)
    # Process the map data
    processed_data = json.dumps(process_map_data(map_string))
    
    # Pretty print the processed data
    print(f"Processed Data: {processed_data}")

    algo_main = AlgoMain()
    try:
        commands = algo_main.main(processed_data)
        print(commands)
        print("hehe passed")
    except:
        print("failed")
