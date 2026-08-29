import pygame
from enum import Enum
from src.player import Direction
from src.game_logic import BonusState
from src.rendering import Visualizer, MenuState, fill
from .menu_utils import load_scores_or_fallback


class MenuScreen(Enum):
    """Which menu screen is currently active."""

    MAIN = "MAIN"
    OPTIONS = "OPTIONS"
    HIGH_SCORES = "HIGH SCORES"
    INSTRUCTIONS = "INSTRUCTIONS"
    PAUSED = "PAUSED"


class Menu:
    """Drives the main menu, options menu, high-scores screen, and pause
    menu.
    """

    def __init__(self) -> None:
        """Sets up the initial menu state and each screen's item list."""

        self.start_game = False
        self.curr_menu = MenuScreen.MAIN
        self.selected_index = 0
        self.main_menu_items = ["START", "OPTIONS", "HIGH SCORES",
                                "INSTRUCTIONS", "QUIT"]
        self.options_menu_items = {"Max Pacgums": False, "Bonus Time": False,
                                   "Invincible": False, "Ultra-pacgums": False,
                                   "Lethargic ghosts": False}
        self.pause_menu_items = ["Resume Game", "Quit to Menu"]

    def detect_keypress(self, events: list[pygame.event.Event]) -> str | None:
        """Reads one frame's events for a navigation/confirm/escape key.

        Args:
            events: The frame's events, from pygame.event.get().

        Returns:
            A Direction value for arrow keys, "confirm", "escape", or
            None if nothing relevant was pressed.
        """

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    return Direction.UP.value
                elif event.key == pygame.K_DOWN:
                    return Direction.DOWN.value
                elif event.key == pygame.K_LEFT:
                    return Direction.LEFT.value
                elif event.key == pygame.K_RIGHT:
                    return Direction.RIGHT.value
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                                   pygame.K_SPACE):
                    return "confirm"
                elif event.key == pygame.K_ESCAPE:
                    return "escape"
        return None

    def _current_item_count(self) -> int:
        """Returns how many items the currently active menu has."""

        if self.curr_menu == MenuScreen.MAIN:
            return len(self.main_menu_items)
        elif self.curr_menu == MenuScreen.OPTIONS:
            return len(self.options_menu_items)
        elif self.curr_menu == MenuScreen.PAUSED:
            return len(self.pause_menu_items)
        return 0

    def update_menu_pos(self, direction: str) -> None:
        """Moves the vertical menu selection up/down, wrapping at the ends.

        Args:
            direction: Direction.UP or Direction.DOWN.
        """

        item_count = self._current_item_count()
        if direction == Direction.UP.value:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = item_count - 1
        elif direction == Direction.DOWN.value:
            self.selected_index += 1
            if self.selected_index >= item_count:
                self.selected_index = 0

    def update_vert_menu_pos(self, direction: str) -> None:
        """Moves the pause menu's left/right selection, wrapping at the ends.

        Args:
            direction: Direction.LEFT or Direction.RIGHT.
        """

        item_count = self._current_item_count()
        if direction == Direction.LEFT.value:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = item_count - 1
        elif direction == Direction.RIGHT.value:
            self.selected_index += 1
            if self.selected_index >= item_count:
                self.selected_index = 0

    def run_menu(self, vis: Visualizer, bonuses: BonusState,
                 highscore_path: str) -> str | None:
        """Runs the main/options/high-scores menu loop until start or quit.

        Args:
            vis: The Visualizer, for input, rendering, and the running flag.
            bonuses: Bonus toggles, updated directly from the options menu.
            highscore_path: Path to the highscore file, for that screen.

        Returns:
            "QUIT" if the player quit, otherwise None once start_game is set.
        """

        highscores = load_scores_or_fallback(highscore_path)
        while not self.start_game and vis.running:
            vis.set_tick()
            events = pygame.event.get()
            action = self.detect_keypress(events)
            if action in (Direction.UP.value, Direction.DOWN.value):
                if self.curr_menu == MenuScreen.MAIN:
                    fill(vis.screen, (0, 0, 0))
                self.update_menu_pos(action)

            elif action == "confirm":
                if self.curr_menu == MenuScreen.MAIN:
                    fill(vis.screen, (0, 0, 0))
                    selected_item = self.main_menu_items[self.selected_index]
                    if selected_item == "START":
                        self.start_game = True
                    elif selected_item == "OPTIONS":
                        self.curr_menu = MenuScreen.OPTIONS
                        self.selected_index = 0
                    elif selected_item == "HIGH SCORES":
                        self.curr_menu = MenuScreen.HIGH_SCORES
                        self.selected_index = 0
                    elif selected_item == "INSTRUCTIONS":
                        self.curr_menu = MenuScreen.INSTRUCTIONS
                        self.selected_index = 0
                    elif selected_item == "QUIT":
                        vis.running = False
                        return "QUIT"

                elif self.curr_menu == MenuScreen.OPTIONS:
                    fill(vis.screen, (0, 0, 0))
                    selected_item = list(self.options_menu_items.keys()
                                         )[self.selected_index]
                    self.options_menu_items[selected_item] = \
                        not self.options_menu_items[selected_item]
                    if selected_item == "Max Pacgums":
                        bonuses.max_gums = \
                            self.options_menu_items[selected_item]
                    elif selected_item == "Bonus Time":
                        bonuses.bonus_time = \
                            self.options_menu_items[selected_item]
                    elif selected_item == "Invincible":
                        bonuses.invincible = \
                            self.options_menu_items[selected_item]
                    elif selected_item == "Ultra-pacgums":
                        bonuses.ultragums = \
                            self.options_menu_items[selected_item]
                    elif selected_item == "Lethargic ghosts":
                        bonuses.slowpoke_ghost = \
                            self.options_menu_items[selected_item]

            elif action == "escape":
                fill(vis.screen, (0, 0, 0))
                if self.curr_menu == MenuScreen.MAIN:
                    vis.running = False
                    return "QUIT"
                elif (self.curr_menu == MenuScreen.OPTIONS
                      or self.curr_menu == MenuScreen.HIGH_SCORES
                        or self.curr_menu == MenuScreen.INSTRUCTIONS):
                    self.curr_menu = MenuScreen.MAIN
                    self.selected_index = 0

            menu_data = MenuState(self.main_menu_items,
                                  self.options_menu_items,
                                  self.selected_index,
                                  self.curr_menu.value)
            vis.render_menus(menu_data, highscores)
            vis.handle_events(events)
        if not vis.running:
            return "QUIT"
        return None

    def handle_pause_menu(self, vis: Visualizer) -> str | None:
        """Runs the pause menu loop until resume or quit-to-menu.

        Args:
            vis: The Visualizer, for input, rendering, and the running flag.

        Returns:
            "MAIN_MENU" or "QUIT", or None once the player resumes.
        """

        self.curr_menu = MenuScreen.PAUSED
        self.selected_index = 0
        paused = True
        while paused and vis.running:
            vis.set_tick()
            events = pygame.event.get()
            action = self.detect_keypress(events)

            if action in (Direction.LEFT.value, Direction.RIGHT.value):
                self.update_vert_menu_pos(action)

            elif action == "confirm":
                selected_item = self.pause_menu_items[self.selected_index]

                if selected_item == "Resume Game":
                    paused = False

                elif selected_item == "Quit to Menu":
                    paused = False
                    self.curr_menu = MenuScreen.MAIN
                    self.selected_index = 0
                    return "MAIN_MENU"

            elif action == "escape":
                paused = False

            vis.menu_rend.render_pause_menu(
                vis.screen,
                self.pause_menu_items,
                self.selected_index)
            pygame.display.flip()
            vis.handle_events(events)
        if not vis.running:
            return "QUIT"
        return None
