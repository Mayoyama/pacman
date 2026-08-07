from mazegenerator import MazeGenerator
from rendering import Visualizer
from typing import NamedTuple
import pygame


class PixelMath(NamedTuple):
    cell_size: int = 20
    padding: int = 10



def main() -> None:
    mazegen = MazeGenerator((16, 16), False, (7, 7), (-1, -1), 0)
    pixel_math = PixelMath()
    maze = mazegen.maze
    start = mazegen.maze_entry

    # Dummy stand-in for real ghost objects. Refactor once ghosts exist:
    # e.g. {ghost.name: ghost.color for ghost in ghosts}
    ghosts: dict[str, tuple[int, int, int]] = {
        "Blinky": (255, 0, 0),
        "Pinky": (255, 184, 255),
        "Inky": (0, 255, 255),
        "Clyde": (255, 184, 82),
    }

    vis = Visualizer(start, maze, pixel_math, ghosts)

    while vis.running:
        vis.set_tick()
        events = pygame.event.get()
        vis.handle_events(events)
        vis.render_frame()

    pygame.quit()

if __name__ == "__main__":
    main()
