from src.objects import Ghost
from src.player import Movement


class MazeState:
    def __init__(self, maze: list[list[int]], player: Movement,
                 ghosts: dict[str, Ghost]) -> None:
        self.maze = maze
        self.player = player
        self.pinky = ghosts["Pinky"]
        self.blinky = ghosts["Blinky"]
        self.inky = ghosts["Inky"]
        self.clyde = ghosts["Clyde"]
