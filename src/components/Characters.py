from abc import ABC, abstractmethod
from math import sqrt
from random import randint
from typing import Any


class Player:
    def __init__(self, col: int, row: int):
        if not self.check_position(col, row):
            raise ValueError("Player position is not possible")
        self._lives = 3
        self._position = (col, row)
        self._score = 0
        self.invincible = False

    def check_position(self, x, y) -> bool:
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        if x < 0 or x >= 100:
            return False
        if y < 0 or y >= 100:
            return False
        return True

    def get_name(self) -> None:
        self._name = ""
        while not self._name:
            self._name = str(input("Player's name: "))
            for char in self._name:
                if len(self._name) < 3:
                    print("WARNING: player name too short.")
                    self._name = ""
                    break
                if len(self._name) > 10:
                    print("WARNING: player name too long.")
                    self._name = ""
                    break
                if not char.isalnum() and char != ' ':
                    print("WARNING: invalid character in player name.")
                    self._name = ""
                    break

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
        x, y = self._position[0], self._position[1]
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

    def die(self) -> None:
        if self._lives < 1:
            raise ValueError("no life anymore.")
        self._lives -= 1

    def get_stats(self) -> tuple[str, tuple[int, int], int]:
        return (self._name, self._position, self._score)


class Ghost(ABC):
    def __init__(self, col: int, row: int, color: str):
        self.chase = True
        self.scatter = False
        self.frightened = False
        self.position = (col, row)
        self.color = color
        """
        [[9, 1, 1, 5, 1, 1, 5, 1, 3, 9, 5, 1, 5, 5, 3],
        [8, 2, 12, 5, 2, 10, 9, 2, 10, 8, 5, 6, 9, 1, 6],
        [10, 8, 1, 3, 12, 4, 2, 8, 2, 8, 5, 5, 6, 8, 3],
        [10, 12, 0, 0, 1, 5, 2, 10, 10, 8, 3, 9, 1, 4, 2],
        [12, 5, 6, 12, 4, 3, 10, 8, 6, 12, 4, 2, 12, 1, 2],
        [9, 1, 1, 3, 15, 10, 12, 6, 15, 15, 15, 8, 3, 8, 6],
        [10, 10, 8, 6, 15, 12, 5, 1, 5, 7, 15, 8, 2, 8, 3],
        [8, 6, 8, 3, 15, 15, 15, 10, 15, 15, 15, 10, 8, 4, 2],
        [10, 9, 2, 8, 5, 3, 15, 10, 15, 13, 5, 2, 8, 3, 10],
        [8, 2, 12, 2, 9, 6, 15, 10, 15, 15, 15, 8, 6, 8, 2],
        [10, 8, 1, 6, 12, 3, 9, 2, 9, 5, 1, 6, 9, 4, 6],
        [8, 2, 12, 5, 1, 2, 10, 8, 2, 9, 4, 3, 8, 1, 3],
        [8, 4, 3, 9, 2, 12, 0, 4, 2, 10, 9, 4, 2, 10, 10],
        [8, 3, 8, 6, 12, 1, 4, 1, 4, 6, 12, 3, 12, 2, 10],
        [12, 6, 12, 5, 5, 4, 5, 4, 5, 5, 5, 4, 5, 4, 6]]
        """

    def heuristics(self, target: tuple[int, int], moves: list[tuple[int, int]]
                   ) -> tuple[int, int]:
        """
        compute the best move to do by Manhattan distance
        Args:
            maze (Maze): the environnement
            moves (list[tuple[int, int]]): possible moves to do from
                            the position
        Returns:
            (tuple[int, int]) the best move to do
        """
        h = 1000
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
    def move(self) -> tuple[int, int]:
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
        x, y = self.position[0], self.position[1]
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

    @staticmethod
    def get_move(ghost: Any, maze: Any
                 ) -> tuple[tuple[int, int], tuple[int, int]]:
        try:
            return (ghost.position, ghost.move(maze))
        except Exception:
            raise ValueError("maze or ghost or not in a good type.")


