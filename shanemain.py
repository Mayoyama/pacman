from mazegenerator import MazeGenerator
from rendering import Visualizer
from typing import NamedTuple
from player import check_keypress, Direction, Movement, Player
from objects import Gummis, Blinky, Pinky, Inky, Clyde
import pygame
import math


class PixelMath(NamedTuple):
    """Rendering constants shared everywhere.

    Attributes:
        cell_size: Width/height of one maze cell, in pixels.
        padding: Margin around the maze, in pixels.
    """

    cell_size: int = 22
    padding: int = 10


def main() -> None:
    maze_w = 10
    maze_h = 12
    center = (maze_w // 2, maze_h // 2)
    mazegen = MazeGenerator((maze_w, maze_h), False, center, (-1, -1), 1)
    pixel_math = PixelMath()

    maze = mazegen.maze
    start_col, start_row = mazegen.maze_entry
    start = (start_row, start_col)
    player = Player()
    movement = Movement(start, maze, pixel_math)

    gums = Gummis(maze, start)
    pinky = Pinky(0, 0)
    blinky = Blinky(len(maze[0]) - 1, 0)
    clyde = Clyde(0, len(maze) - 1)
    inky = Inky(len(maze[0]) - 1, len(maze) - 1)

    ghosts: dict[str, tuple[int, int, int]] = {
        "Blinky": blinky.color,
        "Pinky": pinky.color,
        "Inky": inky.color,
        "Clyde": clyde.color,
    }

    # Testing code, offsets to be erased in real version
    bc, br = blinky.curr_pos
    b_offset = (bc, br + 1)
    pc, pr = pinky.curr_pos
    p_offset = (pc + 1, pr + 1)
    ic, ir = inky.curr_pos
    i_offset = (ic - 2, ir - 3)
    ghost_pos: dict[str, tuple[int, int]] = {
        "Blinky": b_offset,
        "Pinky": p_offset,
        "Inky": i_offset,
        "Clyde": clyde.curr_pos,
    }

    vis = Visualizer(start, maze, pixel_math, ghosts)

    last_openness = 1.0  # starts facing right, fully open
    last_dir = Direction.RIGHT.value
    while vis.running:
        vis.set_tick()
        events = pygame.event.get()
        direction = check_keypress(events)
        if direction is not None:
            movement.set_desired_direction(direction)
        movement.update()
        if movement.direction != Direction.PAUSED:
            last_dir = movement.direction.value
            px, py = movement.pixel_pos
            cx, cy = movement.cell_center(*movement.position)
            distance = abs(px - cx) + abs(py - cy)
            fraction = ((movement.cell_size - distance)
                        / (movement.cell_size - movement.tolerance))
            fraction = max(0.0, min(1.0, fraction))
            last_openness = math.sin(math.pi * fraction)
        # else: leave last_openness untouched - frozen at whatever it last was

        if last_openness < 0.33:
            mouth_state = "closed"
        elif last_openness < 0.66:
            mouth_state = "half"
        else:
            mouth_state = "open"

        vis.handle_events(events)
        vis.render_frame(last_dir, ghost_pos, gums.superpacgums,
                         gums.pacgums, movement.pixel_pos, mouth_state)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"ValueError: {e}")
    except AssertionError as e:
        print(f"Internal logic error: {e}")
