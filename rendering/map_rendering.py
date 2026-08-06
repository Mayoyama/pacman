from .frame_buffer import FrameBuffer
from .settings import RenderSettings, UI_state


class MapRenderer:
    def __init__(self, maze: list[list[int]], frame_buffer: FrameBuffer,
                 render_setting: RenderSettings, ui_state: UI_state,
                 pixel_math: tuple[int, int]) -> None:
        self.cell_size, _ = pixel_math
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
        ft_cell_list: list[tuple[int, int]] = []
        for r in range(0, len(self.maze)):
            for c in range(0, len(self.maze[0])):
                if self.maze[r][c] == 15:
                    ft_cell_list.append((r, c))
        return ft_cell_list
                        

    def _draw_cell(self, x: int, y: int, cell: int) -> None:
        """Checks the binary values (LSB) and draws walls if they exist"""
        if self._has_N_wall(cell):
            self.frame_buff.draw_horizontal_line(x, y, self.cell_size, self.ui.wall_color)
        if self._has_E_wall(cell):
            self.frame_buff.draw_vertical_line(x + self.cell_size, y, self.cell_size, self.ui.wall_color)
        if self._has_S_wall(cell):
            self.frame_buff.draw_horizontal_line(x, y + self.cell_size, self.cell_size, self.ui.wall_color)
        if self._has_W_wall(cell):
            self.frame_buff.draw_vertical_line(x, y, self.cell_size, self.ui.wall_color)

    def render_grid(self) -> None:
        """Renders walls and logo, """
        for r in range(len(self.maze)):
            for c in range(len(self.maze[0])):
                cell = self.maze[r][c]
                x, y = self.frame_buff.cell_to_pixel(r, c)
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
