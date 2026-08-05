class MapRenderer:
    def __init__(self, maze: list[list[int]], start: tuple[int, int]) -> None:
        self.maze = maze
        self.start = start

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

    def _draw_cell(self, x: int, y: int, cell: int) -> None:
        """Checks the binary values (LSB) and draws walls if they exist"""
        if self._has_N_wall(cell):
            self._draw_horizontal_line(x, y, self.cell_size)
        if self._has_E_wall(cell):
            self._draw_vertical_line(x + self.cell_size, y, self.cell_size)
        if self._has_S_wall(cell):
            self._draw_horizontal_line(x, y + self.cell_size, self.cell_size)
        if self._has_W_wall(cell):
            self._draw_vertical_line(x, y, self.cell_size)

    def render_grid(self, path_cells: list[tuple[int, int]]) -> None:
        """Renders walls, logo, start/end cells and optional solution path."""
        for r in range(len(self.maze)):
            for c in range(len(self.maze[0])):
                cell = self.maze[r][c]
                x, y = self._cell_to_pixel(r, c)
                self._draw_cell(x, y, cell)

        # self._fill_logo42()
        #if self._ui.show_path:
        #    self.draw_path(path_cells)
        # self._fill_start_cell()
        # self._fill_end_cell()

    def update_grid(self, grid: list[list[int]],
                    fixed_cells: set[tuple[int, int]]) -> None:
        """Replaces the maze grid and '42' pattern cells being rendered.

        Called after the maze has been regenerated so that subsequent
        render calls draw the new layout.

        Args:
            grid: The new maze grid to render.
            fixed_cells: The new set of '42' pattern cell coordinates.
        """
        self._grid = grid
        self._fixed_cells = fixed_cells

    def _fill_logo42(self) -> None:
        """Wrapper function to fill in the cells of the 42 logo"""
        for r, c in self._fixed_cells:
            self._fill_cell(r, c, self._ui.logo42_color)
