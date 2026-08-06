import pygame
from .movement import Direction

def check_keypress(events: list[pygame.event.Event]) -> Direction | None:
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




