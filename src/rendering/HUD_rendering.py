from pathlib import Path
from .rendering_utils import (
    fill, make_placeholder, load_image_or_fallback, copy_surface_info,
    build_colored_ghosts, recolor_sprite)
from .settings import TextObjs, RenderSettings, HUDState
import pygame
import math


class HUD:
    """Owns and draws the top/bottom HUD strip surfaces.

    The top strip is the placeholder colored banner with the PACMAN
    title logo blitted on top of it, at its native size. The bottom
    strip is still a plain placeholder fill - real score/lives/level
    content will replace it as the class grows.
    """

    def __init__(self, rend_sett: RenderSettings,
                 ghosts: dict[str, tuple[int, int, int]],
                 win_w: int, win_h: int) -> None:
        """Builds and pre-fills the top and bottom HUD surfaces.

        The surfaces are filled once here, not per frame, since their
        content doesn't change frame to frame - render_huds() just
        positions and blits the already-filled surfaces.

        Args:
            rend_sett: Shared rendering configuration - supplies each
                HUD surface's width/height.
            ghosts: Name-to-color map used to build the cached colored
                ghost surfaces once, at startup.
            win_w: Window width, in pixels.
            win_h: Window height, in pixels.
        """

        self.logo_h = rend_sett.ingame_logo_h
        self.logo_w = rend_sett.ingame_logo_w
        self.top_hud_h = rend_sett.top_hud_h
        self.top_hud_w = rend_sett.top_hud_w
        self.btm_hud_h = rend_sett.btm_hud_h
        self.btm_hud_w = rend_sett.btm_hud_w
        self.win_h = win_h
        self.win_w = win_w

        self.yellow = (255, 255, 0)
        self.white = (255, 255, 255)
        self.red = (220, 53, 69)

        self.full_blank = pygame.Surface((win_w, win_h), pygame.SRCALPHA, 32)
        fill(self.full_blank, (0, 0, 0))

        self.top_surf_blank = pygame.Surface(
            (self.top_hud_w, self.top_hud_h), pygame.SRCALPHA, 32)
        self.btm_surf_blank = pygame.Surface(
            (self.btm_hud_w, self.btm_hud_h), pygame.SRCALPHA, 32)

        self.logo_surf = pygame.Surface(
            (self.logo_w, self.logo_h), pygame.SRCALPHA, 32)

        self.top_surf = pygame.Surface(
            (self.top_hud_w, self.top_hud_h), pygame.SRCALPHA, 32)
        self.btm_surf = pygame.Surface(
            (self.btm_hud_w, self.btm_hud_h), pygame.SRCALPHA, 32)
        self.lv_clear_surf = pygame.Surface((500, 160), pygame.SRCALPHA, 32)

        fill(self.top_surf, (0, 0, 0), 0)
        fill(self.btm_surf, (0, 0, 0), 0)
        fill(self.lv_clear_surf, (0, 132, 61), 128)

        self.hud_font = pygame.font.Font(None, 24)

        self._load_sprites()

        self.deathsprite_list = [
            self.sprites_dict["pac_up_3"], self.sprites_dict["pac_death_1"],
            self.sprites_dict["pac_death_2"], self.sprites_dict["pac_death_3"],
            self.sprites_dict["pac_death_4"],
            self.sprites_dict["pac_death_blank"]
        ]

        self.pac_right_sprites = {
            0: self.sprites_dict["pac_right_3"],
            1: self.sprites_dict["pac_right_2"],
            2: self.sprites_dict["pac_closed"]
        }

        self.colored_ghosts: dict[str, pygame.surface.Surface] = \
            build_colored_ghosts(
                ghosts, self.sprites_dict["base_ghost"])

        self.frightened_dark: pygame.surface.Surface = \
            recolor_sprite(self.sprites_dict["base_ghost"], (0, 0, 140))

        logo_rect = self.sprites_dict["pacman_logo"].get_rect(
            center=(self.logo_w // 2, (self.logo_h // 2) - 40))

        self.logo_surf.blit(self.sprites_dict["pacman_logo"], logo_rect)

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
        logo_backup = make_placeholder((100, 100), self.yellow)
        ghost_placeholder = make_placeholder((20, 20), self.white)
        gummy_placeholder = make_placeholder((20, 20), self.yellow)
        pacman_placeholder = make_placeholder((20, 20), self.yellow)
        frame_placeholder = make_placeholder((1, 1), (0, 0, 0))

        self.sprites_dict: dict[str, pygame.surface.Surface] = {}

        specs = [
            ("pacman_logo", "pacman_logo.png", logo_backup),
            ("victory", "victory.png", logo_backup),
            ("game_over", "game_over.png", logo_backup),
            ("pacgum", "pacgum.png", gummy_placeholder),
            ("base_ghost", "ghost_base.png", ghost_placeholder),
            ("pac_right_3", "pacman_right_open.png", pacman_placeholder),
            ("pac_right_2", "pacman_right_half.png", pacman_placeholder),
            ("pac_closed", "pacman_closed.png", pacman_placeholder),
            ("pac_up_3", "pacman_up_open.png", pacman_placeholder),
            ("pac_death_1", "pacman_death_1.png", pacman_placeholder),
            ("pac_death_2", "pacman_death_2.png", pacman_placeholder),
            ("pac_death_3", "pacman_death_3.png", pacman_placeholder),
            ("pac_death_4", "pacman_death_4.png", pacman_placeholder),
            ("pac_death_blank", "pacman_death_blank.png", pacman_placeholder),
            ("mini_menu_frame", "mini_menu_frame.png", frame_placeholder),
            ("pacman_thumbs_up", "pacman_thumbs_up.png", pacman_placeholder),
            ("confetti", "confetti_ball.png", pacman_placeholder)
        ]

        for name, filename, placeholder in specs:
            self.sprites_dict[name] = load_image_or_fallback(
                self.__class__.__name__,
                ASSETS_DIR / filename, placeholder)

    def render_hud(self, target: pygame.Surface, hud_data: HUDState,
                   maze_midbtm: tuple[int, int],
                   maze_midtop: tuple[int, int]) -> None:
        """Positions and blits the top/bottom HUD surfaces onto `target`.

        Args:
            target: The target surface to draw onto - the top HUD is
                centered flush against its top edge, the bottom HUD
                flush against its bottom edge.
            hud_data: This frame's score/lives/level/time-remaining values.
            maze_midbtm: The maze's on-screen midbottom point, anchoring
                the top HUD strip.
            maze_midtop: The maze's on-screen midtop point, anchoring
                the bottom HUD strip.
        """

        copy_surface_info(self.top_surf_blank, self.top_surf)
        copy_surface_info(self.btm_surf_blank, self.btm_surf)

        mx_top, my_top = maze_midtop
        mx_btm, my_btm = maze_midbtm
        top_hud_mid = self.top_hud_w // 2
        btm_hud_mid = self.btm_hud_w // 2

        top_rect = self.top_surf.get_rect(midbottom=(mx_top, my_top))
        score_x_offset = -130
        time_x_offset_right = 130
        top_y_offset = 80

        rem_time = (hud_data.remaining_time
                    if hud_data.remaining_time > 0
                    else 0)

        curr_score_txt = TextObjs(
            self.hud_font, f"Current Score: {hud_data.curr_score}", "center",
            self.white, (top_hud_mid + score_x_offset, top_y_offset))
        time_rem_txt = TextObjs(
            self.hud_font, f" Time Remaining: {rem_time // 30}", "center",
            self.white, (top_hud_mid + time_x_offset_right, top_y_offset))

        self.top_surf.blit(curr_score_txt.surf, curr_score_txt.rect)
        self.top_surf.blit(time_rem_txt.surf, time_rem_txt.rect)
        target.blit(self.top_surf, top_rect)

        btm_rect = self.btm_surf.get_rect(midtop=(mx_btm, my_btm))

        lives_x_offset = -150
        lv_txt_offset_right = 180
        btm_y_offset = 25

        if hud_data.remaining_lives > 3:
            lives = 3
        else:
            lives = hud_data.remaining_lives

        for i in range(lives):
            self.btm_surf.blit(
                self.sprites_dict["pac_right_3"],
                self.sprites_dict["pac_right_3"].get_rect(center=(
                    btm_hud_mid + lives_x_offset + (i * 25), btm_y_offset)))

        curr_lv_txt = TextObjs(
            self.hud_font, f"Current Level: {hud_data.curr_lv}", "midright",
            self.white, (btm_hud_mid + lv_txt_offset_right, btm_y_offset))

        self.btm_surf.blit(curr_lv_txt.surf, curr_lv_txt.rect)

        target.blit(self.btm_surf, btm_rect)

    def render_maze_logo(self, target: pygame.Surface) -> None:
        """Draws the Pac-Man logo centered at the top of the window."""

        surf_w, _ = target.get_size()
        mid_x = surf_w // 2
        top_center = (mid_x, self.logo_h // 2 - 20)

        target.blit(self.sprites_dict["pacman_logo"],
                    self.sprites_dict["pacman_logo"].get_rect(
                        center=top_center))

    def _render_name_entry(self, target: pygame.Surface, mid_x: int,
                           prompt_y_offset_mid: int, typed: str,
                           warning: str) -> None:
        """Draws the name-entry prompt, typed name, and optional warning.

        Args:
            target: Surface to draw onto.
            mid_x: Horizontal center to anchor the prompt/warning around.
            prompt_y_offset_mid: Vertical center for the prompt row.
            typed: The name typed so far.
            warning: Validation message to show, if any.
        """

        prompt_x_offset_right = 80
        name_x_offset_left = 110

        prompt_txt = TextObjs(
            self.hud_font, "Enter your name (3-10 characters):",
            "midright", self.white,
            (mid_x + prompt_x_offset_right, prompt_y_offset_mid))
        typed_txt = TextObjs(
            self.hud_font, typed, "midleft", self.yellow,
            (mid_x + name_x_offset_left, prompt_y_offset_mid))

        target.blit(prompt_txt.surf, prompt_txt.rect)
        target.blit(typed_txt.surf, typed_txt.rect)

        if warning:
            warning_txt = TextObjs(
                self.hud_font, warning, "center", self.red,
                (mid_x, prompt_y_offset_mid + 50))

            target.blit(warning_txt.surf, warning_txt.rect)

    def _render_score_footer(self, target: pygame.Surface, mid_x: int,
                             score_y_offset: int, score: int) -> None:
        """Draws the final score and scoreboard reminder text.

        Args:
            target: Surface to draw onto.
            mid_x: Horizontal center to anchor both lines around.
            score_y_offset: Vertical position for the score line - the
                reminder line is drawn 30px below it.
            score: Final score to display.
        """

        score_txt = TextObjs(
            self.hud_font, f"Score achieved: {score}!", "center",
            self.white, (mid_x, score_y_offset))
        remind_txt = TextObjs(
            self.hud_font, "Don't forget to check the scoreboard!",
            "center", self.white, (mid_x, score_y_offset + 30))

        target.blit(score_txt.surf, score_txt.rect)
        target.blit(remind_txt.surf, remind_txt.rect)

    def render_victory(self, target: pygame.Surface, pac_x: int,
                       animating: bool, typed: str,
                       warning: str, score: int) -> None:

        copy_surface_info(self.full_blank, target)

        mid_x = self.win_w // 2
        icon_y_mid = self.win_h // 3

        prompt_y_offset_mid = self.win_h // 2 + 30

        target.blit(self.sprites_dict["victory"],
                    self.sprites_dict["victory"].get_rect(
                        center=(mid_x, icon_y_mid)))

        frightened_ghosts_x = [0, 75, 150, 225]

        if animating:
            cycle = 20
            eaten_x_offset = 9

            fraction = max(0.0, min(1.0, ((pac_x % cycle) / cycle)))

            last_openness = math.sin(math.pi * fraction)

            if last_openness < 0.33:
                mouth_state = 2
            elif last_openness < 0.66:
                mouth_state = 1
            else:
                mouth_state = 0

            pac_img = self.pac_right_sprites[mouth_state]

            pac_surf_mid = pac_img.get_rect(
                center=(mid_x + pac_x, prompt_y_offset_mid))

            target.blit(pac_img, pac_surf_mid)

            for i in range(4):
                ghost_surf_mid = (mid_x + frightened_ghosts_x[i],
                                  prompt_y_offset_mid)

                if frightened_ghosts_x[i] > pac_x + eaten_x_offset:
                    target.blit(
                        self.frightened_dark,
                        self.frightened_dark.get_rect(
                            center=(ghost_surf_mid)))

        else:
            for conf_pos in ((mid_x - 400, prompt_y_offset_mid),
                             (mid_x + 400, prompt_y_offset_mid)):
                rect = self.sprites_dict["confetti"].get_rect(center=(
                    conf_pos))
                target.blit(self.sprites_dict["confetti"], rect)

            self._render_name_entry(
                target, mid_x, prompt_y_offset_mid, typed, warning)

        score_y_offset = (self.win_h // 3) * 2 + 40
        self._render_score_footer(target, mid_x, score_y_offset, score)

    def render_gameover(self, target: pygame.Surface, death_step: int,
                        animating: bool, typed: str, warning: str,
                        score: int) -> None:
        """Draws the game-over screen: sprite, death animation,
        name entry, and final score.

        Args:
            target: Surface to draw onto.
            death_step: Which death-animation frame to show.
            animating: Whether the death animation is still playing.
            typed: The name typed so far.
            warning: Validation message to show, if any.
            score: Final score to display.
        """

        copy_surface_info(self.full_blank, target)

        mid_x = self.win_w // 2
        icon_y_mid = self.win_h // 3
        death_y_mid = self.win_h // 2

        prompt_y_offset_mid = death_y_mid + 10

        target.blit(self.sprites_dict["game_over"],
                    self.sprites_dict["game_over"].get_rect(
                        center=(mid_x, icon_y_mid)))

        death_img = self.deathsprite_list[death_step]
        target.blit(death_img, death_img.get_rect(center=(
            mid_x, death_y_mid)))

        if not animating:
            self._render_name_entry(
                target, mid_x, prompt_y_offset_mid, typed, warning)

        ghost_offsets = [-54, -18, 18, 54]
        ghost_y_offset = (self.win_h // 3) * 2

        for i, (_, surf) in enumerate(self.colored_ghosts.items()):
            ghost_rect = surf.get_rect(center=(
                mid_x + ghost_offsets[i], ghost_y_offset))

            target.blit(surf, ghost_rect)

        score_y_offset = ghost_y_offset + 50
        self._render_score_footer(target, mid_x, score_y_offset, score)

    def render_lv_complete_splash(self, target: pygame.Surface) -> None:
        """Draws the level-complete splash: banner frame, message, and icon."""

        target_w, target_h = target.get_size()
        target_mid = (target_w // 2, target_h // 2)
        splash_x_mid, splash_y_top = self.lv_clear_surf.get_rect().midtop

        lv_done_txt = TextObjs(
            self.hud_font, "Level Complete!!", "center", self.white,
            (splash_x_mid, splash_y_top + 40))
        next_loading_txt = TextObjs(
            self.hud_font, "Loading next level, please standby", "center",
            self.white, (splash_x_mid, splash_y_top + 120))
        thumbs_up_rect = self.sprites_dict["pacman_thumbs_up"].get_rect(
            center=(splash_x_mid, splash_y_top + 75))

        self.lv_clear_surf.blit(self.sprites_dict["mini_menu_frame"], (0, 0))
        self.lv_clear_surf.blit(lv_done_txt.surf, lv_done_txt.rect)
        self.lv_clear_surf.blit(next_loading_txt.surf, next_loading_txt.rect)
        self.lv_clear_surf.blit(
            self.sprites_dict["pacman_thumbs_up"], thumbs_up_rect)

        target.blit(self.lv_clear_surf, self.lv_clear_surf.get_rect(
            center=target_mid))
