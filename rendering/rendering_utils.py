def cell_to_pixel(r: int, c: int, cell_size: int,
                  padding: int) -> tuple[int, int]:
    """Converts a grid cell's (row, col) to its top-left pixel position.

    Args:
        r: The cell's row index.
        c: The cell's column index.
        cell_size: Width/height of one cell, in pixels.
        padding: Margin around the maze, in pixels.

    Returns:
        The (x, y) pixel coordinates of the cell's top-left corner,
        accounting for the image margin and cell size.
    """
    x = padding + (c * cell_size)
    y = padding + (r * cell_size)
    return x, y


def cell_center(r: int, c: int, cell_size: int,
                padding: int) -> tuple[int, int]:

    """Converts a grid cell's (row, col) to its center pixel position.

    Args:
        r: The cell's row index.
        c: The cell's column index.

    Returns:
        The (x, y) pixel coordinates of the cell's center point.
    """
    x, y = cell_to_pixel(r, c, cell_size, padding)
    return x + cell_size // 2, y + cell_size // 2
