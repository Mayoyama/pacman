from dataclasses import dataclass


@dataclass
class BonusState:
    """Player-selected challenge/cheat toggles, chosen from the options menu.

    Attributes:
        max_gums: Fill every eligible cell with a pacgum instead of a
            set amount from the config file (challenge mode).
        bonus_time: Doubles each level's time limit (cheat mode).
        invincible: Disables all ghost collisions (cheat mode).
        ultragums: Doubles the frightened-ghost duration (cheat mode).
        slowpoke_ghost: Halves ghost movement speed (cheat mode).
    """

    max_gums: bool = False
    bonus_time: bool = False
    invincible: bool = False
    ultragums: bool = False
    slowpoke_ghost: bool = False
