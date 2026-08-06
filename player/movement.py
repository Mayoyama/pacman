from enum import Enum

class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    PAUSED = "paused"


class Movement:
    def __init__(self, start: tuple[int, int], maze: list[list[int]], pixel_math: tuple[int, int]) -> None:
        self.cell_size, self.padding = pixel_math
        self.maze = maze
        self.cell: tuple[int, int] = start          # grid cell, for wall checks
        self.pixel_pos: tuple[int, int] = self.cell_center(*start)       # continuous position, for tolerance check + rendering
        self.direction: Direction = Direction.PAUSED    # direction actually moving
        self.buffer_dir: Direction = Direction.PAUSED   # desired direction, applied when valid
        frames_per_cell = 4
        self.speed: int = max(1, self.cell_size // frames_per_cell)        # advance per frame
        self.tolerance: int = self.speed    # how close to a cell center counts as "centered"

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
        x = self.padding + (c * self.cell_size)
        y = self.padding + (r * self.cell_size)
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

    def has_blocked_wall(self, direction: Direction) -> bool:
        """Checks whether a wall blocks movement from the current cell.

        Args:
            direction: The direction to check (e.g. self.direction to see
                if travel can continue, or self.buffer_dir to see if a
                queued turn is currently valid).

        Returns:
            True if a wall blocks movement in that direction, False
            otherwise.
        """
        r, c = self.cell
        cell_value = self.maze[r][c]
        if direction == Direction.UP:
            return self._has_N_wall(cell_value)
        elif direction == Direction.DOWN:
            return self._has_S_wall(cell_value)
        elif direction == Direction.LEFT:
            return self._has_W_wall(cell_value)
        elif direction == Direction.RIGHT:
            return self._has_E_wall(cell_value)
        return False

    def set_desired_direction(self, direction: Direction) -> None:
        """Buffers the last direction requested by input.

        Does not move the player immediately - applied by update() once
        the player is centered and that direction is not wall-blocked.

        Args:
            direction: The direction requested.
        """
        self.buffer_dir = direction

    def _is_centered(self) -> bool:
        """Checks whether pixel_pos is within tolerance of the current
        cell's center.

        Returns:
            True if close enough to cell_center(*self.cell) to be
            considered aligned, False otherwise.
        """
        px, py = self.pixel_pos
        cx, cy = self.cell_center(*self.cell)
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
        if self._is_centered():
            if not self.has_blocked_wall(self.buffer_dir):
                self.direction = self.buffer_dir
            elif self.has_blocked_wall(self.direction):
                self.direction = Direction.PAUSED

            if self.direction != Direction.PAUSED:
                self.cell = self._next_cell(self.direction)
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
        r, c = self.cell
        if direction == Direction.UP:
            return (r - 1, c)
        elif direction == Direction.DOWN:
            return (r + 1, c)
        elif direction == Direction.LEFT:
            return (r, c - 1)
        elif direction == Direction.RIGHT:
            return (r, c + 1)
        return (r, c)
