from dataclasses import dataclass


@dataclass(frozen=True)
class RenderSettings:
    """Frozen rendering configuration shared across the renderer.

    Attributes:
        target_fps: Frame rate the game loop is capped at.
        top_hud_height: Reserved pixel height for the top HUD strip.
        btm_hud_height: Reserved pixel height for the bottom HUD strip.
    """

    target_fps: int = 30
    top_hud_height: int = 40
    btm_hud_height: int = 40


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
