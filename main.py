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
    vis = Visualizer(start, maze, pixel_math)

    while vis.running:
        vis.set_tick()
        events = pygame.event.get()
        vis.handle_events(events)
        vis.render_frame()

    pygame.quit()

if __name__ == "__main__":
    main()
