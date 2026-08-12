from enum import Enum
from sys import stderr


class Direction(Enum):
    """The four cardinal movement directions, plus a paused state."""

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PAUSED = "paused"


class Movement:
    """Owns one entity's grid cell, pixel position, and per-frame movement."""

    def __init__(self, start: tuple[int, int], maze: list[list[int]],
                 maze_offset: tuple[int, int],
                 cell_size: int) -> None:
        """Sets up starting position and movement/tolerance parameters.

        Args:
            start: Starting (row, col) grid cell.
            maze: Grid representation of the maze, for wall checks.
            maze_offset: (x, y) pixel offset centering the actual maze
                within its (possibly larger) surface.
            cell_size: Width/height of one maze cell, in pixels.
        """
        self.cell_size = cell_size
        self.maze_offset = maze_offset
        self.maze = maze
        self.position: tuple[int, int] = start
        self.pixel_pos: tuple[int, int] = self.cell_center(*start)
        self.direction: Direction = Direction.PAUSED
        self.buffer_dir: Direction = Direction.PAUSED
        frames_per_cell = 8
        if frames_per_cell < 2:
            print("Invalid frames_per_cell (<2); using default of 12",
                  file=stderr)
            frames_per_cell = 12
        self.speed: int = max(1, self.cell_size // frames_per_cell)
        # self.tolerance: how close to a cell center counts as "centered"
        self.tolerance: int = 0

    @staticmethod
    def _has_N_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a north wall"""
        return bool(cell & 1)

    @staticmethod
    def _has_E_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a east wall"""
        return bool(cell & 2)

    @staticmethod
    def _has_S_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a south wall"""
        return bool(cell & 4)

    @staticmethod
    def _has_W_wall(cell: int) -> bool:
        """Returns True/False whether the cell has a west wall"""
        return bool(cell & 8)

    def cell_to_pixel(self, r: int, c: int) -> tuple[int, int]:
        """Converts a grid cell's (row, col) to its top-left pixel position.

        Args:
            r: The cell's row index.
            c: The cell's column index.

        Returns:
            The (x, y) pixel coordinates of the cell's top-left corner,
            accounting for the image margin and cell size.
        """
        off_x, off_y = self.maze_offset
        x = off_x + (c * self.cell_size)
        y = off_y + (r * self.cell_size)
        return x, y

    def cell_center(self, r: int, c: int) -> tuple[int, int]:
        """Converts a grid cell's (row, col) to its center pixel position.

        Args:
            r: The cell's row index.
            c: The cell's column index.

        Returns:
            The (x, y) pixel coordinates of the cell's center point.
        """
        x, y = self.cell_to_pixel(r, c)
        return x + self.cell_size // 2, y + self.cell_size // 2

    def can_move(self, direction: Direction) -> bool:
        """Checks whether a movement is valid from the current cell.

        Args:
            direction: The direction to check.

        Returns:
            True if movement in valid, False otherwise.
        """
        r, c = self.position[0], self.position[1]
        match direction:
            case Direction.UP:
                return r > 0 and not self._has_N_wall(self.maze[r][c])
            case Direction.LEFT:
                return c > 0 and not self._has_W_wall(self.maze[r][c])
            case Direction.DOWN:
                return (r < len(self.maze) - 1
                        and not self._has_S_wall(self.maze[r][c]))
            case Direction.RIGHT:
                return (c < len(self.maze[0]) - 1
                        and not self._has_E_wall(self.maze[r][c]))
        return False

    def set_desired_direction(self, direction: Direction) -> None:
        """Buffers the last direction requested by input.

        Does not move the player immediately - applied by update() once
        the player is centered and that direction is not wall-blocked.

        Args:
            direction: The direction requested.
        """
        self.buffer_dir = direction

    def is_centered(self) -> bool:
        """Checks whether pixel_pos is within tolerance of the current
        cell's center.

        Returns:
            True if close enough to cell_center(*self.cell) to be
            considered aligned, False otherwise.
        """
        px, py = self.pixel_pos
        cx, cy = self.cell_center(*self.position)
        if abs(px - cx) <= self.tolerance and abs(py - cy) <= self.tolerance:
            return True
        return False

    def update(self) -> None:
        """Advances movement by one frame.

        Moves pixel_pos by speed in self.direction. When centered on a
        cell, updates self.cell and applies buffer_dir if it is not
        wall-blocked; otherwise keeps moving in self.direction unless
        that is wall-blocked, in which case movement stops.
        """
        if self.is_centered():
            if self.can_move(self.buffer_dir):
                self.direction = self.buffer_dir
            elif not self.can_move(self.direction):
                self.direction = Direction.PAUSED

            if self.direction != Direction.PAUSED:
                self.position = self._next_cell(self.direction)
        else:
            x, y = self.pixel_pos
            if self.direction == Direction.UP:
                self.pixel_pos = (x, y - self.speed)
            elif self.direction == Direction.DOWN:
                self.pixel_pos = (x, y + self.speed)
            elif self.direction == Direction.LEFT:
                self.pixel_pos = (x - self.speed, y)
            elif self.direction == Direction.RIGHT:
                self.pixel_pos = (x + self.speed, y)

    def _next_cell(self, direction: Direction) -> tuple[int, int]:
        """Returns the adjacent cell one step over in the given direction.

        Args:
            direction: The direction to step in.

        Returns:
            The (row, col) of the neighboring cell.
        """
        r, c = self.position
        if direction == Direction.UP:
            return (r - 1, c)
        elif direction == Direction.DOWN:
            return (r + 1, c)
        elif direction == Direction.LEFT:
            return (r, c - 1)
        elif direction == Direction.RIGHT:
            return (r, c + 1)
        return (r, c)
