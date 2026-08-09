from .frame_buffer import FrameBuffer
from .rendering_utils import cell_to_pixel
from .settings import RenderSettings, UI_state, PixelMath


class MapRenderer:
    """Draws the maze's static walls and '42' logo cells."""

    def __init__(self, maze: list[list[int]], frame_buffer: FrameBuffer,
                 render_setting: RenderSettings, ui_state: UI_state,
                 pixel_math: PixelMath) -> None:
        """Sets up the maze reference and derives the '42' logo cells.

        Args:
            maze: Grid representation of the maze to render.
            frame_buffer: Target buffer walls/logo are drawn into.
            render_setting: Shared rendering configuration.
            ui_state: Shared mutable UI colors/toggles.
            pixel_math: (cell_size, padding) shared rendering constants.
        """
        self.cell_size, self.padding = pixel_math
        self.ui = ui_state
        self.frame_buff = frame_buffer
        self.rend_sett = render_setting
        self.maze = maze
        self.ft_cells: list[tuple[int, int]] = self.get_42_cells()

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

    def get_42_cells(self) -> list[tuple[int, int]]:
        """Scans self.maze for '42' logo cells.

        Returns:
            (row, col) of every cell whose value is 15 (all walls set,
            marking it as part of the logo pattern rather than a
            normal corridor).
        """
        ft_cell_list: list[tuple[int, int]] = []
        for r in range(0, len(self.maze)):
            for c in range(0, len(self.maze[0])):
                if self.maze[r][c] == 15:
                    ft_cell_list.append((r, c))
        return ft_cell_list

    def _draw_cell(self, x: int, y: int, cell: int) -> None:
        """Checks the binary values (LSB) and draws walls if they exist"""
        if self._has_N_wall(cell):
            self.frame_buff.draw_horizontal_line(
                x, y, self.cell_size, self.ui.wall_color)
        if self._has_E_wall(cell):
            self.frame_buff.draw_vertical_line(
                x + self.cell_size, y, self.cell_size, self.ui.wall_color)
        if self._has_S_wall(cell):
            self.frame_buff.draw_horizontal_line(
                x, y + self.cell_size, self.cell_size, self.ui.wall_color)
        if self._has_W_wall(cell):
            self.frame_buff.draw_vertical_line(
                x, y, self.cell_size, self.ui.wall_color)

    def render_grid(self) -> None:
        """Draws every cell's walls, then fills in the '42' logo cells."""
        for r in range(len(self.maze)):
            for c in range(len(self.maze[0])):
                cell = self.maze[r][c]
                x, y = cell_to_pixel(r, c, self.cell_size, self.padding)
                self._draw_cell(x, y, cell)

        self._fill_logo42(color=self.ui.logo42_color)

    def update_grid(self, grid: list[list[int]],
                    fixed_cells: list[tuple[int, int]]) -> None:
        """Replaces the maze grid and '42' pattern cells being rendered.

        Called after the maze has been regenerated so that subsequent
        render calls draw the new layout.

        Args:
            grid: The new maze grid to render.
            fixed_cells: The new set of '42' pattern cell coordinates.
        """
        self.maze = grid
        self.ft_cells = fixed_cells

    def _fill_logo42(self, color: tuple[int, int, int]) -> None:
        """Wrapper function to fill in the cells of the 42 logo"""
        for r, c in self.ft_cells:
            self.frame_buff.fill_cell(r, c, color)
