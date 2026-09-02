import sys
import pygame
from typing import Any, TextIO
from src.player import Player
from src.rendering.visualizer import Visualizer
from src.objects.ghosts import Blinky, Pinky, Inky, Clyde
from src.objects.pacgums import Gummis
from .bonusstate import BonusState
from .entry_cell_adjuster import find_safe_entry_cell
import contextlib
try:
    from mazegenerator import MazeGenerator
except ImportError:
    print("STOP: No import of mazegenerator found", file=sys.stderr)
    sys.exit(0)


class _FilterStream:
    """Passes writes through to `target`, except any containing `blocked`.
    Skips the system's default '\n' after blocking the 'target' phrase.
    """

    def __init__(self, target: TextIO, blocked: str) -> None:
        """Sets up the pass-through target and the phrase to block.

        Args:
            target: The real stream to forward unblocked writes to.
            blocked: Any write containing this substring is dropped.
        """

        self._target = target
        self._blocked = blocked
        self._skip_gnl = False

    def write(self, text: str) -> int:
        """Forwards `text` to `target`, unless it contains the blocked
        phrase - in which case it (and the newline that follows it) is
        dropped instead.

        Args:
            text: The chunk of text being written.

        Returns:
            Number of characters "written" (always len(text), whether
            forwarded or silently dropped, to satisfy the stream API).
        """

        if self._blocked in text:
            self._skip_gnl = True
            return len(text)
        if self._skip_gnl and text == "\n":
            self._skip_gnl = False
            return len(text)
        return self._target.write(text)

    def flush(self) -> None:
        """Flushes the underlying target stream."""

        self._target.flush()


class MazeState(MazeGenerator):  # type: ignore[misc]
    """Owns one level's maze, player, ghosts, gums, and rendering."""

    def __init__(self, size: tuple[int, int], maze_config: Any,
                 screen_size: tuple[int, int],
                 bonuses: BonusState, lv_index: int = 0) -> None:
        """Builds the maze, ghosts, player, gums, and visualizer for one level.

        Args:
            size: (width, height) of this level's maze, in cells.
            maze_config: The parsed game Configs (points, pacgum count,
                level timer, etc).
            screen_size: (width, height) of the display, in pixels.
            bonuses: The player's chosen bonus/cheat toggles.
            lv_index: This level's 1-based position in the level list -
                used for wall-color cycling and the ghost-speed ramp.
        """

        try:
            with contextlib.redirect_stdout(
                _FilterStream(sys.stdout,
                              "maze is too small to add '42' in it")
            ):
                super().__init__(
                    size=size,
                    entry_cell=find_safe_entry_cell(size[0], size[1]),
                    seed=maze_config.seed)
        except Exception as e:
            print(f"{self.__class__.__name__} error: {e}. "
                  "Unable to generate maze.", file=sys.stderr)
            pygame.quit()
            sys.exit(1)

        self.bonuses = bonuses

        self.lv_index = lv_index

        self.pinky = Pinky(0, 0)
        self.blinky = Blinky(0, len(self.maze[0]) - 1)
        self.inky = Inky(len(self.maze) - 1, len(self.maze[0]) - 1)
        self.clyde = Clyde(len(self.maze) - 1, 0)

        self.ghosts = (self.blinky, self.inky, self.pinky, self.clyde)

        ghost_colors = {ghost.__class__.__name__: ghost.color
                        for ghost in self.ghosts}

        self.vis = Visualizer(self.maze, ghost_colors, screen_size,
                              maze_config.points_per_pacgum,
                              maze_config.points_per_super_pacgum,
                              maze_config.points_per_ghost,
                              self.lv_index - 1)

        self.player = Player(self)

        c, r = self.maze_entry
        self.pacstart = (r, c)

        # time_per_cell: float = 0.35
        # maze_time_limit = (maze_config.level_max_time
        #                   if self.lv_index <= 3
        #                   else max(maze_config.level_max_time,
        #                            (int(len(self.maze)
        #                                 * len(self.maze[0])
        #                                 * time_per_cell))))
        maze_time_limit = maze_config.level_max_time
        self.time = self.set_lv_timer(maze_time_limit)

        self.gummis = Gummis(
            self.maze,
            self.pacstart,
            maze_config.pacgum,
            self.bonuses.max_gums
        )

        self.gum_point = maze_config.points_per_pacgum
        self.supergum_point = maze_config.points_per_super_pacgum

        if bonuses.slowpoke_ghost:
            self.ghost_speed = max(1, int(self.player.speed * 0.5))
        elif self.lv_index <= 3:
            self.ghost_speed = (max(1, int(self.player.speed) - 1))
        else:
            self.ghost_speed = int(self.player.speed)

        self.collision_threshhold = 10
        self.ghost_freeze_frames = 150

    def handle_eaten_gums(self) -> None:
        """Checks whether pacman is centered on a gum and, if so, eats it.

        Pops the gum, awards its points, and - for a super-pacgum -
        sets every ghost frightened. Also clears invincibility once
        pacman has left the starting cell.
        """

        if self.player.is_centered():
            if not (self.player.position == self.pacstart
                    and self.player.is_invincible):
                self.player.set_invincible(False)

            if self.player.position in self.gummis.pacgums:
                self.gummis.pop_pacgum(self.player.position)
                self.player.increase_score(self.gum_point)
            elif self.player.position in self.gummis.superpacgums:
                self.gummis.pop_superpacgum(self.player.position)
                self.player.increase_score(self.supergum_point)

                if self.lv_index < 4:
                    frightened_time = 240
                elif self.lv_index < 7:
                    frightened_time = 180
                else:
                    frightened_time = 120
                frightened_duration = ((frightened_time * 2)
                                       if self.bonuses.ultragums
                                       else frightened_time)

                for ghost in (self.pinky, self.blinky, self.inky, self.clyde):
                    ghost.set_frightened_status(frightened_duration)

    def set_lv_timer(self, time_lim: int) -> int:
        """Converts a level's configured time limit into frames.

        Args:
            time_lim: Configured time limit, in seconds.

        Returns:
            The time limit in frames, doubled if bonus_time is active.
        """

        return time_lim * 2 * 30 if self.bonuses.bonus_time else time_lim * 30
