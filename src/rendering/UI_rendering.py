from pathlib import Path
from .rendering_utils import fill, make_placeholder, load_image_or_fallback
from .settings import RenderSettings
import pygame




class HUD:
    """Owns and draws the top/bottom HUD strip surfaces.

    The top strip is the placeholder colored banner with the PACMAN
    title logo blitted on top of it, at its native size. The bottom
    strip is still a plain placeholder fill - real score/lives/level
    content will replace it as the class grows.
    """

    def __init__(self, rend_sett: RenderSettings) -> None:
        """Builds and pre-fills the top and bottom HUD surfaces.

        The surfaces are filled once here, not per frame, since their
        content doesn't change frame to frame - render_huds() just
        positions and blits the already-filled surfaces.

        Args:
            rend_sett: Shared rendering configuration - supplies each
                HUD surface's width/height.
        """
        self.top_hud_h = rend_sett.top_hud_h
        self.top_hud_w = rend_sett.top_hud_w
        self.btm_hud_h = rend_sett.btm_hud_h
        self.btm_hud_w = rend_sett.btm_hud_w

        self.top_surf = pygame.Surface((self.top_hud_w, self.top_hud_h),
                                       pygame.SRCALPHA, 32)
        self.btm_surf = pygame.Surface((self.btm_hud_w, self.btm_hud_h),
                                       pygame.SRCALPHA, 32)
        fill(self.top_surf, (125, 125, 0))
        fill(self.btm_surf, (0, 200, 200))

        ASSETS_DIR = Path(__file__).resolve().parent / "assets"

        logo_backup = make_placeholder((100, 100), (255, 255, 0))

        self.logo = load_image_or_fallback(self.__class__.__name__,
                                      ASSETS_DIR / "pacman_logo.png", logo_backup)
        logo_rect = self.logo.get_rect(
            center=(self.top_hud_w // 2, self.top_hud_h // 2))
        self.top_surf.blit(self.logo, logo_rect)

    def render_huds(self, surface: pygame.Surface) -> None:
        """Positions and blits the top/bottom HUD surfaces onto `surface`.

        Args:
            surface: The target surface to draw onto - the top HUD is
                centered flush against its top edge, the bottom HUD
                flush against its bottom edge.
        """
        surf_w, surf_h = surface.get_size()
        mid_x = surf_w // 2
        top_center = (mid_x, self.top_hud_h // 2)
        btm_mid_y = surf_h - (self.btm_hud_h // 2)
        btm_center = (mid_x, btm_mid_y)

        # Briefly centered off each surface's own actual size instead
        # (self.top_surf.get_height()/self.btm_surf.get_height()). That
        # only mattered while the logo itself was being rescaled to a
        # height different from top_hud_h - centering on top_hud_h would
        # then center it in empty reserved space rather than on the
        # image. Reverted: the logo is no longer rescaled (no MLX
        # equivalent for pygame.transform), so top_surf's actual size
        # always equals top_hud_w/h anyway - kept here for the record.
        # top_center = (mid_x, self.top_surf.get_height() // 2)
        # btm_center = (mid_x, surf_h - (self.btm_surf.get_height() // 2))

        top_rect = self.top_surf.get_rect(center=top_center)
        btm_rect = self.btm_surf.get_rect(center=btm_center)
        surface.blit(self.top_surf, top_rect)
        surface.blit(self.btm_surf, btm_rect)
