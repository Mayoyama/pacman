import pygame
from pathlib import Path


def cell_to_pixel(r: int, c: int, cell_size: int,
                  maze_offset: tuple[int, int]) -> tuple[int, int]:
    """Converts a grid cell's (row, col) to its top-left pixel position.

    Args:
        r: The cell's row index.
        c: The cell's column index.
        cell_size: Width/height of one cell, in pixels.
        maze_offset: (x, y) pixel offset of the maze's top-left corner
            within its surface, accounting for both padding and any
            centering within an oversized surface.

    Returns:
        The (x, y) pixel coordinates of the cell's top-left corner,
        accounting for the image margin and cell size.
    """
    off_x, off_y = maze_offset
    x = off_x + (c * cell_size)
    y = off_y + (r * cell_size)
    return x, y


def cell_center(r: int, c: int, cell_size: int,
                maze_offset: tuple[int, int]) -> tuple[int, int]:

    """Converts a grid cell's (row, col) to its center pixel position.

    Args:
        r: The cell's row index.
        c: The cell's column index.
        cell_size: Width/height of one cell, in pixels.
        maze_offset: (x, y) pixel offset of the maze's top-left corner
            within its surface - see cell_to_pixel for details.

    Returns:
        The (x, y) pixel coordinates of the cell's center point.
    """
    x, y = cell_to_pixel(r, c, cell_size, maze_offset)
    return x + cell_size // 2, y + cell_size // 2


def fill(base: pygame.Surface,
         color: tuple[int, int, int], alpha: int = 255) -> None:
    """Fills every pixel of `base` with a solid color, in place.

    Args:
        base: The surface to fill. Modified directly - not copied,
            nothing is returned.
        color: RGB fill color.
        alpha: Alpha value (0-255) applied to every pixel.
    """

    dst = memoryview(base.get_buffer())
    pitch = base.get_pitch()
    w, h = base.get_size()
    r, g, b = color
    for y in range(h):
        for x in range(w):
            offset = (y * pitch) + (x * 4)
            dst[offset + 0] = b
            dst[offset + 1] = g
            dst[offset + 2] = r
            dst[offset + 3] = alpha
    dst.release()

 
def make_placeholder(size: tuple[int, int],
                      color: tuple[int, int, int]) -> pygame.Surface:
    """Plain filled square, used when a sprite PNG fails to load."""
    surf = pygame.Surface(size, pygame.SRCALPHA, 32)
    fill(surf, color)
    return surf


def load_image_or_fallback(caller: str, path: Path,
                            fallback: pygame.Surface) -> pygame.Surface:
    """Loads `path` as a Surface; returns `fallback` if unreadable."""
    try:
        return pygame.image.load(path).convert_alpha()
    except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
        print(f"Rendering error in {caller} loading {path}: {e}")
        return fallback


