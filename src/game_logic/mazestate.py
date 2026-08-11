import sys

from src.player import Player
from src.rendering.visualizer import Visualizer
try:
    from mazegenerator import MazeGenerator
except Exception:
    print("Do a 'make install' first")
    sys.exit(0)
from src.objects.ghosts import Blinky, Pinky, Inky, Clyde


class MazeState(MazeGenerator):
    def __init__(self, size: tuple[int, int], seed) -> None:
        super().__init__(
            size=size,
            entry_cell=(size[0] // 2, size[1] // 2),
            seed=seed)
        self.pinky = Pinky(0, 0)
        self.blinky = Blinky(0, len(self._maze[0]) - 1)
        self.inky = Inky(len(self._maze) - 1, len(self._maze[0]) - 1)
        self.clyde = Clyde(len(self._maze) - 1, 0)
        ghost_colors = {ghost.__class__.__name__.lower(): ghost.color
                        for ghost in [self.pinky, self.blinky,
                                      self.inky, self.clyde]}
        self.vis = Visualizer(self._maze, ghost_colors)
        self.player = Player(self)
