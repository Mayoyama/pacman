import pygame
from pathlib import Path
from .rendering_utils import make_placeholder, load_image_or_fallback


class MenuRender:
    def __init__(self, win_w, win_h, highscore_filename: str) -> None:
        self.win_w = win_w
        self.win_h = win_h
        self.highscore_filename = highscore_filename
        self._load_menu_sprites()
        self.large_menu_font = pygame.font.Font(None, 56)
        self.medium_menu_font = pygame.font.Font(None, 36)


    def _load_menu_sprites(self) -> None:
        ASSETS_DIR = Path(__file__).resolve().parent / "assets"

        pacman_placeholder = make_placeholder((20, 20), (255, 255, 0))
        logo_placeholder = make_placeholder((100, 100), (255, 255, 0))

        self.pac_icon = load_image_or_fallback(self.__class__.__name__,
                                           ASSETS_DIR / "pacman_right_open.png",
                                           pacman_placeholder)
        self.logo = load_image_or_fallback(self.__class__.__name__,
                                           ASSETS_DIR / "pacman_logo.png",
                                           logo_placeholder)
        self.screen_y_mid = self.win_h // 4
        self.logo_x_mid = self.win_w // 2
        self.logo_rect = self.logo.get_rect(center=(self.logo_x_mid, self.screen_y_mid))

    def render_main_menu(self, target: pygame.Surface, options: list[str],
                         menu_pos: int) -> None:
        target.blit(self.logo, self.logo_rect)
        heading = self.large_menu_font.render("MAIN MENU", False, (200, 200, 200))
        lx,ly = self.logo_rect.midbottom
        heading_y_offset = 60
        heading_rect = heading.get_rect(midtop=(lx, ly + heading_y_offset))
        target.blit(heading, heading_rect)
        _, hy = heading_rect.midbottom
        menu_y_offset = 40
        pac_offset = -25
        for i, option in enumerate(options):
            if i == menu_pos:
                menu_item = self.medium_menu_font.render(option, False, (0, 0, 205))
                menu_item_rect = menu_item.get_rect(midtop=(lx,  hy + ((i + 1) * menu_y_offset)))
                mx, my = menu_item_rect.midleft
                pac_rect = self.pac_icon.get_rect(center=(mx + pac_offset, my))
                target.blit(self.pac_icon, pac_rect)
            else:
                menu_item = self.medium_menu_font.render(option, False, (255, 255, 255))
                menu_item_rect = menu_item.get_rect(midtop=(lx,  hy + ((i + 1) * menu_y_offset)))
            target.blit(menu_item, menu_item_rect)
            
        

    def render_options_menu(self, target: pygame.Surface,
                            options: dict[str, bool], menu_pos: int) -> None:
        target.blit(self.logo, self.logo_rect)
        heading = self.large_menu_font.render("OPTIONS MENU", False, (200, 200, 200))
        lx,ly = self.logo_rect.midbottom
        heading_y_offset = 60
        heading_rect = heading.get_rect(midtop=(lx, ly + heading_y_offset))
        target.blit(heading, heading_rect)
        _, hy = heading_rect.midbottom
        menu_y_offset = 40
        left_x_offset = -100
        right_x_offset = 100
        for i, (option, state) in enumerate(options.items()):
            if i == menu_pos:
                menu_item = self.medium_menu_font.render(option, False, (0, 0, 205))
            else:
                menu_item = self.medium_menu_font.render(option, False, (255, 255, 255))
            menu_item_rect = menu_item.get_rect(midtop=(lx + left_x_offset,  hy + ((i + 1) * menu_y_offset)))
            target.blit(menu_item, menu_item_rect)
            if state:
                state_indicator = self.medium_menu_font.render(str(state), False, (34, 139, 34))
            else:
                state_indicator = self.medium_menu_font.render(str(state), False, (220, 53, 69))
            _, iy = menu_item_rect.midright
            ind_rect = state_indicator.get_rect(midleft=(lx + right_x_offset, iy ))
            target.blit(state_indicator, ind_rect)

    def render_highscores(self, target: pygame.Surface) -> None:
        target.blit(self.logo, self.logo_rect)
