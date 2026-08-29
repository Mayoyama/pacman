from typing import Any

from .movement import Movement


class Player(Movement):
    """Tracks player-owned game state.

    Position, movement, and collision belong to Movement, not Player.
    """

    def __init__(self, maze: Any, lives: int = 3) -> None:
        """Sets up starting lives and invincibility state.

        Args:
            maze: The MazeState this player belongs to - supplies the
                starting cell, maze grid, and pixel geometry.
            lives: Starting life count.
        """

        start_col, start_row = maze.maze_entry

        super().__init__(
            start=(start_row, start_col),
            maze=maze.maze,
            maze_offset=maze.vis.get_maze_offset(),
            cell_size=maze.vis.pixel_math.cell_size
            )

        self._lives = lives
        self._score = 0
        self._is_invincible = False
        self._respawn_immunity_timer = 0
        self.start_respawn_immunity_timer(90)
        self._name = ""

    @property
    def name(self) -> str:
        """Return the player's name."""

        return self._name

    @property
    def lives(self) -> int:
        """Return the player's current life count."""

        return self._lives

    @property
    def score(self) -> int:
        """Return the player's current score."""

        return self._score

    @property
    def is_invincible(self) -> bool:
        """Return whether the player is currently invincible."""

        return self._is_invincible

    def pixel_to_cell(self, x: int, y: int) -> tuple[int, int]:
        """Converts (x, y) pixel coordinates back to a grid cell's (row, col).

        Args:
            x: The horizontal pixel coordinate.
            y: The vertical pixel coordinate.

        Returns:
            The (row, col) grid indices matching the pixel location.
        """

        off_x, off_y = self.maze_offset
        c = (x - off_x) // self.cell_size
        r = (y - off_y) // self.cell_size

        return r, c

    def set_name(self, name: str) -> bool:
        """Validates and stores a candidate player name.

        Args:
            name: The candidate name to validate and store.

        Returns:
            True if valid and stored, False if rejected.
        """

        if len(name) < 3 or len(name) > 10:
            return False

        for char in name:
            if not char.isalnum() and char != " ":
                return False

        self._name = name

        return True

    def set_lives(self, lives: int) -> None:
        """Sets the player's life count directly, e.g. when carrying it into
        a new level.

        Args:
            lives: The life count to set. Must be non-negative.

        Raises:
            ValueError: If lives is negative (also resets lives to 0).
        """

        if lives < 0:
            self._lives = 0
            raise ValueError(f"set_lives: Invalid value passed [{lives}]. "
                             "Resetting lives to 0")

        self._lives = lives

    def increase_lives(self, amount: int = 1) -> None:
        """Add to the player's life count.

        Args:
            amount: Number of lives to add. Must be at least 1.

        Raises:
            ValueError: If amount is less than 1.
        """

        if amount < 1:
            raise ValueError("increase_lives: amount must be at least 1")

        self._lives += amount

    def decrease_lives(self) -> int:
        """Remove one life from the player's count.

        Returns:
            The player's remaining life count.

        Raises:
            ValueError: If called when no lives remain.
        """

        if self._lives < 1:
            raise ValueError("decrease_lives: no lives remaining")

        self._lives -= 1

        return self._lives

    def increase_score(self, points: int) -> None:
        """Adds points to the player's score.

        Args:
            points: Points to add. Must be at least 1.

        Raises:
            ValueError: If points is less than 1.
        """

        if points < 1:
            raise ValueError("increase_score: 0 or negative value passed")

        self._score += points

    def set_score(self, score: int) -> None:
        """Sets the player's score directly, e.g. when carrying it into a new
        level.

        Args:
            score: The score to set. Must be non-negative.

        Raises:
            ValueError: If score is negative (also resets score to 0).
        """

        if score < 0:
            self._score = 0
            raise ValueError(f"set_score: Invalid value passed [{score}]. "
                             "Resetting score to 0")

        self._score = score

    def set_invincible(self, value: bool) -> None:
        """Enable or disable invincibility (cheat mode)."""

        self._is_invincible = value

    def start_respawn_immunity_timer(self, frames: int = 60) -> None:
        """Starts (or restarts) a hard cap on how long invincibility can
        last after pacman respawns, regardless of position or movement.

        Args:
            frames: Frames invincibility will last.
        """

        self._is_invincible = True
        self._respawn_immunity_timer = frames

    def handle_immunity_timer(self) -> None:
        """Counts the invincibility cap down by one frame, forcing
        invincibility off once it reaches zero. Safe to call every frame
        unconditionally - does nothing once the timer's already at 0.
        """

        if self._respawn_immunity_timer > 0:
            self._respawn_immunity_timer -= 1

            if self._respawn_immunity_timer == 0:
                self.set_invincible(False)
