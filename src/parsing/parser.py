import sys
import json
from pathlib import Path
from random import randint
from pydantic import ValidationError

from .models import Configs, Score, LevelConfig
from .utils import load_content


def configs_parser(filename: str) -> Configs:
    """Loads and validates the config file, clamping invalid fields to
    defaults.

    Args:
        filename: Path to the config JSON file.

    Returns:
        A fully valid Configs.

    Raises:
        SyntaxError: If the file's content isn't valid JSON.
    """

    content = load_content(filename)
    try:
        configs = {}
        if content:
            configs = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"configs_parser: {e}", file=sys.stderr)
        raise SyntaxError(f"invalid syntax for '{filename}'") from e
    while True:
        try:
            return Configs(**configs)
        except ValidationError as e:
            for error in e.errors():
                print(f"WARNING: invalid value for '{error['loc'][-1]}'",
                      file=sys.stderr)
                loc = error["loc"]
                if loc[0] != "levels":
                    configs.pop(loc[0], None)
                elif len(loc) >= 3:
                    configs[loc[0]][loc[1]].pop(loc[2], None)
                else:
                    configs.pop("levels", None)


def scores_parser(filename: str) -> None:
    """Checks if the file content respects the model.

    Args:
        filename: Name of the file containing the scores.

    Raises:
        ValueError: If the file's content doesn't match the expected
            score format.
    """

    content = load_content(filename)
    try:
        if len(content) > 0:
            for score in json.loads(content):
                Score(**score)
    except (json.JSONDecodeError, ValidationError, TypeError) as e:
        raise ValueError(
            f"{filename} doesn't respect the expected syntax") from e


def parsing() -> Configs:
    """Parses the command-line config argument into a ready-to-play Configs.

    Falls back to a blank configs.json if the given path isn't a JSON
    file, pads the level list up to 10 entries, ensures a valid
    highscore filename, and validates any existing highscore data.

    Returns:
        The fully prepared Configs for this run.

    Raises:
        ValueError: If the program wasn't launched with exactly one
            argument.
    """

    if len(sys.argv) != 2:
        raise ValueError("Invalid launch. Usage: uv run python3 pac-man.py "
                         "config.json")
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
                width=randint(10, 29),
                height=randint(10, 29)
            ))

    if (configs.highscore_filename is None
            or not configs.highscore_filename.is_file()
            or configs.highscore_filename.suffix != ".json"):
        print(f"WARNING: {configs.highscore_filename} is not an existing "
              "json file", file=sys.stderr)
        configs.highscore_filename = Path("best_scores.json")
        configs.highscore_filename.touch()
    scores_parser(str(configs.highscore_filename))
    return configs
