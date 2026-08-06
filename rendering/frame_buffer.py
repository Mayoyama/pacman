from .settings import RenderSettings
import pygame


class FrameBuffer:
    def __init__(self, dimensions: tuple[int, int],
                 rend_settings: RenderSettings,
                 pixel_math: tuple[int, int]) -> None:
        self.cell_size, self.padding = pixel_math
        self.maze_w, self.maze_h = dimensions
        self.rend_set = rend_settings
        self.surf_w = ((2 * self.padding)
                       + (self.maze_w * self.cell_size))
        self.surf_h = ((2 * self.padding)
                       + (self.maze_h * self.cell_size))
        self.surf = pygame.Surface((self.surf_w, self.surf_h),
                                   pygame.SRCALPHA, 32)
        self.data: memoryview | None = None
        self.size_line = self.surf.get_pitch()

    def cell_to_pixel(self, r: int, c: int) -> tuple[int, int]:
        """Converts a grid cell's (row, col) to its top-left pixel position.

        Args:
            r: The cell's row index.
            c: The cell's column index.

        Returns:
            The (x, y) pixel coordinates of the cell's top-left corner,
            accounting for the image margin and cell size.
        """
        x = self.padding + (c * self.cell_size)
        y = self.padding + (r * self.cell_size)
        return x, y

    def put_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """Renders pixels to the screen, based on RGBA values"""
        if self.data is not None:
            offset = (y * self.size_line) + (x * 4)
            self.data[offset + 0] = color[2]
            self.data[offset + 1] = color[1]
            self.data[offset + 2] = color[0]
            self.data[offset + 3] = 255
        else:
            raise ValueError("Put_pixel: illegal call with [self.data is None]")

    def draw_horizontal_line(self, x: int, y: int, length: int,
                              color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Renders a straight horizontal line to the screen"""
        for i in range(length):
            self.put_pixel(x + i, y, color)

    def draw_vertical_line(self, x: int, y: int, length: int,
                            color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Renders a straight vertical line to the screen"""
        for i in range(length):
            self.put_pixel(x, y + i, color)

    def clear_map(self) -> None:
        """Fills the entire image buffer with black, erasing any
        previously rendered maze, path, or sprite before a redraw.
        """
        for y in range(self.surf_h):
            for x in range(self.surf_w):
                self.put_pixel(x, y, (0, 0, 0))

    def fill_cell(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        """
        Loops to fill in every pixel within a cell. Requires RGB to
        be passed in
        """
        x, y = self.cell_to_pixel(r, c)
        for r_offset in range(1, self.cell_size - 1):
            for c_offset in range(1, self.cell_size - 1):
                self.put_pixel(x + c_offset, y + r_offset, color)

    def blit_to_window(self, win_surf: pygame.Surface) -> None:
        avail_height = (win_surf.get_height() - self.rend_set.top_hud_height
                        - self.rend_set.btm_hud_height)
        mid: tuple[int, int] = (win_surf.get_width() // 2,
                                self.rend_set.top_hud_height
                                + (avail_height // 2))
        surf_loc = self.surf.get_rect(center=mid)
        win_surf.blit(self.surf, surf_loc)

    def lock_memview(self) -> None:
            self.data = memoryview(
                        self.surf.get_buffer())  # type: ignore[arg-type]

    def unlock_memview(self) -> None:
        if self.data is not None:
            self.data.release()
            self.data = None
        else:
            raise ValueError("Unlock_memview: illegal call with [self.data is None]")
