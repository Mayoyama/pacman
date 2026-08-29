from abc import ABC, abstractmethod
from math import sqrt
from sys import stderr
from random import randint
from enum import Enum
from typing import TYPE_CHECKING
from src.player import Direction
if TYPE_CHECKING:
    from src.game_logic.mazestate import MazeState


class GhostStatus(Enum):
    """A ghost's current behavior mode."""

    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"


class Ghost(ABC):
    """Base class for the four ghosts: shared position/animation state
    and timers. Each subclass implements move() with its own targeting
    logic.
    """

    def __init__(self, row: int, col: int,
                 color: tuple[int, int, int]) -> None:
        """Sets up starting position and state flags.

        Args:
            row: Starting row, in grid cells.
            col: Starting column, in grid cells.
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
        """Whether this ghost is currently chasing the player."""

        return self._mode == GhostStatus.CHASE

    @property
    def scatter(self) -> bool:
        """Whether this ghost is currently in scatter mode."""

        return self._mode == GhostStatus.SCATTER

    @property
    def frightened(self) -> bool:
        """Whether this ghost is currently edible."""

        return self._mode == GhostStatus.FRIGHTENED

    def heuristics(self, target: tuple[int, int], moves: list[tuple[int, int]]
                   ) -> tuple[int, int]:
        """Computes the best move based on straight-line (Euclidean)
        distance to target.

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
        """Computes this ghost's next target cell for this frame.

        Args:
            maze_state: The current level's MazeState.

        Returns:
            The (row, col) cell to move toward next.
        """

        pass

    def can_move(self, move: str, maze: list[list[int]]) -> bool:
        """Checks whether this ghost can move one step in a direction.

        Args:
            move: The direction to check ("NORTH"/"EAST"/"SOUTH"/"WEST").
            maze: Grid representation of the maze, for wall checks.

        Returns:
            True if that direction isn't wall-blocked and stays in bounds.

        Note:
            Each cell is a 4-bit wall mask: bit 0 = north, bit 1 = east,
            bit 2 = south, bit 3 = west.
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
        """Advances ghost by one frame, or spends the frame retargeting.

        If curr_pos and next_pos are already equal (just arrived), this
        frame only picks the next cell to move toward and returns - no
        pixel movement happens, matching the player's own one-frame
        pause at each cell boundary. Otherwise steps pixel_pos toward
        next_pos by speed on each axis still needing to move, snapping
        exactly onto its center once within speed of arrival.

        Args:
            maze_state: Shared source for cell_center(), so pixel math
                stays identical to the player's own.
            speed: Pixels to advance per frame along each axis that
                still needs to move.
        """

        if self.curr_pos == self.next_pos:
            self.next_pos = self.move(maze_state)
            return

        nx, ny = maze_state.player.cell_center(*self.next_pos)
        cx, cy = self.pixel_pos

        if abs(nx - cx) <= speed and abs(ny - cy) <= speed:
            self.pixel_pos = (nx, ny)
            self.curr_pos = self.next_pos
            return

        dx = speed if nx > cx else -speed if nx < cx else 0
        dy = speed if ny > cy else -speed if ny < cy else 0

        self.pixel_pos = (cx + dx, cy + dy)

    def respawn(self, maze_state: "MazeState") -> None:
        """Resets this ghost to its starting corner.

        Args:
            maze_state: Shared source for cell_center()/cell_size, so
                pixel math stays identical to the player's own.
        """

        self.curr_pos = self.start_pos
        self.previous_pos = None
        self.next_pos = self.curr_pos
        self.init_pixel_pos(maze_state)

    def eaten(self, freeze_frames: int, remaining_frightened: int) -> None:
        """Marks this ghost eaten: frozen at its corner, then re-armed
        frightened for whatever time it had left when eaten.

        Args:
            freeze_frames: How many frames to stay frozen before moving
                again.
            remaining_frightened: Frightened frames to restore once the
                freeze ends.
        """

        self.dead = True
        self.freeze_timer = freeze_frames
        self.set_frightened_status(remaining_frightened)

    def set_frightened_status(self, frames: int = 300) -> None:
        """Puts this ghost into frightened mode for a number of frames.

        Args:
            frames: How many frames frightened mode should last.
        """

        self._mode = GhostStatus.FRIGHTENED
        self.scared_timer = frames

    def handle_frightened_status(self, reset: bool = False) -> int:
        """Counts down frightened mode by one frame, ending it at zero.

        Args:
            reset: If True, force-clears frightened mode immediately
                instead of counting down.

        Returns:
            Remaining frightened frames, or -1 if already at zero.
        """

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
        """Puts this ghost into scatter mode for a number of frames.

        Args:
            frames: How many frames scatter mode should last.
        """

        self._mode = GhostStatus.SCATTER
        self.scatter_timer = frames

    def handle_scatter_mode(self) -> int:
        """Counts down scatter mode by one frame, ending it at zero.

        Returns:
            Remaining scatter frames, or -1 if already at zero.
        """

        if self.scatter_timer > 0:
            self.scatter_timer -= 1

            if self.scatter_timer == 0:
                self._mode = GhostStatus.CHASE

            return self.scatter_timer

        else:
            print("handle_scatter_mode: scatter timer already 0",
                  file=stderr)
            return -1


class Blinky(Ghost):
    """Red ghost, starts top-right. Targets Pac-Man's exact current
    tile - the most direct chaser.
    """

    def __init__(self, row: int, col: int) -> None:
        """Sets up Blinky's starting position and color.

        Args:
            row: Starting row, in grid cells.
            col: Starting column, in grid cells.
        """

        super().__init__(row, col, (255, 0, 0))

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """Computes the best move to do by the heuristics.

        Args:
            maze_state: The current level's MazeState.

        Returns:
            The (row, col) cell to move toward next.
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
    """Pink ghost, starts top-left. Targets 4 tiles ahead of Pac-Man's
    facing direction, to cut him off.
    """

    def __init__(self, row: int, col: int) -> None:
        """Sets up Pinky's starting position and color.

        Args:
            row: Starting row, in grid cells.
            col: Starting column, in grid cells.
        """

        super().__init__(row, col, (255, 184, 255))

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """Computes the best move to do by the heuristics.

        Args:
            maze_state: The current level's MazeState.

        Returns:
            The (row, col) cell to move toward next.
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
    """Cyan ghost, starts bottom-right."""

    def __init__(self, row: int, col: int) -> None:
        """Sets up Inky's starting position and color.

        Args:
            row: Starting row, in grid cells.
            col: Starting column, in grid cells.
        """

        super().__init__(row, col, (0, 255, 255))

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """Computes the best move to do by the heuristics.

        Args:
            maze_state: The current level's MazeState.

        Returns:
            The (row, col) cell to move toward next.
        """

        x, y = maze_state.player.pixel_pos
        target = maze_state.player.pixel_to_cell(x, y)
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
    """Orange ghost, starts bottom-left."""

    def __init__(self, row: int, col: int) -> None:
        """Sets up Clyde's starting position and color.

        Args:
            row: Starting row, in grid cells.
            col: Starting column, in grid cells.
        """

        super().__init__(row, col, (255, 184, 82))

    def get_dist(self, target: tuple[int, int]) -> int:
        """Returns the straight-line distance from this ghost to target.

        Args:
            target: (row, col) cell to measure distance to.

        Returns:
            The Euclidean distance, rounded down to an int.
        """

        return int(sqrt(((self.curr_pos[0] - target[0]) ** 2) +
                        ((self.curr_pos[1] - target[1]) ** 2)))

    def move(self, maze_state: "MazeState") -> tuple[int, int]:
        """Computes the best move to do by the heuristics.

        Args:
            maze_state: The current level's MazeState.

        Returns:
            The (row, col) cell to move toward next.
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
