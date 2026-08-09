from .settings import RenderSettings, PixelMath
from .rendering_utils import cell_to_pixel
import pygame


class FrameBuffer:
    """Owns the pixel surface the maze and gameplay are drawn onto."""

    def __init__(self, dimensions: tuple[int, int],
                 rend_settings: RenderSettings,
                 pixel_math: PixelMath) -> None:
        """Allocates the drawing surface sized for the given maze.

        Args:
            dimensions: (maze_w, maze_h) in cells.
            rend_settings: Shared rendering configuration.
            pixel_math: (cell_size, padding) shared rendering constants.
        """
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
        self.snapshot: pygame.Surface | None = None
        self.maze_surf_loc: pygame.Rect | None = None

    def get_maze_location(self) -> pygame.Rect:
        """Returns the maze surface's current on-screen Rect.

        Returns:
            The Rect last set by blit_maze_to_win(), giving the maze's
            top-left offset within the window.
        """
        assert self.maze_surf_loc is not None, "self.maze_surf_loc is None"
        return self.maze_surf_loc

    def put_pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """Renders pixels to the screen, based on RGBA values"""
        if self.data is not None:
            offset = (y * self.size_line) + (x * 4)
            self.data[offset + 0] = color[2]
            self.data[offset + 1] = color[1]
            self.data[offset + 2] = color[0]
            self.data[offset + 3] = 255
        else:
            raise ValueError("Put_pixel: illegal call with "
                             "[self.data is None]")

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

    def clear_maze(self) -> None:
        """Fills the entire image buffer with black, erasing any
        previously rendered maze, path, or sprite before a redraw.
        """
        for y in range(self.surf_h):
            for x in range(self.surf_w):
                self.put_pixel(x, y, (0, 0, 0))

    def fill_cell(self, r: int, c: int, color: tuple[int, int, int]) -> None:
        """Fills every pixel within one cell with a solid color.

        Args:
            r: The cell's row index.
            c: The cell's column index.
            color: RGB fill color.
        """
        x, y = cell_to_pixel(r, c, self.cell_size, self.padding)
        for r_offset in range(1, self.cell_size - 1):
            for c_offset in range(1, self.cell_size - 1):
                self.put_pixel(x + c_offset, y + r_offset, color)

    def blit_maze_to_win(self, win_surf: pygame.Surface) -> None:
        """Centers and blits the maze surface onto the window.

        Args:
            win_surf: The window surface to blit onto.
        """
        avail_height = (win_surf.get_height() - self.rend_set.top_hud_height
                        - self.rend_set.btm_hud_height)
        mid: tuple[int, int] = (win_surf.get_width() // 2,
                                self.rend_set.top_hud_height
                                + (avail_height // 2))
        self.maze_surf_loc = self.surf.get_rect(center=mid)
        win_surf.blit(self.surf, self.maze_surf_loc)

    def save_maze_snapshot(self) -> None:
        """Copies the current maze surface into self.snapshot.

        Called once after the static maze is drawn, so render_frame()
        can cheaply restore it each frame via blit_maze_snapshot()
        instead of redrawing the whole maze from scratch.
        """
        self.snapshot = pygame.Surface((self.surf_w, self.surf_h),
                                       pygame.SRCALPHA, 32)
        src = memoryview(self.surf.get_buffer())  # type: ignore[arg-type]
        dst = memoryview(self.snapshot.get_buffer())  # type: ignore[arg-type]
        dst[:] = src[:]
        src.release()
        dst.release()

    def blit_maze_snapshot(self) -> None:
        """Restores the cached static maze onto self.surf for this frame."""
        assert self.snapshot is not None, ("blit_maze_snapshot: "
                                           "snapshot is None")
        self.surf.blit(self.snapshot, (0, 0))

    def lock_maze_memview(self) -> None:
        """Opens direct pixel access to self.surf via self.data.

        Must be paired with unlock_maze_memview() before self.surf can
        be blitted anywhere - pygame refuses to blit a surface while
        something still holds a buffer view into it.
        """
        self.data = memoryview(
                    self.surf.get_buffer())  # type: ignore[arg-type]

    def unlock_maze_memview(self) -> None:
        """Releases the direct pixel access opened by lock_maze_memview()."""
        assert self.data is not None, ("Unlock_maze_memview: illegal call "
                                       "with [self.data is None]")
        self.data.release()
        self.data = None
