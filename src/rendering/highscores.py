from .menu_rend_base import MenuRendBase
from .settings import TextObjs
import pygame


class ScoreBoardRender(MenuRendBase):
    """Draws the high-scores table."""

    def __init__(self, win_w: int, win_h: int) -> None:
        super().__init__(win_w, win_h)

        self.gold = (255, 215, 0)
        self.silver = (192, 192, 192)
        self.bronze = (205, 127, 50)
        self.pine_green = (0, 75, 30)

    def render_highscores(self, target: pygame.surface.Surface,
                          highscores: list[tuple[str, int, int]]) -> None:
        """Draws a ranked table of up to the top 10 highscores.

        Args:
            target: Surface to draw onto.
            highscores: (name, score, level) tuples, already sorted.
        """

        target.blit(self.logo, self.logo_rect)

        lx, ly = self.logo_rect.midbottom
        heading_y_offset = 40

        heading = TextObjs(
            self.large_menu_font, "HIGH SCORES", "midtop", self.sky_blue,
            (lx, ly + heading_y_offset))

        _, hy = heading.rect.midbottom
        place_x_offset = -200
        name_x_offset = -75
        score_x_offset = 90
        lv_x_offset = 210

        name_head = TextObjs(
            self.medium_menu_font, "Name", "center", self.head_white,
            (lx + name_x_offset, hy + heading_y_offset))
        score_head = TextObjs(
            self.medium_menu_font, "Score", "center", self.head_white,
            (lx + score_x_offset, hy + heading_y_offset))
        lv_head = TextObjs(
            self.medium_menu_font, "Level", "center", self.head_white,
            (lx + lv_x_offset, hy + heading_y_offset))

        target.blit(heading.surf, heading.rect)
        target.blit(name_head.surf, name_head.rect)
        target.blit(score_head.surf, score_head.rect)
        target.blit(lv_head.surf, lv_head.rect)

        menu_y_offset = 40

        for i, (name, score, level) in enumerate(highscores[:10]):
            if i == 0:
                color = self.gold
            elif i == 1:
                color = self.silver
            elif i == 2:
                color = self.bronze
            elif i >= 3 and i <= 5:
                color = self.sel_blue
            else:
                color = self.pine_green

            row_y = hy + heading_y_offset + ((i + 1) * menu_y_offset)

            pos_txt = TextObjs(
                self.medium_menu_font, f"#{i + 1}", "center", color,
                (lx + place_x_offset, row_y))
            name_txt = TextObjs(
                self.medium_menu_font, f"{name}", "center", color,
                (lx + name_x_offset, row_y))
            score_txt = TextObjs(
                self.medium_menu_font, f"{score}", "center", color,
                (lx + score_x_offset, row_y))
            lv_txt = TextObjs(
                self.medium_menu_font, f"{level}", "center", color,
                (lx + lv_x_offset, row_y))

            target.blit(pos_txt.surf, pos_txt.rect)
            target.blit(name_txt.surf, name_txt.rect)
            target.blit(score_txt.surf, score_txt.rect)
            target.blit(lv_txt.surf, lv_txt.rect)

        target.blit(self.footer.surf, self.footer.rect)
