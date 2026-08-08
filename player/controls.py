import pygame
from .movement import Direction


def check_keypress(events: list[pygame.event.Event]) -> Direction | None:
    """Checks one frame's events for an arrow-key press.

    Checks every event rather than stopping at the first match, since
    pygame can batch multiple events in one frame.

    Args:
        events: The frame's events, from pygame.event.get().

    Returns:
        The pressed direction's Direction, or None if no arrow key
        was pressed this frame.
    """
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            return Direction.UP
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            return Direction.DOWN
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            return Direction.LEFT
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            return Direction.RIGHT
    return None
