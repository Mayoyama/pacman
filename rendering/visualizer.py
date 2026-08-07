from .settings import UI_state, RenderSettings
from .frame_buffer import FrameBuffer
from  .map_rendering import MapRenderer
from .sprite_rendering import Sprites
import pygame


class Visualizer:
    def __init__(self, start: tuple[int, int],
                 maze: list[list[int]],
                 pixel_math: tuple[int, int],
                 ghosts: dict[str, tuple[int, int, int]]) -> None:
        """Set up the pygame window and static assets.

        Args:
            start: Start location of pacman.
            maze: Grid representaion of the maze.
        """
        pygame.init()
        pygame.display.set_caption("Pacman")

        self.ui_state = UI_state()
        self.rend_sett = RenderSettings()
        maze_h = len(maze)
        maze_w = len(maze[0])
        self.frame_buff = FrameBuffer((maze_w, maze_h), self.rend_sett, pixel_math)
        self.map_rend = MapRenderer(maze, self.frame_buff, self.rend_sett, self.ui_state, pixel_math)

        self.refresh_static_layer()

        display_info = pygame.display.Info()
        win_height = int(display_info.current_h * 0.7)
        win_width = int(display_info.current_w * 0.7)
        self.screen = pygame.display.set_mode((win_width, win_height))

        self.sprites = Sprites()
        self.sprites.build_colored_ghosts(ghosts)

        self.running = True
        self.clock = pygame.time.Clock()

    def set_tick(self) -> None:
        """Advances the frame clock by one tick, capped at target_fps."""
        self.clock.tick(self.rend_sett.target_fps)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Processes window-level events, such as closing the window.

        Args:
            events: The frame's events, from pygame.event.get().
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def refresh_static_layer(self) -> None:
        """Renders the static maze (walls + logo) and caches it.

        Call once after construction, and again whenever the maze changes
        (e.g. a new level via MapRenderer.update_grid), so render_frame()
        can cheaply restore this cached layer each frame instead of
        redrawing the whole maze from scratch.
        """
        self.frame_buff.lock_memview()
        self.frame_buff.clear_map()
        self.map_rend.render_grid()
        self.frame_buff.unlock_memview()
        self.frame_buff.save_snapshot()

    def render_frame(self) -> None:
        """Draws one frame: restores the cached maze, then blits to window."""
        self.frame_buff.blit_snapshot()
        self.frame_buff.blit_to_window(self.screen)
        self.sprites.render_sprites(self.screen)
        pygame.display.flip()
