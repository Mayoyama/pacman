import pygame
from .movement import Direction


def check_keypress(events: list[pygame.event.Event]) -> Direction | str | None:
    """Checks one frame's events for key presses.

    Checks every event rather than stopping at the first match, since
    pygame can batch multiple events in one frame.

    Args:
        events: The frame's events, from pygame.event.get().

    Returns:
        The pressed direction's Direction, "pause_toggle" if P was
        pressed, "skip_level" if Ctrl+S was pressed, or None if no
        relevant key was pressed this frame.
    """

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                return Direction.UP
            elif event.key == pygame.K_DOWN:
                return Direction.DOWN
            elif event.key == pygame.K_LEFT:
                return Direction.LEFT
            elif event.key == pygame.K_RIGHT:
                return Direction.RIGHT
            elif event.key == pygame.K_p:
                return "pause_toggle"
            elif event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                return "skip_level"
            elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                return "add_life"

    return None
