from pathlib import Path
import pygame


class Sprites:
    def __init__(self) -> None:
        ASSETS_DIR = Path(__file__).resolve().parent / "assets"
        pacgum_path = ASSETS_DIR / "pacgum.png"
        superpacgum_path = ASSETS_DIR / "super_pacgum.png"
        base_ghost_path = ASSETS_DIR / "ghost_base.png"
        try:
            self.pacgum_img = pygame.image.load(pacgum_path).convert_alpha()
            self.superpacgum_img = pygame.image.load(superpacgum_path).convert_alpha()
            self.base_ghost_img = pygame.image.load(base_ghost_path).convert_alpha()
        except (FileNotFoundError, IsADirectoryError, PermissionError) as e:
            print(f"Sprites class error: {e}")

        self.colored_ghosts: dict[str, pygame.Surface] = {}


        self.frightened_bright: pygame.Surface = self.apply_ghost_color(self.base_ghost_img, (0, 0, 255))
        self.frightened_dark: pygame.Surface = self.apply_ghost_color(self.base_ghost_img, (0, 0, 140))

    def apply_ghost_color(self, ghost_surf: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
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
        for name, color in ghosts.items():
            self.colored_ghosts[name] = \
                self.apply_ghost_color(self.base_ghost_img, color)


    def render_sprites(self, target: pygame.Surface) -> None:
        """Draws gummies, pacman, and ghosts for one frame.

        Args:
            target: Surface to blit onto.

        TODO: decide the actual parameter list - gummy position sets,
        pacman's pixel_pos/direction, ghost positions + which color/
        frightened-state each one needs, based on what main.py/Visualizer
        actually has available once wiring happens.
        """

        """
         TEMPORARY: positions are hardcoded and not maze-aligned, just to
        confirm the colorized ghosts actually render. Replace once real
        ghost positions + the FrameBuffer offset are wired in.
        """
        positions = [(50, 50), (150, 50), (50, 150), (150, 150)]
        for (name, surf), pos in zip(self.colored_ghosts.items(), positions):
            target.blit(surf, pos)

        target.blit(self.pacgum_img, (50, 220))
        target.blit(self.superpacgum_img, (150, 220))
