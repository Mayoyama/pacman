from abc import ABC, abstractmethod
from math import sqrt
from sys import stderr
from random import randint
from enum import Enum
from typing import TYPE_CHECKING, Any
from src.player import Direction
if TYPE_CHECKING:
    from src.game_logic.mazestate import MazeState


class GhostStatus(Enum):
    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"


class Ghost(ABC):
    """Base class for the four ghosts: shared state, no targeting
    logic yet - move() is a placeholder until partner's algorithm
    research lands.
    """

    def __init__(self, row: int, col: int,
                 color: tuple[int, int, int]) -> None:
        """Sets up starting position and state flags.

        Args:
            col: Starting column, in grid cells.
            row: Starting row, in grid cells.
            color: This ghost's RGB color.
        """
        self.name = self.__class__.__name__
        self.start_pos = (row, col)
        self.curr_pos = self.start_pos
        self.next_pos = self.curr_pos
        self.previous_pos: tuple[int, int] | None = None
        self.color = color
        self._mode = GhostStatus.CHASE
        self.dead = False
        self.scared_timer = 0
        self.freeze_timer = 0
        self.scatter_timer = 0

    @property
    def chase(self) -> bool:
        return self._mode == GhostStatus.CHASE

    @property
    def scatter(self) -> bool:
        return self._mode == GhostStatus.SCATTER

    @property
    def frightened(self) -> bool:
        return self._mode == GhostStatus.FRIGHTENED

    def heuristics(self, target: tuple[int, int], moves: list[tuple[int, int]]
                   ) -> tuple[int, int]:
        """Computes the best move to do based on Manhattan distance
        Args:
            target: The (row, col) cell being pathed toward.
            moves: Candidate (row, col) cells reachable this step.
        Returns:
            The (row, col) of the chosen move.
        """
        h: float = 1000
        next: list[tuple[int, int]] = []
        for move in moves:
            score = sqrt(((move[0] - target[0]) ** 2) +
                         ((move[1] - target[1]) ** 2))
            if score <= h:
                if score < h:
                    next = []
                h = score
                next.append(move)
        return next[randint(0, len(next)-1)]

    @abstractmethod
    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        pass

    def can_move(self, move: str, maze: list[list[int]]) -> bool:
        """
        Check the bit depending on the move and if we are allow to do it
        ARGS:
            move (str): the direction
            maze (list[list[int]]): the maze
        Return:
            (boolean) answer if we can make the move
        Note:
            a cell is four bits (WEST SOUTH EAST NORTH)
        """
        r, c = self.curr_pos[0], self.curr_pos[1]
        match move.upper():
            case "NORTH":
                return r > 0 and not ((maze[r][c] >> 0) & 1)
            case "EAST":
                return c < len(maze[0]) - 1 and not ((maze[r][c] >> 1) & 1)
            case "SOUTH":
                return r < len(maze) - 1 and not ((maze[r][c] >> 2) & 1)
            case "WEST":
                return c > 0 and not ((maze[r][c] >> 3) & 1)
        return False

    @staticmethod
    def get_move(ghost: Any, maze_state: Any
                 ) -> tuple[tuple[int, int], tuple[int, int]]:
        try:
            return (ghost.curr_pos, ghost.move(maze_state))
        except (AttributeError, TypeError) as e:
            raise TypeError("maze or ghost or not in a good type.") from e

    def init_pixel_pos(self, maze_state: "MazeState") -> None:
        """Sets this ghost's pixel_pos to the pixel center of its current
        cell (curr_pos). Call once per ghost, right after maze_state
        exists - cell_size/maze_offset live on maze_state.player, so this
        can't happen inside __init__ itself.

        Args:
            maze_state: Shared source for cell_center()/cell_size, so
                pixel math stays identical to the player's own.
        """
        self.pixel_pos = maze_state.player.cell_center(*self.curr_pos)

    def advance_pixel_pos(self, maze_state: "MazeState", speed: int) -> None:
        """Advances pixel_pos by one frame toward next_pos's cell center.

        Once close enough (within speed, on both axes) to count as
        arrived, snaps pixel_pos exactly onto that cell center and updates
        curr_pos to match next_pos.

        Args:
            maze_state: Shared source for cell_center(), so pixel math
                stays identical to the player's own.
            speed: Pixels to advance per frame along each axis that still
                needs to move.
        """
        nx, ny = maze_state.player.cell_center(*self.next_pos)
        cx, cy = self.pixel_pos
        dx = min(speed, abs(nx - cx))
        dy = min(speed, abs(ny - cy))
        if nx < cx:
            dx = -dx
        if ny < cy:
            dy = -dy
        cx += dx
        cy += dy
        self.pixel_pos = (cx, cy)
        if cx == nx and cy == ny:
            self.curr_pos = self.next_pos
            self.next_pos = self.move(maze_state)

    def set_frightened_status(self, frames: int = 300) -> None:
        self._mode = GhostStatus.FRIGHTENED
        self.scared_timer = frames

    def handle_frightened_status(self, reset: bool = False) -> int:
        if reset:
            self._mode = GhostStatus.CHASE
            self.scared_timer = 0
            return 0
        if self.scared_timer > 0:
            self.scared_timer -= 1
            if self.scared_timer == 0:
                self._mode = GhostStatus.CHASE
            return self.scared_timer
        else:
            print("handle_frightened_status: scared timer already 0",
                  file=stderr)
            return -1

    def set_scatter_mode(self, frames: int = 450) -> None:
        self._mode = GhostStatus.SCATTER
        self.scatter_timer = frames

    def handle_scatter_mode(self) -> int:
        if self.scatter_timer > 0:
            self.scatter_timer -= 1
            if self.scatter_timer == 0:
                self._mode = GhostStatus.CHASE
            return self.scatter_timer
        else:
            print("handle_scatter_status: scatter timer already 0",
                  file=stderr)
            return -1


