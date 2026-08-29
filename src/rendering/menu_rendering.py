from .menu_rend_base import MenuRendBase
from .settings import TextObjs
from .rendering_utils import recolor_sprite
import pygame


class MenuRender(MenuRendBase):
    """Draws the main menu, options menu, and pause menu."""

    def __init__(self, win_w: int, win_h: int) -> None:
        super().__init__(win_w, win_h)

        self.orange = (255, 140, 0)

    def render_main_menu(self, target: pygame.Surface,
                         options: list[str], menu_pos: int) -> None:
        """Draws the main menu's items, highlighting the selected one.

        Args:
            target: Surface to draw onto.
            options: Menu item labels, in order.
            menu_pos: Index of the currently selected item.
        """

        target.blit(self.logo, self.logo_rect)

        lx, ly = self.logo_rect.midbottom
        heading_y_offset = 60
        heading = TextObjs(
            self.large_menu_font, "MAIN MENU", "midtop", self.head_white,
            (lx, ly + heading_y_offset))

        target.blit(heading.surf, heading.rect)

        _, hy = heading.rect.midbottom
        menu_y_offset = 40
        pac_offset = -25

        for i, option in enumerate(options):
            color = self.sel_blue if i == menu_pos else self.white
            menu_item = TextObjs(
                self.medium_menu_font, option, "midtop", color,
                (lx, hy + ((i + 1) * menu_y_offset)))

            if i == menu_pos:
                mx, my = menu_item.rect.midleft
                pac_rect = self.pac_icon.get_rect(center=(mx + pac_offset, my))

                target.blit(self.pac_icon, pac_rect)

            target.blit(menu_item.surf, menu_item.rect)

    def render_options_menu(self, target: pygame.Surface,
                            options: dict[str, bool], menu_pos: int) -> None:
        """Draws each bonus toggle and its current on/off state.

        Args:
            target: Surface to draw onto.
            options: Toggle name to current state.
            menu_pos: Index of the currently selected toggle.
        """

        target.blit(self.logo, self.logo_rect)

        lx, ly = self.logo_rect.midbottom
        heading_y_offset = 60
        heading = TextObjs(
            self.large_menu_font, "OPTIONS MENU", "midtop", self.purple,
            (lx, ly + heading_y_offset))

        target.blit(heading.surf, heading.rect)

        _, hy = heading.rect.midbottom
        extra_y_offset = hy + 30
        menu_y_offset = 40
        left_x_offset = -100
        right_x_offset = 100

        for i, (option, state) in enumerate(options.items()):
            color = self.sel_blue if i == menu_pos else self.white
            menu_item = TextObjs(
                self.medium_menu_font, option, "midtop", color,
                (lx + left_x_offset,
                 extra_y_offset + ((i + 1) * menu_y_offset)))

            target.blit(menu_item.surf, menu_item.rect)

            state_color = self.green if state else self.red
            _, iy = menu_item.rect.midright
            state_indicator = TextObjs(
                self.medium_menu_font, str(state), "midleft", state_color,
                (lx + right_x_offset, iy))

            target.blit(state_indicator.surf, state_indicator.rect)

        target.blit(self.footer.surf, self.footer.rect)

    def render_pause_menu(self, target: pygame.Surface,
                          options: list[str], menu_pos: int) -> None:
        """Draws the pause menu's two options over a semi-transparent overlay.

        Args:
            target: Surface to draw onto.
            options: Menu item labels, in order.
            menu_pos: Index of the currently selected item.
        """

        target_w, target_h = target.get_size()
        target_mid = (target_w // 2, target_h // 2)

        pause_w, pause_h = self.pause_surf.get_size()
        pause_x_mid = pause_w // 2

        self.pause_surf.blit(self.mini_frame, (0, 0))

        pause_head = TextObjs(
            self.medium_menu_font, "PAUSE MENU", "center", self.vib_blue,
            (pause_x_mid, pause_h // 3))

        self.pause_surf.blit(pause_head.surf, pause_head.rect)

        rainbow_y_offset = 15
        rainbow_x_ofset = 30
        rb_x_start = pause_x_mid + 30

        for i, color in enumerate((self.red, self.orange, self.yellow,
                                   self.green, self.vib_blue, self.purple)):
            rainbow_ghost = recolor_sprite(self.pac_icon, color, self.yellow)
            self.pause_surf.blit(rainbow_ghost, rainbow_ghost.get_rect(center=(
                rb_x_start + ((i + 1) * rainbow_x_ofset), rainbow_y_offset)))

        left_x_offset = -40
        right_x_offset = 40

        for i, option in enumerate(options):
            color = self.yellow if i == menu_pos else self.white
            anchor = "midright" if i == 0 else "midleft"
            x_offset = left_x_offset if i == 0 else right_x_offset

            menu_item = TextObjs(
                self.medium_menu_font, option, anchor, color,
                (pause_x_mid + x_offset, (pause_h // 3) * 2))

            self.pause_surf.blit(menu_item.surf, menu_item.rect)

        target.blit(self.pause_surf,
                    self.pause_surf.get_rect(center=target_mid))
