from abc import ABC
from pathlib import Path
from .rendering_utils import make_placeholder, load_image_or_fallback, fill
from .settings import TextObjs
import pygame


class MenuRendBase(ABC):
    """Shared setup (fonts, icons, logo) for the menu-screen renderers."""

    def __init__(self, win_w: int, win_h: int) -> None:
        """Loads menu fonts/sprites and builds the pause-menu overlay surface.

        Args:
            win_w: Window width, in pixels.
            win_h: Window height, in pixels.
        """

        self.win_w = win_w
        self.win_h = win_h

        self.head_white = (200, 200, 200)
        self.yellow = (255, 255, 0)
        self.sel_blue = (0, 0, 205)
        self.vib_blue = (10, 10, 230)
        self.sky_blue = (0, 162, 255)
        self.white = (255, 255, 255)
        self.red = (220, 53, 69)
        self.green = (34, 139, 34)
        self.purple = (117, 7, 135)

        self.large_menu_font = pygame.font.Font(None, 56)
        self.medium_menu_font = pygame.font.Font(None, 36)
        self.small_menu_font = pygame.font.Font(None, 20)

        self._load_menu_sprites()

        self.pause_surf = pygame.Surface((500, 160), pygame.SRCALPHA, 32)
        fill(self.pause_surf, self.sky_blue, 200)

        self.footer = TextObjs(
            self.small_menu_font, "Press ESC to return to the menu", "center",
            self.head_white, (win_w // 2, win_h - 20))

    def _load_menu_sprites(self) -> None:
        """Loads the pacman icon and logo, falling back to placeholders
        if missing.
        """

        ASSETS_DIR = Path(__file__).resolve().parent / "assets"

        pacman_placeholder = make_placeholder((20, 20), self.yellow)
        logo_placeholder = make_placeholder((100, 100), self.yellow)
        frame_placeholder = make_placeholder((1, 1), self.sky_blue)

        self.pac_icon = load_image_or_fallback(
            self.__class__.__name__, ASSETS_DIR / "pacman_right_open.png",
            pacman_placeholder)

        self.mini_frame = load_image_or_fallback(
            self.__class__.__name__, ASSETS_DIR / "mini_menu_frame.png",
            frame_placeholder)

        self.logo = load_image_or_fallback(
            self.__class__.__name__, ASSETS_DIR / "pacman_logo.png",
            logo_placeholder)

        self.screen_y_mid = self.win_h // 4
        self.logo_x_mid = self.win_w // 2
        self.logo_rect = self.logo.get_rect(center=(
            self.logo_x_mid, self.screen_y_mid))