class Blinky(Ghost):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, "red")
        """
        Top-Right
        Behavior: He targets Pac-Man's exact current tile.
        Specialty: He is the most dangerous ghost. As Pac-Man eats more dots,
        Blinky speeds up (a mechanic known as "Cruise Elroy"). During "Scatter"
        mode, Blinky often refuses to stop hunting and keeps tracking Pac-Man
        directly.
        """

    def move(self, maze: Any) -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze (Maze): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        if self.frightened:
            target = (maze.width - 1, 0)
        else:
            target = maze.player._position
        moves = {"NORTH": (0, -1), "EAST": (1, 0),
                 "SOUTH": (0, 1), "WEST": (-1, 0)}
        c, r = self.position
        reachable = [(c + dx, r + dy)
                     for m, (dx, dy) in moves.items()
                     if self.can_move(m, maze._maze)]
        if not reachable:
            return self.position
        return self.heuristics(target, reachable)


class Pinky(Ghost):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, "pink")
        """
        Top-Left
        Behavior: She targets 4 tiles ahead of Pac-Man, based on the direction
        he is facing.
        Specialty: Her goal is to cut you off and trap you. Due to
        an original code overflow bug, if Pac-Man is facing upward, Pinky
        targets 4 tiles up and 4 tiles to the left.
        """

    def move(self, maze: Any) -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze (Maze): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        moves = {"NORTH": (0, -1), "EAST": (1, 0),
                 "SOUTH": (0, 1), "WEST": (-1, 0)}
        c, r = self.position
        direction = maze.player.direction
        col, row = maze.player.position
        if direction == "UP":
            y, x = -1, 0
        elif direction == "DOWN":
            y, x = 1, 0
        elif direction == "LEFT":
            y, x = 0, -1
        elif direction == "RIGHT":
            y, x = 0, 1
        else:
            y, x = 0, 0
        target_row = row + (y * 4)
        target_col = col + (x * 4)
        target = (target_col, target_row)
        if not self.chase:
            target = (0, 0)
        reachable = [(c + dx, r + dy)
                     for m, (dx, dy) in moves.items()
                     if self.can_move(m, maze._maze)]
        if not reachable:
            return self.position
        return self.heuristics(target, reachable)


class Inky(Ghost):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, "cyan")
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

    def move(self, maze: Any) -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze (Maze): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        moves = {"NORTH": (0, -1), "EAST": (1, 0),
                 "SOUTH": (0, 1), "WEST": (-1, 0)}
        c, r = self.position
        direction = maze.player.direction
        blinky_col, blinky_row = maze.blinky.position
        col, row = maze.player.position
        if direction == "UP":
            y, x = -1, 0
        elif direction == "DOWN":
            y, x = 1, 0
        elif direction == "LEFT":
            y, x = 0, -1
        elif direction == "RIGHT":
            y, x = 0, 1
        else:
            y, x = 0, 0
        target_row = row + (y * 2)
        target_col = col + (x * 2)
        # Compute the vector between Blinky et ce pivot
        vector_row = target_row - blinky_row
        vector_col = target_col - blinky_col
        # Add the double of the vector to the Blinky position
        target_row = blinky_row + (vector_row * 2)
        target_col = blinky_col + (vector_col * 2)
        target = (target_col, target_row)
        if not self.chase:
            target = (maze.width - 1, maze.height - 1)
        moves = {"NORTH": (0, -1), "EAST": (1, 0),
                 "SOUTH": (0, 1), "WEST": (-1, 0)}
        c, r = self.position
        reachable = [(c + dx, r + dy)
                     for m, (dx, dy) in moves.items()
                     if self.can_move(m, maze._maze)]
        if not reachable:
            return self.position
        return self.heuristics(target, reachable)


class Clyde(Ghost):
    def __init__(self, col: int, row: int):
        super().__init__(col, row, "orange")
        """
        Bottom-Left
        Behavior: His logic changes based on his proximity to Pac-Man.The
        8-Tile
        Rule: If Clyde is more than 8 tiles away from Pac-Man, he acts like
        Blinky and targets him directly. The moment he gets closer than 8
        tiles, he panics, abandons the chase, and retreats to his home corner
        (bottom-left).
        """

    def move(self, maze: Any) -> tuple[int, int]:
        """
        compute the best move to do by the heuristic
        Args:
            maze (Maze): the environnement
        Returns:
            (tuple[int, int]) the best move to do
        """
        moves = {"NORTH": (0, -1), "EAST": (1, 0),
                 "SOUTH": (0, 1), "WEST": (-1, 0)}
        c, r = self.position
        target = maze.player.position
        if self.get_dist() < 8 or not self.chase:
            target = (0, maze.height - 1)
        reachable = [(c + dx, r + dy)
                     for m, (dx, dy) in moves.items()
                     if self.can_move(m, maze._maze)]
        if not reachable:
            return self.position
        return self.heuristics(target, reachable)
