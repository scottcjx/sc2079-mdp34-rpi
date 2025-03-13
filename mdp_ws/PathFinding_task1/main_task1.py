from game_maker import GameMaker
from visualiser import Visualiser
from game_solver import GameSolverTask1
from ObjectTypes.object_types import Position, LocationType, Facing



class Task1_Manager:
    def __init__(self):
        do_while_flage = 0
        while do_while_flage == 0:
            game = game_maker_manager.make_game()
            game_solver_manager = GameSolverTask1(game=game)
            game, distance_matrix, sale_path = game_solver_manager.solve()

            if game != None:
                do_while_flage = 1

        self.game = game
        self.distance_matrix = distance_matrix
        self.sale_path = sale_path


if __name__ == "__main__":
    game_maker_manager = GameMaker()
    visualiser_manager = Visualiser()

    # src = Position(x=100, y=0, locationType=LocationType.empty, facing=Facing.north)
    # dest = Position(x=0,y=100,locationType=LocationType.empty, facing=Facing.north)

    # src = Position(x=30, y=80, locationType=LocationType.empty, facing=Facing.west)
    # dest = Position(x=30,y=0,locationType=LocationType.empty, facing=Facing.east)

    # dest = Position(x=6, y=0, locationType=LocationType.empty, facing=Facing.east)
    # src = Position(x=0,y=100,locationType=LocationType.empty, facing=Facing.east)

    do_while_flage = 0
    while do_while_flage == 0:
        game = game_maker_manager.make_game()
        game_solver_manager = GameSolverTask1(game=game)
        game, distance_matrix, sale_path = game_solver_manager.solve()

        if game != None:
            do_while_flage = 1
    # game_solver_manager.solve_move_safe_path(move_index=2, src=src, dest=dest)
    visualiser_manager.display_game(game=game, distance_matrix=distance_matrix, sale_path=sale_path)
