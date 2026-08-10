from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path


class LevelConfig(BaseModel):
    level_id: int = Field(ge=0, default=1)
    width: int = Field(ge=10, le=100, default=10)
    height: int = Field(ge=10, le=100, default=10)


class Configs(BaseModel):
    model_config = ConfigDict(extra='ignore')
    highscore_filename: Path | None = Field(default=Path("Unknown"))
    pacgum: int = Field(gt=0, le=100, default=42)
    points_per_pacgum: int = Field(gt=0, le=15, default=10)
    points_per_super_pacgum: int = Field(gt=15, le=50, default=50)
    points_per_ghost: int = Field(gt=50, le=200, default=200)
    seed: int | str | None = None
    level_max_time: int = Field(default=90, gt=0, le=1000)
    levels: list[LevelConfig] = Field(
        min_length=1,
        default=[LevelConfig()]
    )


class Score(BaseModel):
    name: str = Field(min_length=3, max_length=10)
    score: int = Field(ge=0)
    level: int = Field(ge=0)
