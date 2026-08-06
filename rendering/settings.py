from dataclasses import dataclass


@dataclass(frozen=True)
class RenderSettings:
    """
    Stores and freezes rendering configuration values such as window
    dimensions and target fps.
    """
    target_fps: int = 30
    top_hud_height: int = 40
    btm_hud_height: int = 40


@dataclass
class UI_state:
    """
    Stores mutable UI settings including colors and display toggles
    used by the renderer.
    """
    wall_color: tuple[int, int, int] = (150, 255, 0)
    logo42_color: tuple[int, int, int] = (0, 0, 0)  # (255, 255, 255)
    animate_sprite: bool = False
    show_sprite: bool = False