class Blinky(Ghost):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, (255, 0, 0))
        """
        Top-Right
        Behavior: He targets Pac-Man's exact current tile.
        Specialty: He is the most dangerous ghost. As Pac-Man eats more dots,
        Blinky speeds up (a mechanic known as "Cruise Elroy"). During "Scatter"
        mode, Blinky often refuses to stop hunting and keeps tracking Pac-Man
        directly.
        """

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze_state (MazeState): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        if self.frightened or self.dead or self.scatter:
            target = (0, len(maze_state._maze[0]) - 1)
        else:
            x, y = maze_state.player.pixel_pos
            target = maze_state.player.pixel_to_cell(x, y)
        moves = {"NORTH": (-1, 0), "EAST": (0, 1),
                 "SOUTH": (1, 0), "WEST": (0, -1)}
        r, c = self.curr_pos
        reachable = [(r + dr, c + dc)
                     for m, (dr, dc) in moves.items()
                     if self.can_move(m, maze_state._maze)]
        if len(reachable) > 1 and self.previous_pos in reachable:
            reachable.remove(self.previous_pos)
        if not reachable:
            return self.curr_pos
        self.previous_pos = self.curr_pos
        return self.heuristics(target, reachable)


class Pinky(Ghost):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, (255, 184, 255))
        """
        Top-Left
        Behavior: She targets 4 tiles ahead of Pac-Man, based on the direction
        he is facing.
        Specialty: Her goal is to cut you off and trap you. Due to
        an original code overflow bug, if Pac-Man is facing upward, Pinky
        targets 4 tiles up and 4 tiles to the left.
        """

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze_state (MazeState): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        moves = {"NORTH": (-1, 0), "EAST": (0, 1),
                 "SOUTH": (1, 0), "WEST": (0, -1)}
        x, y = maze_state.player.pixel_pos
        target = maze_state.player.pixel_to_cell(x, y)
        r, c = self.curr_pos
        direction = maze_state.player.direction
        if direction == Direction.UP:
            step_r, step_c = -1, 0
        elif direction == Direction.DOWN:
            step_r, step_c = 1, 0
        elif direction == Direction.LEFT:
            step_r, step_c = 0, -1
        elif direction == Direction.RIGHT:
            step_r, step_c = 0, 1
        else:
            step_r, step_c = 0, 0
        target_row = target[0] + (step_r * 4)
        target_col = target[1] + (step_c * 4)
        target = (target_row, target_col)
        if not self.chase or self.dead:
            target = (0, 0)
        reachable = [(r + dr, c + dc)
                     for m, (dr, dc) in moves.items()
                     if self.can_move(m, maze_state._maze)]
        if len(reachable) > 1 and self.previous_pos in reachable:
            reachable.remove(self.previous_pos)
        if not reachable:
            return self.curr_pos
        self.previous_pos = self.curr_pos
        return self.heuristics(target, reachable)


