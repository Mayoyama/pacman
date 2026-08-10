def check_collision(pos_a: tuple[int, int], pos_b: tuple[int, int],
                    threshold: int) -> bool:
    """Checks whether two pixel positions are close enough to count
    as a collision.

    Only counts a hit if aligned on one axis and close along the other -
    a cross/plus shape, not a circle or square, so diagonal proximity never
    counts (see the design notes for why).

    Args:
        pos_a: First entity's (x, y) pixel position.
        pos_b: Second entity's (x, y) pixel position.
        threshold: Max distance along the shared axis still considered
            touching (e.g. same row, how close on x counts as a hit).
            alignment_tolerance (below) is a separate, tighter check -
            how close on the *other* axis counts as actually being in
            that same row/column at all, not just nearby.

    Returns:
        True if within threshold, False otherwise.
    """

    alignment_tolerance = 6
    ax, ay = pos_a
    bx, by = pos_b

    if abs(bx - ax) < threshold and abs(by - ay) <= alignment_tolerance:
        return True
    if abs(by - ay) < threshold and abs(bx - ax) <= alignment_tolerance:
        return True
    return False
