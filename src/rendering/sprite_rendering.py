from pathlib import Path
from .rendering_utils import (
    cell_center, make_placeholder, load_image_or_fallback, recolor_sprite,
    build_colored_ghosts)
from .settings import PixelMath, SpriteRenderState
import pygame
import math
from sys import stderr


class Sprites:
    """Loads sprite assets and recolors/draws them each frame."""

    def __init__(self, pixel_math: PixelMath,
                 maze_offset: tuple[int, int],
                 ghosts: dict[str, tuple[int, int, int]]) -> None:
        """Loads every sprite asset, builds the per-direction pacman
        frame dict, and derives the frightened-ghost tints.

        Args:
            pixel_math: (cell_size, padding) shared rendering constants.
            maze_offset: (x, y) pixel offset centering the actual maze
                within its (possibly larger) surface.
            ghosts: Name-to-color map used to build the cached colored
                ghost surfaces once, at startup.
        """

        self.cell_size = pixel_math.cell_size
        self.maze_offset = maze_offset

        self._load_sprites()

        self.pacsprite_dict = self._build_pacsprite_dict()

        self.deathsprite_list = [
            self.sprites_dict["pac_up_3"], self.sprites_dict["pac_death_1"],
            self.sprites_dict["pac_death_2"], self.sprites_dict["pac_death_3"],
            self.sprites_dict["pac_death_4"],
            self.sprites_dict["pac_death_blank"]]

        self.colored_ghosts: dict[str, pygame.surface.Surface] = \
            build_colored_ghosts(
                ghosts, self.sprites_dict["base_ghost"])

        self.frightened_bright: pygame.surface.Surface = \
            recolor_sprite(self.sprites_dict["base_ghost"], (0, 0, 255))

        self.frightened_dark: pygame.surface.Surface = \
            recolor_sprite(self.sprites_dict["base_ghost"], (0, 0, 140))

        # Pacman starts facing right, fully open
        self.last_openness: float = 1.0
        self.last_direction = "right"
        self.mouth_state = "open"

    def _load_sprites(self) -> None:
        """Loads all sprite images into self.sprites_dict, falling back
        to a placeholder per asset family if a file is missing or
        corrupt, so the game doesn't crash.

        Pac-Man frames are keyed as `pac_<direction>_<state>`: state
        1 is mouth closed, 2 is half open, 3 is fully open. The closed
        frame is identical for every direction, so all four `_1`
        keys share one loaded surface.
        """

        ASSETS_DIR = Path(__file__).resolve().parent / "assets"

        # ghost_placeholder must stay pure white - recolor_sprite only
        # recolors exact white pixels, so any other color would silently
        # mis-render every ghost.
        ghost_placeholder = make_placeholder((20, 20), (255, 255, 255))
        gummy_placeholder = make_placeholder((20, 20), (255, 255, 0))
        pacman_placeholder = make_placeholder((20, 20), (255, 255, 0))

        self.sprites_dict: dict[str, pygame.surface.Surface] = {}

        specs = [
            ("pacgum", "pacgum.png", gummy_placeholder),
            ("superpacgum", "super_pacgum.png", gummy_placeholder),
            ("base_ghost", "ghost_base.png", ghost_placeholder),
            ("pac_closed", "pacman_closed.png", pacman_placeholder),
            ("pac_up_2", "pacman_up_half.png", pacman_placeholder),
            ("pac_up_3", "pacman_up_open.png", pacman_placeholder),
            ("pac_down_2", "pacman_down_half.png", pacman_placeholder),
            ("pac_down_3", "pacman_down_open.png", pacman_placeholder),
            ("pac_left_2", "pacman_left_half.png", pacman_placeholder),
            ("pac_left_3", "pacman_left_open.png", pacman_placeholder),
            ("pac_right_2", "pacman_right_half.png", pacman_placeholder),
            ("pac_right_3", "pacman_right_open.png", pacman_placeholder),
            ("pac_death_1", "pacman_death_1.png", pacman_placeholder),
            ("pac_death_2", "pacman_death_2.png", pacman_placeholder),
            ("pac_death_3", "pacman_death_3.png", pacman_placeholder),
            ("pac_death_4", "pacman_death_4.png", pacman_placeholder),
            ("pac_death_blank", "pacman_death_blank.png", pacman_placeholder)
        ]

        for name, filename, placeholder in specs:
            self.sprites_dict[name] = load_image_or_fallback(
                self.__class__.__name__,
                ASSETS_DIR / filename, placeholder)

        for direction in ("up", "down", "left", "right"):
            self.sprites_dict[f"pac_{direction}_1"] = \
                self.sprites_dict["pac_closed"]

    def _build_pacsprite_dict(
        self) -> dict[str, tuple[pygame.surface.Surface,
                                 pygame.surface.Surface,
                                 pygame.surface.Surface]]:
        """Builds the direction-keyed pacman animation-frame dict.

        Falls back to three copies of the closed frame for any
        direction whose sprites can't be found by name, so a naming
        mismatch degrades gracefully instead of crashing.

        Returns:
            dict mapping "up"/"down"/"left"/"right" to that
            direction's (closed, half, open) frame tuple.
        """

        pacsprites: dict[str, tuple[pygame.surface.Surface,
                                    pygame.surface.Surface,
                                    pygame.surface.Surface]] = {}

        for direction in ("up", "down", "left", "right"):
            try:
                sprites: tuple[pygame.surface.Surface, pygame.surface.Surface,
                               pygame.surface.Surface] = (
                    self.sprites_dict[f"pac_{direction}_1"],
                    self.sprites_dict[f"pac_{direction}_2"],
                    self.sprites_dict[f"pac_{direction}_3"]
                )
            except KeyError:
                print(f"_build_pacsprite_dict: pac_{direction} img not found."
                      " Defaulting to pac_closed img", file=stderr)
                sprites = (self.sprites_dict["pac_closed"],
                           self.sprites_dict["pac_closed"],
                           self.sprites_dict["pac_closed"])

            pacsprites[direction] = sprites

        return pacsprites

    def render_sprites(self, target: pygame.surface.Surface,
                       maze_offset: pygame.rect.Rect,
                       sprite_state: SpriteRenderState, died: bool,
                       death_step: int) -> None:
        """Draws gummies, pacman, and ghosts for one frame.

        Args:
            target: Surface to blit onto.
            maze_offset: The maze surface's current on-screen Rect,
                used to shift every cell-based position onto the
                window correctly.
            sprite_state: This frame's pacman/ghost/pacgum animation
                state - see SpriteRenderState for field details.
            died: Whether pacman has died this frame (dev-mode: any
                collision counts as death).
            death_step: Which sprite in the death sequence is currently
                showing, if died is True.
        """

        off_x, off_y = maze_offset.topleft
        pac_x, pac_y = sprite_state.pacpixel_pos

        for r, c in sprite_state.superpacgums:
            cx, cy = cell_center(r, c, self.cell_size, self.maze_offset)
            surf_mid = self.sprites_dict["superpacgum"].get_rect(
                center=(cx + off_x, cy + off_y))

            target.blit(self.sprites_dict["superpacgum"], surf_mid)

        for r, c in sprite_state.pacgums:
            cx, cy = cell_center(r, c, self.cell_size, self.maze_offset)
            surf_mid = self.sprites_dict["pacgum"].get_rect(
                center=(cx + off_x, cy + off_y))

            target.blit(self.sprites_dict["pacgum"], surf_mid)

        for name, surf in self.colored_ghosts.items():
            gx, gy = sprite_state.ghost_pos[name]

            if sprite_state.respawn_timers[name] > 0:
                continue
            elif sprite_state.scared_timers[name] > 0:
                if sprite_state.scared_timers[name] < 75:
                    cycle_frames = 10
                    fraction = ((sprite_state.scared_timers[name]
                                % cycle_frames) / cycle_frames)
                    scared_math = math.sin(math.pi * fraction)

                    if scared_math < 2 / 5:
                        scared_frame = self.frightened_dark
                    elif scared_math < 4 / 5:
                        scared_frame = self.frightened_bright
                    else:
                        scared_frame = self.sprites_dict["base_ghost"]

                    surf_mid = scared_frame.get_rect(center=(gx + off_x,
                                                             gy + off_y))
                    target.blit(scared_frame, surf_mid)
                else:
                    surf_mid = self.frightened_dark.get_rect(
                        center=(gx + off_x, gy + off_y))

                    target.blit(self.frightened_dark, surf_mid)
            else:
                surf_mid = surf.get_rect(center=(gx + off_x, gy + off_y))

                target.blit(surf, surf_mid)

        if sprite_state.player_direction != "paused":
            self.last_direction = sprite_state.player_direction

            px, py = sprite_state.pacpixel_pos
            cx, cy = cell_center(
                *sprite_state.player_pos, self.cell_size, self.maze_offset)

            distance = abs(px - cx) + abs(py - cy)
            fraction = ((self.cell_size - distance)
                        / (self.cell_size - sprite_state.tolerance))
            fraction = max(0.0, min(1.0, fraction))

            self.last_openness = math.sin(math.pi * fraction)

            if self.last_openness < 0.33:
                self.mouth_state = "closed"
            elif self.last_openness < 0.66:
                self.mouth_state = "half"
            else:
                self.mouth_state = "open"
            # else: leave last_openness frozen at whatever it was last

        if died:
            img = self.deathsprite_list[death_step]
        else:
            mouth_index = {"closed": 0, "half": 1, "open": 2}
            img = self.pacsprite_dict[self.last_direction][
                mouth_index[self.mouth_state]]

        surf_mid = img.get_rect(center=(pac_x + off_x, pac_y + off_y))

        target.blit(img, surf_mid)
