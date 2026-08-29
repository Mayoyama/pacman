def find_safe_entry_cell(w: int, h: int) -> tuple[int, int]:
    """Picks a maze entry cell as close to dead-center as possible,
    without landing on one of the '42' logo's blocked cells.

    If dead-center lands on a logo wall cell, shifts entry one column left.

    Args:
        w: Maze width, in cells.
        h: Maze height, in cells.

    Returns:
        (col, row) entry cell - column first, matching the order the
        mazegenerator package's own entry_cell argument expects.
    """

    logo_pattern = [[1, 0, 0, 0, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 0, 1, 1, 1],
                    [0, 0, 1, 0, 1, 0, 0],
                    [0, 0, 1, 0, 1, 1, 1]]

    def is_logo_cell(c: int, r: int) -> bool:
        """Checks whether grid cell (col c, row r) lands on one of the
        logo's blocked cells, replicating the mazegenerator package's
        own (fixed, seed-independent) centering math.
        """

        center_r = (h - len(logo_pattern)) // 2
        center_c = (w - len(logo_pattern[0])) // 2
        rel_c, rel_r = c - center_c, r - center_r

        if (rel_r >= 0 and rel_r < len(logo_pattern)
                and rel_c >= 0 and rel_c < len(logo_pattern[0])):
            return logo_pattern[rel_r][rel_c] == 1

        return False

    col, row = w // 2, h // 2
    if not is_logo_cell(col, row):
        return (col, row)

    return (col - 1, row)
