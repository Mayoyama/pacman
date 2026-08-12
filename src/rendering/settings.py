from dataclasses import dataclass
from typing import NamedTuple


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
        top_hud_height: Reserved pixel height for the top HUD strip.
        btm_hud_height: Reserved pixel height for the bottom HUD strip.
    """

    target_fps: int = 30
    top_hud_h: int = 200
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
    scared_timer: dict[str, int]
    tolerance: int


@dataclass
class UI_state:
    """Mutable UI colors and display toggles shared across the renderer.

    Attributes:
        wall_color: RGB color maze walls are drawn in.
        logo42_color: RGB color the '42' logo cells are filled with.
        animate_sprite: Whether sprite animation is currently enabled.
        show_sprite: Whether sprites should be drawn at all.
    """

    wall_color: tuple[int, int, int] = (150, 255, 0)
    logo42_color: tuple[int, int, int] = (0, 255, 150)  # (255, 255, 255)
    animate_sprite: bool = False
    show_sprite: bool = False
