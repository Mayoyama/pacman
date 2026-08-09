from .settings import UI_state, RenderSettings, PixelMath, SpriteRenderState
from .frame_buffer import FrameBuffer
from .map_rendering import MapRenderer
from .sprite_rendering import Sprites
import pygame


class Visualizer:
    """Owns the pygame window and drives per-frame rendering.

    Class Attributes:
        SCREEN_FRACTION: Fraction of the screen resolution the window
            may use at most, leaving room for the taskbar/panel.
        MAX_DESIGN_COLS: Design ceiling (not a technical limit) for
            maze width in cells, used to size the window once for the
            whole game.
        MAX_DESIGN_ROWS: Design ceiling (not a technical limit) for
            maze height in cells, used the same way as MAX_DESIGN_COLS.
    """

    SCREEN_FRACTION = 0.85
    MAX_DESIGN_COLS = 45
    MAX_DESIGN_ROWS = 30

    def __init__(self, start: tuple[int, int],
                 maze: list[list[int]],
                 pixel_math: PixelMath,
                 ghosts: dict[str, tuple[int, int, int]]) -> None:
        """Set up the pygame window and static assets.

        cell_size/padding are fixed for the whole game, so the window
        is sized once here and never touched again: big enough for a
        maze at the design ceiling, capped by the screen itself so it
        never overflows onto the taskbar/panel.

        Args:
            start: Start location of pacman.
            maze: Grid representation of the maze.
            pixel_math: (cell_size, padding) shared rendering constants.
            ghosts: Name-to-color map used to build the cached colored
                ghost surfaces once, at startup.
        """
        pygame.init()
        pygame.display.set_caption("Pacman")

        self.ui_state = UI_state()
        self.rend_sett = RenderSettings()

        cell_size, padding = pixel_math
        display_info = pygame.display.Info()
        screen_w = int(display_info.current_w * self.SCREEN_FRACTION)
        screen_h = int(display_info.current_h * self.SCREEN_FRACTION)

        design_w = (self.MAX_DESIGN_COLS * cell_size) + (2 * padding)
        design_h = ((self.MAX_DESIGN_ROWS * cell_size) + (2 * padding)
                    + self.rend_sett.top_hud_height
                    + self.rend_sett.btm_hud_height)
        win_w = min(screen_w, design_w)
        win_h = min(screen_h, design_h)

        maze_h = len(maze)
        maze_w = len(maze[0])
        self.frame_buff = FrameBuffer(
            (maze_w, maze_h), self.rend_sett, pixel_math)
        self.map_rend = MapRenderer(
            maze, self.frame_buff, self.rend_sett, self.ui_state, pixel_math)

        self.refresh_static_layer()

        self.screen = pygame.display.set_mode((win_w, win_h))

        self.sprites = Sprites(pixel_math)
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
        self.frame_buff.lock_maze_memview()
        self.frame_buff.clear_maze()
        self.map_rend.render_grid()
        self.frame_buff.unlock_maze_memview()
        self.frame_buff.save_maze_snapshot()

    def render_frame(self, sprite_state: SpriteRenderState, died: bool,
                     death_step: int) -> None:
        """Draws one frame: restores the cached maze, then blits to window.

        Args:
            sprite_state: This frame's pacman/ghost/pacgum animation
                state - see SpriteRenderState for field details.
                Untouched here, just forwarded to Sprites.render_sprites.
            died: Whether pacman has died this frame (dev-mode: any
                collision counts as death).
            death_step: Which sprite in the death sequence is currently
                showing, if died is True.
        """
        self.screen.fill((0, 0, 0))
        self.frame_buff.blit_maze_snapshot()
        self.frame_buff.blit_maze_to_win(self.screen)
        maze_offset = self.frame_buff.get_maze_location()
        self.sprites.render_sprites(self.screen, maze_offset, sprite_state,
                                    died, death_step)
        pygame.display.flip()
