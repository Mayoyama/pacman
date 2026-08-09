from pathlib import Path
from .rendering_utils import cell_center
from .settings import PixelMath, SpriteRenderState
import pygame


class Sprites:
    """Loads sprite assets and recolors/draws them each frame."""

    def __init__(self, pixel_math: PixelMath) -> None:
        """Loads every sprite asset, builds the per-direction pacman
        frame dict, and derives the frightened-ghost tints.

        Args:
            pixel_math: (cell_size, padding) shared rendering constants.
        """
        self.cell_size, self.padding = pixel_math
        self._load_sprites()
        self.pacsprite_dict = self._build_pacsprite_dict()
        self.deathsprite_list = [self.pac_up_3, self.pac_death_1,
                                 self.pac_death_2, self.pac_death_3,
                                 self.pac_death_4, self.pac_death_blank]

        self.colored_ghosts: dict[str, pygame.Surface] = {}

        self.frightened_bright: pygame.Surface = \
            self.apply_ghost_color(self.base_ghost_img, (0, 0, 255))
        self.frightened_dark: pygame.Surface = \
            self.apply_ghost_color(self.base_ghost_img, (0, 0, 140))

    def _load_sprites(self) -> None:
        """Loads all sprite images, falling back to a placeholder per
        asset family if a file is missing or corrupt, so the game
        doesn't crash.

        Pac-Man frames are named `self.pac_<direction>_<state>`: state
        1 is mouth closed, 2 is half open, 3 is fully open. The closed
        frame is identical for every direction, so all four `_1`
        attributes share one loaded surface.
        """
        ASSETS_DIR = Path(__file__).resolve().parent / "assets"
        pacgum_path = ASSETS_DIR / "pacgum.png"
        superpacgum_path = ASSETS_DIR / "super_pacgum.png"
        base_ghost_path = ASSETS_DIR / "ghost_base.png"

        pac_closed_path = ASSETS_DIR / "pacman_closed.png"
        pac_up_half_path = ASSETS_DIR / "pacman_up_half.png"
        pac_up_open_path = ASSETS_DIR / "pacman_up_open.png"
        pac_down_half_path = ASSETS_DIR / "pacman_down_half.png"
        pac_down_open_path = ASSETS_DIR / "pacman_down_open.png"
        pac_left_half_path = ASSETS_DIR / "pacman_left_half.png"
        pac_left_open_path = ASSETS_DIR / "pacman_left_open.png"
        pac_right_half_path = ASSETS_DIR / "pacman_right_half.png"
        pac_right_open_path = ASSETS_DIR / "pacman_right_open.png"

        pac_death_1_path = ASSETS_DIR / "pacman_death_1.png"
        pac_death_2_path = ASSETS_DIR / "pacman_death_2.png"
        pac_death_3_path = ASSETS_DIR / "pacman_death_3.png"
        pac_death_4_path = ASSETS_DIR / "pacman_death_4.png"
        pac_death_blank_path = ASSETS_DIR / "pacman_death_blank.png"

        # ghost_placeholder must stay pure white - apply_ghost_color only
        # recolors exact white pixels, so any other color would silently
        # mis-render every ghost.
        ghost_placeholder = self._make_placeholder((20, 20), (255, 255, 255))
        gummy_placeholder = self._make_placeholder((20, 20), (255, 255, 0))
        pacman_placeholder = self._make_placeholder((20, 20), (255, 255, 0))

        self.pacgum_img = self._load_image_or_fallback(
            pacgum_path, gummy_placeholder)
        self.superpacgum_img = self._load_image_or_fallback(
            superpacgum_path, gummy_placeholder)
        self.base_ghost_img = self._load_image_or_fallback(
            base_ghost_path, ghost_placeholder)

        self.pac_closed = self._load_image_or_fallback(
            pac_closed_path, pacman_placeholder)
        self.pac_up_1 = self.pac_closed
        self.pac_down_1 = self.pac_closed
        self.pac_left_1 = self.pac_closed
        self.pac_right_1 = self.pac_closed

        self.pac_up_2 = self._load_image_or_fallback(
            pac_up_half_path, pacman_placeholder)
        self.pac_up_3 = self._load_image_or_fallback(
            pac_up_open_path, pacman_placeholder)
        self.pac_down_2 = self._load_image_or_fallback(
            pac_down_half_path, pacman_placeholder)
        self.pac_down_3 = self._load_image_or_fallback(
            pac_down_open_path, pacman_placeholder)
        self.pac_left_2 = self._load_image_or_fallback(
            pac_left_half_path, pacman_placeholder)
        self.pac_left_3 = self._load_image_or_fallback(
            pac_left_open_path, pacman_placeholder)
        self.pac_right_2 = self._load_image_or_fallback(
            pac_right_half_path, pacman_placeholder)
        self.pac_right_3 = self._load_image_or_fallback(
            pac_right_open_path, pacman_placeholder)

        # Death sequence: frame 0 reuses pac_up_open (already loaded above),
        # these are frames 1-4, followed by a fully blank frame.
        self.pac_death_1 = self._load_image_or_fallback(
            pac_death_1_path, pacman_placeholder)
        self.pac_death_2 = self._load_image_or_fallback(
            pac_death_2_path, pacman_placeholder)
        self.pac_death_3 = self._load_image_or_fallback(
            pac_death_3_path, pacman_placeholder)
        self.pac_death_4 = self._load_image_or_fallback(
            pac_death_4_path, pacman_placeholder)
        self.pac_death_blank = self._load_image_or_fallback(
            pac_death_blank_path, pacman_placeholder)

    @staticmethod
    def _make_placeholder(
            size: tuple[int, int],
            color: tuple[int, int, int]) -> pygame.Surface:
        """Plain filled square, used when a sprite PNG fails to load."""
        surf = pygame.Surface(size, pygame.SRCALPHA, 32)
        surf.fill(color)
        return surf

    @staticmethod
    def _load_image_or_fallback(
            path: Path, fallback: pygame.Surface) -> pygame.Surface:
        """Loads `path` as a Surface; returns `fallback` if unreadable."""
        try:
            return pygame.image.load(path).convert_alpha()
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            print(f"Sprites class error loading {path}: {e}")
            return fallback

    def apply_ghost_color(self, ghost_surf: pygame.Surface,
                          color: tuple[int, int, int]) -> pygame.Surface:
        """Returns a new surface: base's silhouette recolored to `color`.

        Loops every pixel of `base`. Wherever its color is pure white,
        writes `color` into the new surface at that pixel (keeping the
        original alpha). Wherever alpha is zero, the new surface stays
        transparent there (its default state).
        """

        new_surf = pygame.Surface(ghost_surf.get_size(), pygame.SRCALPHA, 32)
        src = memoryview(ghost_surf.get_buffer())  # type: ignore[arg-type]
        dst = memoryview(new_surf.get_buffer())  # type: ignore[arg-type]
        pitch = ghost_surf.get_pitch()
        w, h = ghost_surf.get_size()
        for y in range(h):
            for x in range(w):
                offset = (y * pitch) + (x * 4)
                b, g, r, a = src[offset:offset + 4]
                if (r, g, b) == (255, 255, 255) and a != 0:
                    dst[offset + 0] = color[2]
                    dst[offset + 1] = color[1]
                    dst[offset + 2] = color[0]
                    dst[offset + 3] = a
                else:
                    dst[offset + 0] = b
                    dst[offset + 1] = g
                    dst[offset + 2] = r
                    dst[offset + 3] = a
        src.release()
        dst.release()
        return new_surf

    def build_colored_ghosts(self,
                             ghosts: dict[str, tuple[int, int, int]]) -> None:
        """Builds and caches one recolored ghost surface per name.

        Args:
            ghosts: Name-to-RGB-color map, one entry per ghost.
        """
        for name, color in ghosts.items():
            self.colored_ghosts[name] = \
                self.apply_ghost_color(self.base_ghost_img, color)

    def _build_pacsprite_dict(
            self) -> dict[str, tuple[pygame.Surface, pygame.Surface,
                                     pygame.Surface]]:
        """Builds the direction-keyed pacman animation-frame dict.

        Falls back to three copies of the closed frame for any
        direction whose sprites can't be found by name, so a naming
        mismatch degrades gracefully instead of crashing.

        Returns:
            dict mapping "up"/"down"/"left"/"right" to that
            direction's (closed, half, open) frame tuple.
        """
        pacsprites: dict[str, tuple[pygame.Surface, pygame.Surface,
                                    pygame.Surface]] = {}
        for direction in ("up", "down", "left", "right"):
            try:
                sprites: tuple[pygame.Surface, pygame.Surface,
                               pygame.Surface] = \
                  (
                    getattr(self, f"pac_{direction}_1"),
                    getattr(self, f"pac_{direction}_2"),
                    getattr(self, f"pac_{direction}_3")
                  )
            except AttributeError:
                print(f"_build_pacsprite_dict: pac_{direction} img not found."
                      " Defaulting to pac_closed img")
                sprites = (self.pac_closed, self.pac_closed, self.pac_closed)
            pacsprites[direction] = sprites
        return pacsprites

    def render_sprites(self, target: pygame.Surface,
                       maze_offset: pygame.Rect,
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

        Frightened-state ghost tints (self.frightened_bright/_dark) are
        not yet used here - still pending real frightened-state logic.
        """
        off_x, off_y = maze_offset.topleft

        for r, c in sprite_state.superpacgums:
            cx, cy = cell_center(r, c, self.cell_size, self.padding)
            surf_mid = self.superpacgum_img.get_rect(
                center=(cx + off_x, cy + off_y))
            target.blit(self.superpacgum_img, surf_mid)

        for r, c in sprite_state.pacgums:
            cx, cy = cell_center(r, c, self.cell_size, self.padding)
            surf_mid = self.pacgum_img.get_rect(
                center=(cx + off_x, cy + off_y))
            target.blit(self.pacgum_img, surf_mid)

        for name, surf in self.colored_ghosts.items():
            c, r = sprite_state.ghost_pos[name]
            cx, cy = cell_center(r, c, self.cell_size, self.padding)
            surf_mid = surf.get_rect(center=(cx + off_x, cy + off_y))
            target.blit(surf, surf_mid)

        pac_x, pac_y = sprite_state.pacpixel_pos

        if died:
            img = self.deathsprite_list[death_step]
        else:
            mouth_index = {"closed": 0, "half": 1, "open": 2}
            img = self.pacsprite_dict[sprite_state.last_direction][mouth_index[sprite_state.mouth_state]]
        surf_mid = img.get_rect(center=(pac_x + off_x, pac_y + off_y))
        target.blit(img, surf_mid)
