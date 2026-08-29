from dataclasses import dataclass
from typing import NamedTuple
from pygame import font
from sys import stderr


class TextObjs:
    """Bundles a rendered text surface with its positioned rect."""

    _SINGLE_ANCHORS = {"left", "right", "top", "bottom", "centerx", "centery"}
    _TUPLE_ANCHORS = {"topleft", "topright", "bottomleft", "bottomright",
                      "midtop", "midbottom", "midleft", "midright", "center"}

    def __init__(self, font: font.Font, text: str, anchor: str,
                 color: tuple[int, int, int], pos: tuple[int, int],
                 antialias: bool = False) -> None:
        """Renders the text and computes its anchored rect.

        Args:
            font: Font to render with.
            text: The string to render.
            anchor: Which get_rect() keyword to position by (e.g. "center",
                "midleft").
            color: RGB text color.
            pos: Position to anchor at.
            antialias: Whether to antialias the rendered text.
        """

        invalid_single_anchor = (
            anchor in self._SINGLE_ANCHORS
            and (not isinstance(pos, int) or isinstance(pos, bool)))

        invalid_tuple_anchor = (
            anchor in self._TUPLE_ANCHORS
            and not (isinstance(pos, tuple) and len(pos) == 2
                     and all(isinstance(v, int) and not isinstance(v, bool)
                             for v in pos)))

        if (anchor not in self._SINGLE_ANCHORS
                and anchor not in self._TUPLE_ANCHORS):
            print(f"TextObjs: '{anchor}' not a valid anchor. "
                  "Defaulting to center=(0, 0).", file=stderr)
            anchor, pos = "center", (0, 0)

        elif invalid_single_anchor or invalid_tuple_anchor:
            print(f"TextObjs: '{anchor}' '{pos}' not a valid combination. "
                  "Defaulting to center=(0, 0).", file=stderr)
            anchor, pos = "center", (0, 0)

        self.text = text
        self.anchor = anchor
        self.pos = pos
        self.surf = font.render(text, antialias, color)
        self.rect = self.surf.get_rect(**{anchor: pos})


class PixelMath(NamedTuple):
    """Rendering constants shared everywhere.

    Attributes:
        cell_size: Width/height of one maze cell, in pixels.
        padding: Margin around the maze, in pixels.
    """

    cell_size: int = 24
    padding: int = 10


class RenderSettings(NamedTuple):
    """Frozen rendering configuration shared across the renderer.

    Attributes:
        target_fps: Frame rate the game loop is capped at.
        ingame_logo_h: Height of the in-game Pac-Man logo, in pixels.
        ingame_logo_w: Width of the in-game Pac-Man logo, in pixels.
        top_hud_h: Reserved pixel height for the top HUD strip.
        top_hud_w: Reserved pixel width for the top HUD strip.
        btm_hud_h: Reserved pixel height for the bottom HUD strip.
        btm_hud_w: Reserved pixel width for the bottom HUD strip.
    """

    target_fps: int = 30
    ingame_logo_h: int = 200
    ingame_logo_w: int = 800
    top_hud_h: int = 100
    top_hud_w: int = 800
    btm_hud_h: int = 100
    btm_hud_w: int = 800


class SpriteRenderState(NamedTuple):
    """Per-frame animation state needed to draw pacman, ghosts, and pacgums.

    Rebuilt fresh every frame from that frame's current values - never
    mutated in place, so a new instance simply replaces the old one.

    Attributes:
        last_direction: Pacman's current facing direction, one of
            "up"/"down"/"left"/"right" (a `Direction.value`).
        ghost_pos: Each ghost's current (row, col) grid position,
            keyed by name.
        superpacgums: (row, col) of every remaining super pacgum.
        pacgums: (row, col) of every remaining pacgum.
        pacpixel_pos: Pacman's continuous pixel position.
        mouth_state: Pacman's current mouth animation frame, one of
            "closed"/"half"/"open".
    """

    player_direction: str
    player_pos: tuple[int, int]
    ghost_pos: dict[str, tuple[int, int]]
    superpacgums: set[tuple[int, int]]
    pacgums: set[tuple[int, int]]
    pacpixel_pos: tuple[int, int]
    scared_timers: dict[str, int]
    respawn_timers: dict[str, int]
    tolerance: int


@dataclass
class UI_state:
    """Mutable UI colors and display toggles shared across the renderer.

    Attributes:
        wall_color: RGB color maze walls are drawn in.
        logo42_color: RGB color the '42' logo cells are filled with.
    """

    wall_color: tuple[int, int, int] = (150, 255, 0)
    logo42_color: tuple[int, int, int] = (0, 255, 150)


class MenuState(NamedTuple):
    """Per-frame data needed to render whichever menu screen is active.

    Attributes:
        main_menu_items: Main menu item labels.
        options_menu_items: Bonus toggle name to current state.
        menu_pos: Index of the currently selected item.
        curr_menu: Name of the currently active menu screen.
    """

    main_menu_items: list[str]
    options_menu_items: dict[str, bool]
    menu_pos: int
    curr_menu: str


class HUDState(NamedTuple):
    """Per-frame data needed to draw the in-game HUD.

    Attributes:
        curr_score: Current score.
        remaining_lives: Lives left.
        curr_lv: Current level number.
        remaining_time: Time left in the level, in frames.
    """

    curr_score: int
    remaining_lives: int
    curr_lv: int
    remaining_time: int
