from abc import ABC, abstractmethod
from typing import Any


class Ghost(ABC):
    """Base class for the four ghosts: shared state, no targeting
    logic yet - move() is a placeholder until partner's algorithm
    research lands.
    """

    def __init__(self, col: int, row: int,
                 color: tuple[int, int, int]) -> None:
        """Sets up starting position and state flags.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
            color: This ghost's RGB color.
        """
        self.name = self.__class__.__name__
        self.start_pos = (col, row)
        self.curr_pos = self.start_pos
        self.next_pos = self.curr_pos
        self.color = color
        self.chase = True
        self.scatter = False
        self.frightened = False

    def can_move(self, move: str, maze: list[list[int]]) -> bool:
        """Checks whether this ghost can step one cell in a direction.

        Args:
            move: One of "NORTH"/"EAST"/"SOUTH"/"WEST" (case-insensitive).
            maze: Grid representation of the maze, for wall checks.

        Returns:
            True if movement is valid, False otherwise.
        """
        x, y = self.curr_pos[0], self.curr_pos[1]
        match move.upper():
            case "NORTH":
                return y > 0 and not ((maze[y][x] >> 0) & 1)
            case "EAST":
                return x < len(maze[0]) - 1 and not ((maze[y][x] >> 1) & 1)
            case "SOUTH":
                return y < len(maze) - 1 and not ((maze[y][x] >> 2) & 1)
            case "WEST":
                return x > 0 and not ((maze[y][x] >> 3) & 1)
        return False

    @abstractmethod
    def move(self, maze: Any) -> tuple[int, int]:
        """Placeholder - real targeting algorithm not merged in yet."""
        raise NotImplementedError


class Blinky(Ghost):
    """Red ghost."""

    def __init__(self, col: int, row: int) -> None:
        """Sets up starting position with Blinky's fixed color.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
        """
        super().__init__(col, row, (255, 0, 0))

    def move(self, maze: Any) -> tuple[int, int]:
        return self.curr_pos


class Pinky(Ghost):
    """Pink ghost."""

    def __init__(self, col: int, row: int) -> None:
        """Sets up starting position with Pinky's fixed color.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
        """
        super().__init__(col, row, (255, 184, 255))

    def move(self, maze: Any) -> tuple[int, int]:
        return self.curr_pos


class Inky(Ghost):
    """Cyan ghost."""

    def __init__(self, col: int, row: int) -> None:
        """Sets up starting position with Inky's fixed color.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
        """
        super().__init__(col, row, (0, 255, 255))

    def move(self, maze: Any) -> tuple[int, int]:
        return self.curr_pos


class Clyde(Ghost):
    """Orange ghost."""

    def __init__(self, col: int, row: int) -> None:
        """Sets up starting position with Clyde's fixed color.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
        """
        super().__init__(col, row, (255, 184, 82))

    def move(self, maze: Any) -> tuple[int, int]:
        return self.curr_pos
