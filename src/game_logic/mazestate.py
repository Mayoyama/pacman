import sys
from typing import Any
from src.player import Player
from src.rendering.visualizer import Visualizer
try:
    from mazegenerator import MazeGenerator
except Exception:
    print("No import of mazegenerator known")
    sys.exit(0)
from src.objects.ghosts import Blinky, Pinky, Inky, Clyde
from src.objects.pacgums import Gummis
from .bonusstate import BonusState


class MazeState(MazeGenerator):
    def __init__(self, size: tuple[int, int], maze_config: Any,
                 screen_size: tuple[int, int],
                 bonuses: BonusState) -> None:
        super().__init__(
            size=size,
            entry_cell=(size[0] // 2, size[1] // 2),
            seed=maze_config.seed)
        self.bonuses = bonuses
        self.pinky = Pinky(0, 0)
        self.blinky = Blinky(0, len(self.maze[0]) - 1)
        self.inky = Inky(len(self.maze) - 1, len(self.maze[0]) - 1)
        self.clyde = Clyde(len(self.maze) - 1, 0)
        ghost_colors = {ghost.__class__.__name__: ghost.color
                        for ghost in [self.pinky, self.blinky,
                                      self.inky, self.clyde]}
        self.vis = Visualizer(self.maze, ghost_colors,
                              maze_config.highscore_filename,
                              screen_size)
        
        self.player = Player(self)
        c, r = self.maze_entry
        self.pacstart = (r, c)
        
        self.gummis = Gummis(self.maze, self.pacstart, maze_config.pacgum,
                             self.bonuses.max_gums)
        self.gum_point = maze_config.points_per_pacgum
        self.supergum_point = maze_config.points_per_super_pacgum
        self.ghost_speed_factor: float = 1.0
        self.ghost_speed = int(self.player.speed * self.ghost_speed_factor)
        self.collision_threshhold = 12

    def handle_eaten_gums(self) -> None:
        if self.player.is_centered():
            if self.player.position in self.gummis.pacgums:
                self.gummis.pop_pacgum(self.player.position)
                self.player._score += self.gum_point
            elif self.player.position in self.gummis.superpacgums:
                self.gummis.pop_superpacgum(self.player.position)
                self.player._score += self.supergum_point
                frightened_duration = 1200 if self.bonuses.ultragums else 600
                for ghost in (self.pinky, self.blinky, self.inky, self.clyde):
                    ghost.set_frightened_status(frightened_duration)
