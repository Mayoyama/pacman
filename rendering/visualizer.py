from .settings import UI_state, RenderSettings
from .frame_buffer import FrameBuffer
from  .map_rendering import MapRenderer
import pygame


class Visualizer:
    def __init__(self, start: tuple[int, int],
                 maze: list[list[int]]) -> None:
        """Set up the pygame window and static assets.

        Args:
            start: Start location of pacman.
            maze: Grid representaion of the maze.
        """
        ui_state = UI_state()
        rend_sett = RenderSettings()
        maze_h = len(maze)
        maze_w = len(maze[0])
        self.frame_buff = FrameBuffer((maze_w, maze_h), rend_sett)
        self.map_rend = MapRenderer(maze, self.frame_buff, rend_sett, ui_state)

        pygame.init()
        pygame.display.set_caption("Pacman")


        display_info = pygame.display.Info()
        win_height = int(display_info.current_h * 0.7)
        win_width = int(display_info.current_w * 0.7)
        self.screen = pygame.display.set_mode((win_width, win_height))

        self.running = True
        self.clock = pygame.time.Clock()

    def render_frame(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
        self.frame_buff.lock_memview()
        self.map_rend.render_grid()
        self.frame_buff.unlock_memview()
        self.frame_buff.blit_to_window(self.screen)
        pygame.display.flip()
