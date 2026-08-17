import sys
import json
from pathlib import Path
from random import randint
from pydantic import ValidationError 

from .models import Configs, Score, LevelConfig
from .utils import load_content


def configs_parser(filename: str) -> Configs:
    content = load_content(filename)
    try:
        configs = {}
        if content:
            configs = json.loads(content)
    except Exception as e:
        print(e)
        raise SyntaxError(f"invalid syntax for '{filename}'")
    while 1:
        try:
            return Configs(**configs)
        except ValidationError as e:
            for error in e.errors():
                print(f"WARNING: invalid value for '{error['loc'][-1]}'",
                      file=sys.stderr)
                if error["loc"][0] != "levels":
                    configs.pop(error["loc"][0])
                else:
                    loc = error["loc"]
                    configs[loc[0]][loc[1]].pop(loc[2])


def scores_parser(filename: str) -> None:
    """
    Check if the file content respect the model
    Args:
        filename (str): name of the file contianing the scores
    """
    content = load_content(filename)
    try:
        if len(content) > 0:
            for score in json.loads(content):
                Score(**score)
    except Exception:
        raise ValueError(f"{filename} doesn't respect the waiting syntax")


def parsing() -> Configs:
    try:
        import mazegenerator  # noqa: F401 # type: ignore[import-not-found]
    except ImportError:
        raise ImportError("No import of mazegenerator known")
    if len(sys.argv) != 2:
        raise ValueError("Wrong way to run the program")
    file = Path(sys.argv[1])
    if not file.is_file() or file.suffix != ".json":
        file = Path("configs.json")
        file.touch()
        print("Configuration file is not a json file", file=sys.stderr)
    configs = configs_parser(str(file))
    ids: list[int] = []
    for level in configs.levels:
        level.level_id = len(ids) + 1
        ids.append(level.level_id)
    if len(configs.levels) < 10:
        for _ in range(10 - len(ids)):
            lvl_id = len(ids) + 1
            ids.append(lvl_id)
            configs.levels.append(LevelConfig(
                level_id=lvl_id,
                width=randint(10, 31),
                height=randint(10, 31)
            ))
    for level in configs.levels:
        if level.width % 2 == 0:
            level.width -= 1
        if level.height % 2 == 0:
            level.height -= 1
    if (configs.highscore_filename is None
        or not configs.highscore_filename.is_file()
        or configs.highscore_filename.suffix != ".json"):
        print(f"WARNING: {configs.highscore_filename} is not an existing "
              "json file", file=sys.stderr)
        configs.highscore_filename = Path("best_scores.json")
        configs.highscore_filename.touch()
    scores_parser(str(configs.highscore_filename))
    return configs
