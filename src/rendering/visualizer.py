from .settings import (UI_state, RenderSettings, PixelMath,
                       SpriteRenderState, MenuState, HUDState)
from .frame_buffer import FrameBuffer
from .map_rendering import MapRenderer
from .menu_rendering import MenuRender
from .instructions import InstructionsRenderer
from .highscores import ScoreBoardRender
from .HUD_rendering import HUD
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
        COLOR_PALETTE: Per-level wall/'42' logo colors, cycled by index -
            in order: lime green, sky blue, coral red, amber, purple,
            teal, pink, periwinkle blue, brown, pale lime.
    """

    SCREEN_FRACTION = 0.85
    MAX_DESIGN_COLS = 45
    MAX_DESIGN_ROWS = 30
    COLOR_PALETTE = [
        (150, 255, 0), (0, 200, 255), (255, 80, 80), (255, 190, 0),
        (180, 90, 255), (0, 255, 170), (255, 110, 190), (110, 150, 255),
        (150, 90, 60), (225, 255, 180),
    ]

    def __init__(self, maze: list[list[int]],
                 ghosts: dict[str, tuple[int, int, int]],
                 screen_size: tuple[int, int], gum_points: int,
                 sgum_points: int, ghost_points: int,
                 level_index: int) -> None:
        """Set up the pygame window and static assets.

        cell_size/padding are fixed for the whole game, so the window
        is sized once here and never touched again: big enough for a
        maze at the design ceiling, capped by the screen itself so it
        never overflows onto the taskbar/panel.

        Args:
            maze: Grid representation of the maze.
            ghosts: Name-to-color map used to build the cached colored
                ghost surfaces once, at startup.
            screen_size: (width, height) of the display, in pixels.
            gum_points: Score awarded per pacgum, shown on the
                instructions screen.
            sgum_points: Score awarded per super-pacgum, shown on the
                instructions screen.
            ghost_points: Score awarded per edible ghost, shown on the
                instructions screen.
            level_index: Current level number, used to pick this level's
                wall/'42' logo colors from COLOR_PALETTE.
        """

        pygame.init()
        pygame.display.set_caption("Pacman")

        self.ui_state = UI_state()
        self.rend_sett = RenderSettings()

        self.pixel_math = PixelMath()
        cell_size, padding = self.pixel_math

        self.ui_state.wall_color = \
            self.COLOR_PALETTE[level_index % len(self.COLOR_PALETTE)]
        self.ui_state.logo42_color = \
            self.COLOR_PALETTE[(level_index + 2) % len(self.COLOR_PALETTE)]

        screen_w = int(screen_size[0] * self.SCREEN_FRACTION)
        screen_h = int(screen_size[1] * self.SCREEN_FRACTION)

        design_w = (self.MAX_DESIGN_COLS * cell_size) + (2 * padding)
        design_h = ((self.MAX_DESIGN_ROWS * cell_size)
                    + (2 * padding)
                    + self.rend_sett.top_hud_h
                    + self.rend_sett.btm_hud_h)

        win_w = min(screen_w, design_w)
        win_h = min(screen_h, design_h)

        maze_h = len(maze)
        maze_w = len(maze[0])

        self.frame_buff = FrameBuffer(
            (maze_w, maze_h), (self.MAX_DESIGN_COLS, self.MAX_DESIGN_ROWS),
            self.rend_sett, self.pixel_math)

        self.map_rend = MapRenderer(
            maze, self.frame_buff, self.rend_sett, self.ui_state,
            self.pixel_math, self.get_maze_offset())

        self.refresh_static_layer()

        self.screen = pygame.display.set_mode((win_w, win_h))

        self.menu_rend = MenuRender(win_w, win_h)
        self.scoreboard = ScoreBoardRender(win_w, win_h)
        self.instruction = InstructionsRenderer(win_w, win_h, gum_points,
                                                sgum_points, ghost_points)

        self.sprites = Sprites(self.pixel_math, self.get_maze_offset(), ghosts)

        self.running = True
        self.clock = pygame.time.Clock()

        self.hud = HUD(self.rend_sett, ghosts, win_w, win_h)

    def set_tick(self) -> None:
        """Advances the frame clock by one tick, capped at target_fps."""

        self.clock.tick(self.rend_sett.target_fps)

    def get_maze_offset(self) -> tuple[int, int]:
        """Returns the maze's centering offset within its own surface."""

        return self.frame_buff.get_maze_surf_center()

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
                     death_step: int, hud_data: HUDState) -> None:
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

        self.sprites.render_sprites(
            self.screen, maze_offset, sprite_state, died, death_step)

        self.hud.render_maze_logo(self.screen)

        maze_bounds = self.frame_buff.get_maze_boundaries()
        self.hud.render_hud(self.screen, hud_data, maze_bounds.midbottom,
                            maze_bounds.midtop)

        pygame.display.flip()

    def reset_pac_sprite(self, direction: str) -> None:
        """Resets pacman's animation state after respawning.

        Args:
            direction: Direction value to face after respawn.
        """

        self.sprites.last_openness = 1.0
        self.sprites.last_direction = direction
        self.sprites.mouth_state = "open"

    def render_menus(self, menu_data: MenuState,
                     highscores: list[tuple[str, int, int]]) -> None:
        """Draws whichever menu screen is currently active.

        Args:
            menu_data: The active menu's items and selection state.
            highscores: Loaded highscores, for the high-scores screen.
        """

        if menu_data.curr_menu == "MAIN":
            self.menu_rend.render_main_menu(
                self.screen, menu_data.main_menu_items,
                menu_data.menu_pos)

        elif menu_data.curr_menu == "OPTIONS":
            self.menu_rend.render_options_menu(
                self.screen, menu_data.options_menu_items,
                menu_data.menu_pos)

        elif menu_data.curr_menu == "HIGH SCORES":
            self.scoreboard.render_highscores(self.screen, highscores)

        elif menu_data.curr_menu == "INSTRUCTIONS":
            self.instruction.render_instructions(self.screen)

        pygame.display.flip()

    def handle_end_screen(self, lost_game: bool, score: int,
                          animating: bool = True) -> str:
        """Runs the death animation, then the name-entry loop, for game end.

        Args:
            lost_game: True for a game-over screen, False for victory.
            score: Final score to display.
            animating: If True, will play an animation before getting name.

        Returns:
            The name the player typed and confirmed, or "" if the window
            closed before they finished.
        """

        death_step = 0
        death_timer = 0
        death_frames = [18, 9, 5, 3, 1, 90]

        pac_x = -300
        speed = 3
        end_x = 300

        typed = ""
        warning = ""

        while self.running:
            self.set_tick()

            events = pygame.event.get()
            self.handle_events(events)

            if animating:
                if lost_game:
                    if death_timer >= death_frames[death_step]:
                        death_timer = 0

                        if death_step < len(death_frames) - 1:
                            death_step += 1
                        else:
                            animating = False

                    else:
                        death_timer += 1

                else:
                    if pac_x < end_x:
                        pac_x = min(pac_x + speed, end_x)

                    else:
                        animating = False

            else:
                for e in events:
                    if e.type != pygame.KEYDOWN:
                        continue

                    if e.key == pygame.K_ESCAPE:
                        return ""

                    if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if 3 <= len(typed) <= 10:
                            return typed
                        warning = "Name must be 3-10 characters"
                    elif e.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]
                        warning = ""
                    elif ((e.unicode.isalnum() or e.unicode == ' ')
                            and len(typed) < 10):
                        typed += e.unicode
                        warning = ""

            if lost_game:
                self.hud.render_gameover(
                    self.screen, death_step, animating, typed, warning, score)
            else:
                self.hud.render_victory(self.screen, pac_x, animating,
                                        typed, warning, score)

            pygame.display.flip()

        return ""

    def handle_lv_done(self) -> None:
        """Blocks for 4 seconds, showing the level-complete splash."""

        splash_frames = 4 * self.rend_sett.target_fps

        while splash_frames > 0:
            self.set_tick()
            events = pygame.event.get()
            self.handle_events(events)
            self.hud.render_lv_complete_splash(self.screen)
            pygame.display.flip()
            splash_frames -= 1
