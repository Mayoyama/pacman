from mazegenerator import MazeGenerator
from rendering import Visualizer

import pygame


def main() -> None:
    mazegen = MazeGenerator((16, 16), False, (7, 7), (-1, -1), 0)
    
    maze = mazegen.maze
    start = mazegen.maze_entry
    vis = Visualizer(start, maze)

    if not vis.running:
            return


    while vis.running:
        vis.clock.tick(30)
        vis.render_frame()
        pygame.quit()

if __name__ == "__main__":
    main()
