from random import randint


class Gummis:
    """Tracks which cells still hold a pacgum or super pacgum."""

    def __init__(self, maze: list[list[int]],
                 start: tuple[int, int], gum_count: int,
                 fill_maze: bool) -> None:
        """Places super pacgums at the four corners, pacgums everywhere else.

        Args:
            maze: Grid representation of the maze.
            start: Pacman's starting (row, col) cell, excluded from gums.
            gum_count: Requested number of pacgums to place, unless
                fill_maze is True.
            fill_maze: If True, fills every eligible cell instead of
                capping at 80% of them.
        """

        self.start = start

        self.superpacgums: set[tuple[int, int]] = set()
        self.set_superpacgums(maze)

        self.pacgums: set[tuple[int, int]] = set()
        self.set_pacgums(maze, gum_count, fill_maze)

    def set_superpacgums(self, maze: list[list[int]]) -> None:
        """Places a super pacgum in each of the maze's four corners.

        Args:
            maze: Grid representation of the maze.
        """

        one = (0, 0)
        two = (0, len(maze[0]) - 1)
        three = (len(maze) - 1, 0)
        four = (len(maze) - 1, len(maze[0]) - 1)

        self.superpacgums = set([one, two, three, four])

    def set_pacgums(self, maze: list[list[int]], number: int,
                    fill_maze: bool = False) -> None:
        """Places a pacgum in every cell not already excluded.

        Excludes super pacgum cells, '42' logo cells (value 15), and
        the start cell.

        Args:
            maze: Grid representation of the maze.
            number: Requested pacgum count - capped at 80% of eligible
                cells unless fill_maze is True.
            fill_maze: If True, ignores number and fills every eligible
                cell instead.
        """

        pacgums: list[tuple[int, int]] = []

        if not fill_maze:
            numb = number

            if number > int((len(maze) * len(maze[0])) * 0.8):
                numb = int((len(maze) * len(maze[0])) * 0.8)

            while len(pacgums) < numb:
                pacgum = (randint(0, len(maze) - 1), randint(
                    0, len(maze[0]) - 1))

                if (pacgum not in self.superpacgums
                        and maze[pacgum[0]][pacgum[1]] != 15
                        and pacgum != self.start
                        and pacgum not in pacgums):
                    pacgums.append(pacgum)

        else:
            for r in range(0, len(maze)):
                for c in range(0, len(maze[0])):
                    if ((r, c) not in self.superpacgums
                            and maze[r][c] != 15 and (r, c) != self.start):
                        pacgums.append((r, c))

        self.pacgums = set(pacgums)

    def pop_superpacgum(self, pos: tuple[int, int]) -> None:
        """pos (r, c) is the superpacgums location to pop"""

        assert pos in self.superpacgums, "pop_superpacgum: pos not valid"

        self.superpacgums.discard((pos))

    def pop_pacgum(self, pos: tuple[int, int]) -> int:
        """pos (r, c) is the pacgums location to pop"""

        assert pos in self.pacgums, "pop_pacgum: pos not valid"

        self.pacgums.discard((pos))

        return (len(self.pacgums))
