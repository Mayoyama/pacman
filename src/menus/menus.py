import pygame
from enum import Enum
from src.player import Direction
from src.game_logic import MazeState, BonusState
from src.rendering import Visualizer, MenuState, fill


class MenuScreen(Enum):
    MAIN = "MAIN"
    OPTIONS = "OPTIONS"
    HIGH_SCORES = "HIGH SCORES"


class Menu:
    def __init__(self) -> None:
        self.start_game = False
        self.curr_menu = MenuScreen.MAIN
        self.selected_index = 0
        self.main_menu_items = ["START", "OPTIONS", "HIGH SCORES", "QUIT"]
        self.options_menu_items = {"Max Pacgums": False, "Bonus Time": False,
                                   "Invincible": False, "Ultra-pacgums": False}

    def detect_keypress(self, events: list[pygame.event.Event]) -> str | None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    return Direction.UP.value
                elif event.key == pygame.K_DOWN:
                    return Direction.DOWN.value
                elif event.key in (pygame.K_KP_ENTER, pygame.K_SPACE):
                    return "confirm"
                elif event.key == pygame.K_ESCAPE:
                    return "escape"

    def _current_item_count(self) -> int:
        if self.curr_menu == MenuScreen.MAIN:
            return len(self.main_menu_items)
        elif self.curr_menu == MenuScreen.OPTIONS:
            return len(self.options_menu_items)
        return 0

    def update_menu_pos(self, direction: str) -> None:
        item_count = self._current_item_count()
        if direction == Direction.UP.value:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = item_count - 1
        elif direction == Direction.DOWN.value:
            self.selected_index += 1
            if self.selected_index >= item_count:
                self.selected_index = 0

    def run_menu(self, vis: Visualizer, bonuses: BonusState) -> str | None:
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
                    elif selected_item == "HIGH SCORES":
                        self.curr_menu = MenuScreen.HIGH_SCORES
                    elif selected_item == "QUIT":
                        vis.running = False
                        return "QUIT"
                elif self.curr_menu == MenuScreen.OPTIONS:
                    fill(vis.screen, (0, 0, 0))
                    selected_item = list(self.options_menu_items.keys())[self.selected_index]
                    self.options_menu_items[selected_item] = not self.options_menu_items[selected_item]
                    if selected_item == "Max Pacgums":
                        bonuses.max_gums = self.options_menu_items[selected_item]
                    elif selected_item == "Bonus Time":
                        bonuses.bonus_time = self.options_menu_items[selected_item]
                    elif selected_item == "Invincible":
                        bonuses.invincible = self.options_menu_items[selected_item]
                    elif selected_item == "Ultra-pacgums":
                        bonuses.ultragums = self.options_menu_items[selected_item]
            elif action == "escape":
                fill(vis.screen, (0, 0, 0))
                if self.curr_menu == MenuScreen.MAIN:
                    vis.running = False
                    return "QUIT"
                elif self.curr_menu == MenuScreen.OPTIONS or self.curr_menu == MenuScreen.HIGH_SCORES:
                    self.curr_menu = MenuScreen.MAIN
                    self.selected_index = 0
            menu_data = MenuState(self.main_menu_items, self.options_menu_items, self.selected_index, self.curr_menu.value)
            vis.render_menus(menu_data)
            vis.handle_events(events)
        if not vis.running:
            return "QUIT"