class Inky(Ghost):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, (0, 255, 255))
        """
        Bottom-Right
        Behavior: His targeting depends on both Pac-Man and Blinky.
        Calculation: He takes the tile 2 spaces ahead of Pac-Man, draws a
        vector from Blinky's current position to that tile, and doubles the
        length of that vector.
        Specialty: This makes his behavior seem completely unpredictable. He
        might rush straight at you or suddenly turn away based on where the
        red ghost is.
        """

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze_state (MazeState): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        moves = {"NORTH": (-1, 0), "EAST": (0, 1),
                 "SOUTH": (1, 0), "WEST": (0, -1)}
        x, y = maze_state.player.pixel_pos
        target = maze_state.player.pixel_to_cell(x, y)
        r, c = self.curr_pos
        direction = maze_state.player.direction
        blinky_row, blinky_col = maze_state.blinky.curr_pos
        if direction == Direction.UP:
            step_r, step_c = -1, 0
        elif direction == Direction.DOWN:
            step_r, step_c = 1, 0
        elif direction == Direction.LEFT:
            step_r, step_c = 0, -1
        elif direction == Direction.RIGHT:
            step_r, step_c = 0, 1
        else:
            step_r, step_c = 0, 0
        target_row = target[0] + (step_r * 2)
        target_col = target[1] + (step_c * 2)
        # Compute the vector between Blinky et ce pivot
        vector_row = target_row - blinky_row
        vector_col = target_col - blinky_col
        # Add the double of the vector to the Blinky position
        target_row = blinky_row + (vector_row * 2)
        target_col = blinky_col + (vector_col * 2)
        target = (target_row, target_col)
        if not self.chase or self.dead:
            target = (len(maze_state._maze) - 1, len(maze_state._maze[0]) - 1)
        moves = {"NORTH": (-1, 0), "EAST": (0, 1),
                 "SOUTH": (1, 0), "WEST": (0, -1)}
        r, c = self.curr_pos
        reachable = [(r + dr, c + dc)
                     for m, (dr, dc) in moves.items()
                     if self.can_move(m, maze_state._maze)]
        if len(reachable) > 1 and self.previous_pos in reachable:
            reachable.remove(self.previous_pos)
        if not reachable:
            return self.curr_pos
        self.previous_pos = self.curr_pos
        return self.heuristics(target, reachable)


class Clyde(Ghost):
    def __init__(self, row: int, col: int):
        super().__init__(row, col, (255, 184, 82))
        """
        Bottom-Left
        Behavior: His logic changes based on his proximity to Pac-Man.The
        8-Tile
        Rule: If Clyde is more than 8 tiles away from Pac-Man, he acts like
        Blinky and targets him directly. The moment he gets closer than 8
        tiles, he panics, abandons the chase, and retreats to his home corner
        (bottom-left).
        """

    def get_dist(self, target: tuple[int, int]) -> int:
        return int(sqrt(((self.curr_pos[0] - target[0]) ** 2) +
                        ((self.curr_pos[1] - target[1]) ** 2)))

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze_state (MazeState): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        x, y = maze_state.player.pixel_pos
        target = maze_state.player.pixel_to_cell(x, y)
        moves = {"NORTH": (-1, 0), "EAST": (0, 1),
                 "SOUTH": (1, 0), "WEST": (0, -1)}
        r, c = self.curr_pos
        if self.get_dist(target) < 8 or not self.chase or self.dead:
            target = (len(maze_state._maze) - 1, 0)
        reachable = [(r + dr, c + dc)
                     for m, (dr, dc) in moves.items()
                     if self.can_move(m, maze_state._maze)]
        if len(reachable) > 1 and self.previous_pos in reachable:
            reachable.remove(self.previous_pos)
        if not reachable:
            return self.curr_pos
        self.previous_pos = self.curr_pos
        return self.heuristics(target, reachable)
