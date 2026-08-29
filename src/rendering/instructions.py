from .menu_rend_base import MenuRendBase
from .settings import TextObjs
import pygame


class InstructionsRenderer(MenuRendBase):
    """Draws the how-to-play instructions screen."""

    def __init__(self, win_w: int, win_h: int, gum_points: int,
                 supergum_points: int, ghost_points: int) -> None:
        """Builds the instructions text layout and scoring values.

        Args:
            win_w: Window width, in pixels.
            win_h: Window height, in pixels.
            gum_points: Score awarded per pacgum, shown in the
                SCORING section.
            supergum_points: Score awarded per super-pacgum, shown in
                the SCORING section.
            ghost_points: Score awarded per edible ghost, shown in
                the SCORING section.
        """

        super().__init__(win_w, win_h)

        self.gum_points = gum_points
        self.supergum_points = supergum_points
        self.ghost_points = ghost_points
        self.scoring_values = [
            self.gum_points,
            self.supergum_points,
            self.ghost_points
        ]

        self.subheading_font = pygame.font.Font(None, 30)
        self.instructions_font = pygame.font.Font(None, 24)

        self.sub_linesize = self.subheading_font.get_linesize()
        self.instructions_linesize = self.instructions_font.get_linesize()

        self.heading_y_offset = 100
        self.sub_body_gap = 8
        self.section_gap = 24
        self.line_gap = 4

        self.instructions: dict[str, list[str]] = {
            "OBJECTIVE:": [
                "Eat every pacgum in the maze before time runs out to clear "
                "the level."
            ],
            "CONTROLS:": [
                "Arrow Keys (UP, DOWN, LEFT, RIGHT)  -  Move.",
                "P  -  Pause the game and display the pause menu.",
                "Enter/Return  -  Confirm.",
                "Esc  -  Leave the current menu."
            ],
            "GAME PLAY:": [
                "Clear every pacgum and super pacgum in a level to move on to "
                "the next.",
                "Super pacgums turn the ghosts frightened - eat them for "
                "bonus points!",
                "Contact with a ghost that isn't frightened costs a life.",
                "Failing to complete a level in the time limit costs a life."
            ],
            "SCORING:": [
                "Pacgum: ",
                "Super Pacgum: ",
                "Frightened Ghost: "
            ]
        }

        self.subhead_y_offsets, self.line_y_offsets = self._build_layout()

    def _build_layout(self) -> tuple[dict[str, int], dict[str, list[int]]]:
        """Walks self.instructions once, computing every y-position from a
        running cursor instead of hand-chained offset formulas.

        Returns:
            subhead_ys: heading text -> its y position.
            line_ys: heading text -> list of y positions, one per line,
                in the same order as self.instructions[subheading].
        """

        subhead_ys: dict[str, int] = {}
        line_ys: dict[str, list[int]] = {}

        cursor_pos = self.logo_rect.bottom + self.heading_y_offset

        for subhead, lines in self.instructions.items():
            subhead_ys[subhead] = cursor_pos
            cursor_pos += self.sub_linesize + self.sub_body_gap

            line_ys[subhead] = []
            for _ in lines:
                line_ys[subhead].append(cursor_pos)
                cursor_pos += self.instructions_linesize + self.line_gap

            cursor_pos += self.section_gap

        return subhead_ys, line_ys

    def render_instructions(self, target: pygame.Surface) -> None:
        """Draws the logo, heading, every instruction section, and
        the live scoring values onto `target`.

        Args:
            target: Surface to draw onto.
        """

        target.blit(self.logo, self.logo_rect)

        heading_txt = TextObjs(
            self.large_menu_font, "HOW TO PLAY", "midtop", self.yellow,
            (self.logo_x_mid, self.logo_rect.bottom + 20))

        target.blit(heading_txt.surf, heading_txt.rect)

        left_x = self.logo_rect.left

        for subhead, lines in self.instructions.items():
            subhead_txt = TextObjs(
                self.subheading_font, subhead, "topleft", self.sky_blue,
                (left_x, self.subhead_y_offsets[subhead]))

            target.blit(subhead_txt.surf, subhead_txt.rect)

            for i, (line, y_offset) in enumerate(zip(
                    lines, self.line_y_offsets[subhead])):
                line_txt = TextObjs(
                    self.instructions_font, line, "topleft", self.white,
                    (left_x, y_offset))

                target.blit(line_txt.surf, line_txt.rect)

                if subhead == "SCORING:":
                    value_txt = TextObjs(
                        self.instructions_font, f"  {self.scoring_values[i]} ",
                        "topleft", self.green, (
                            self.win_w // 2 - 70, line_txt.rect.top))
                    pts_str = ("point" if self.scoring_values[i] == 1
                               else "points")
                    pts_txt = TextObjs(
                        self.instructions_font, pts_str, "midleft", self.white,
                        (self.win_w // 2, value_txt.rect.centery))

                    target.blit(value_txt.surf, value_txt.rect)
                    target.blit(pts_txt.surf, pts_txt.rect)

        target.blit(self.footer.surf, self.footer.rect)
