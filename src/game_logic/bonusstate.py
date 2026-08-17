from dataclasses import dataclass

@dataclass
class BonusState:
    max_gums: bool = False
    bonus_time: bool = False
    invincible: bool = False
    ultragums: bool = False
