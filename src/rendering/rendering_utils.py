import pygame
from pathlib import Path
from sys import stderr
from typing import cast, Any


def cell_to_pixel(r: int, c: int, cell_size: int, maze_offset: tuple[int, int]
                  ) -> tuple[int, int]:
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


def cell_center(r: int, c: int, cell_size: int, maze_offset: tuple[int, int]
                ) -> tuple[int, int]:
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


def fill(base: pygame.surface.Surface, color: tuple[int, int, int],
         alpha: int = 255) -> None:
    """Fills every pixel of `base` with a solid color, in place.

    Args:
        base: The surface to fill. Modified directly - not copied,
            nothing is returned.
        color: RGB fill color.
        alpha: Alpha value (0-255) applied to every pixel.
    """

    dst = memoryview(cast(Any, base.get_buffer()))
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


def recolor_sprite(sprite_surf: pygame.surface.Surface,
                   new_color: tuple[int, int, int],
                   base_color: tuple[int, int, int] = (255, 255, 255)
                   ) -> pygame.surface.Surface:
    """Returns a new surface: base's silhouette recolored to `new_color`.

    Loops every pixel of `sprite_surf`. Wherever its color exactly
    matches `base_color`, writes `new_color` into the new surface at
    that pixel (keeping the original alpha). Wherever alpha is zero,
    the new surface stays transparent there (its default state).

    Only works cleanly on flat, non-anti-aliased fills - any pixel
    whose color was softened by anti-aliasing (e.g. a blended edge)
    won't exactly match `base_color` and is left untouched, which can
    leave a faint fringe of the original color around recolored edges.

    Args:
        sprite_surf: Source surface to recolor - not modified in place.
        new_color: RGB color to replace `base_color` pixels with.
        base_color: RGB color to match against, defaults to white.
    """

    new_surf = pygame.surface.Surface(
        sprite_surf.get_size(), pygame.SRCALPHA, 32)

    src = memoryview(cast(Any, sprite_surf.get_buffer()))
    dst = memoryview(cast(Any, new_surf.get_buffer()))

    pitch = sprite_surf.get_pitch()
    w, h = sprite_surf.get_size()

    for y in range(h):
        for x in range(w):
            offset = (y * pitch) + (x * 4)
            b, g, r, a = src[offset:offset + 4]
            if (r, g, b) == base_color and a != 0:
                dst[offset + 0] = new_color[2]
                dst[offset + 1] = new_color[1]
                dst[offset + 2] = new_color[0]
                dst[offset + 3] = a
            else:
                dst[offset + 0] = b
                dst[offset + 1] = g
                dst[offset + 2] = r
                dst[offset + 3] = a

    src.release()
    dst.release()

    return new_surf


def build_colored_ghosts(ghosts: dict[str, tuple[int, int, int]],
                         base: pygame.Surface, ) -> dict[str, pygame.Surface]:
    """Builds and caches one recolored ghost surface per name.

    Args:
        ghosts: Name-to-RGB-color map, one entry per ghost.
        base: Source ghost surface each color is recolored from.
    """

    colored_ghosts: dict[str, pygame.Surface] = {}

    for name, color in ghosts.items():
        colored_ghosts[name] = recolor_sprite(base, color)

    return colored_ghosts


def copy_surface_info(src: pygame.Surface, dst: pygame.Surface) -> None:
    """Copies one surface's raw pixel data onto another of equal or larger
    size.

    Args:
        src: Surface to copy from.
        dst: Surface to copy into - must be at least as large as src.
    """

    src_w, src_h = src.get_size()
    dst_w, dst_h = dst.get_size()

    if dst_w < src_w or dst_h < src_h:
        print("copy_surface_info: Invalid call, dst too small. "
              "Defaulting to src.", file=stderr)
        return

    src_data = memoryview(cast(Any, src.get_buffer()))
    dst_data = memoryview(cast(Any, dst.get_buffer()))

    dst_data[:] = src_data[:]

    dst_data.release()
    src_data.release()


def make_placeholder(size: tuple[int, int], color: tuple[int, int, int]
                     ) -> pygame.surface.Surface:
    """Plain filled square, used when a sprite PNG fails to load."""

    surf = pygame.Surface(size, pygame.SRCALPHA, 32)
    fill(surf, color)

    return surf


def load_image_or_fallback(caller: str, path: Path,
                           fallback: pygame.surface.Surface
                           ) -> pygame.surface.Surface:
    """Loads `path` as a Surface; returns `fallback` if unreadable."""

    try:
        return pygame.image.load(path).convert_alpha()
    except (FileNotFoundError, IsADirectoryError, PermissionError,
            TypeError) as e:
        print(f"Rendering error in {caller} loading {path}: {e}. "
              "Defaulting to fallback image", file=stderr)
        return fallback
