import sys

from src.player import Player
from src.rendering.visualizer import Visualizer
try:
    from mazegenerator import MazeGenerator
except Exception:
    print("Do a 'make install' first")
    sys.exit(0)
from src.objects.ghosts import Blinky, Pinky, Inky, Clyde
from src.objects.pacgums import Gummis
from src.parsing.parser import parsing


class MazeState(MazeGenerator):
    def __init__(self, size: tuple[int, int], maze_config) -> None:
        super().__init__(
            size = size,
            entry_cell = (size[0] // 2, size[1] // 2),
            seed = maze_config.seed)
        self.pinky = Pinky(0, 0)
        self.blinky = Blinky(0, len(self._maze[0]) - 1)
        self.inky = Inky(len(self._maze) - 1, len(self._maze[0]) - 1)
        self.clyde = Clyde(len(self._maze) - 1, 0)
        ghost_colors = {ghost.__class__.__name__: ghost.color
                        for ghost in [self.pinky, self.blinky,
                                      self.inky, self.clyde]}
        self.vis = Visualizer(self._maze, ghost_colors)
        self.player = Player(self)
        c, r = self.maze_entry
        self.gummis = Gummis(self._maze, (r, c), maze_config.pacgum)

        self.ghost_speed_factor: float = 1.0
        self.ghost_speed = int(self.player.speed * self.ghost_speed_factor)
        self.collision_threshhold = 12

    def handle_eaten_gums(self) -> None:
        if self.player.is_centered():
            if self.player.position in self.gummis.pacgums:
                self.gummis.pop_pacgum(self.player.position)
            elif self.player.position in self.gummis.superpacgums:
                self.gummis.pop_superpacgum(self.player.position)
                for ghost in (self.pinky, self.blinky, self.inky, self.clyde):
                    ghost.set_frightened_status(600)
            
