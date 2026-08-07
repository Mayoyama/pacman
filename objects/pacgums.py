class Gummis:
    def __init__(self, maze: list[list[int]],
                 start: tuple[int, int]) -> None:
        self.start = start
        self.superpacgums: set[tuple[int, int]] = set()
        self.set_superpacgums(maze)
        self.pacgums: set[tuple[int, int]] = set()
        self.set_pacgums(maze)

    def set_superpacgums(self, maze: list[list[int]]) -> None:
        one = (0, 0)
        two = (0, len(maze[0]) - 1)
        three = (len(maze) - 1, 0)
        four = (len(maze) - 1, len(maze[0]) - 1)
        self.superpacgums = set([one, two, three, four])

    def set_pacgums(self, maze: list[list[int]]) -> None:
        pacgums = []
        for r in range(0, len(maze)):
            for c in range(0, len(maze[0])):
                if ((r, c) not in self.superpacgums
                    and maze[r][c] != 15 and (r, c) != self.start):
                    pacgums.append((r, c))
        self.pacgums = set(pacgums)

    def pop_superpacgum(self, pos: tuple[int, int]) -> None:
        """pos (r, c) is the superpacgums location to pop"""
        if pos not in self.superpacgums:
            raise ValueError("pop_superpacgum: pos not valid")
        else:
            self.superpacgums.discard((pos))

    def pop_pacgum(self, pos: tuple[int, int]) -> int:
        """pos (r, c) is the pacgums location to pop"""
        if pos not in self.pacgums:
            raise ValueError("pop_pacgum: pos not valid")
        else:
            self.pacgums.discard((pos))
            return (len(self.pacgums))
        
