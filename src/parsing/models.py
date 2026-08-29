from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path


class LevelConfig(BaseModel):
    """One level's dimensions and identifier.

    Attributes:
        level_id: This level's position in the levels list, 1-indexed.
        width: Maze width, in cells.
        height: Maze height, in cells.
    """

    level_id: int = Field(ge=0, default=1)
    width: int = Field(ge=10, le=30, default=10)
    height: int = Field(ge=10, le=30, default=10)


class Configs(BaseModel):
    """Parsed, validated game configuration.

    Attributes:
        highscore_filename: Path to the highscore JSON file.
        pacgum: Number of pacgums to place, unless max_gums is set.
        points_per_pacgum: Score awarded per pacgum eaten.
        points_per_super_pacgum: Score awarded per super-pacgum eaten.
        points_per_ghost: Score awarded per edible ghost eaten.
        seed: Fixed seed for the first level's maze.
        level_max_time: Each level's time limit, in seconds.
        levels: This game's list of levels.
    """

    model_config = ConfigDict(extra='ignore')
    highscore_filename: Path | None = Field(default=Path("Unknown"))
    pacgum: int = Field(gt=0, le=100, default=42)
    points_per_pacgum: int = Field(gt=0, le=15, default=10)
    points_per_super_pacgum: int = Field(gt=15, le=50, default=50)
    points_per_ghost: int = Field(gt=50, le=200, default=200)
    seed: int = Field(default=42, gt=0)
    level_max_time: int = Field(default=90, gt=0, le=1000)
    levels: list[LevelConfig] = Field(
        min_length=1, default=[LevelConfig()])


class Score(BaseModel):
    """One saved highscore entry.

    Attributes:
        name: Player name, 3-10 alphanumeric/space characters.
        score: Final score, non-negative.
        level: The level reached.
    """

    name: str = Field(min_length=3, max_length=10)
    score: int = Field(ge=0)
    level: int = Field(ge=0)
