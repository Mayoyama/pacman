import json
from typing import Any
from sys import stderr
from .models import Score
from pydantic import ValidationError


def load_content(filename: str) -> str:
    """Parse a file to get only the conent without argument line.

    Args:
        filename (str): name of the file contianing the content to load
    Return:
        content (str): the content of the file with no argument line
    """

    try:
        content = ""
        with open(filename, "r") as f:
            for line in f.readlines():
                if not line.strip().startswith(("#", "//")):
                    content += line
        return content
    except (OSError, UnicodeDecodeError) as e:
        print(f"load_content: {e}", file=stderr)
        raise


def write_scores(filename: str, player: Any, level: int) -> None:
    """Appends this run's score to the highscore file, keeping the top 10.

    Args:
        filename: Path to the highscore JSON file.
        player: The Player whose name/score to save.
        level: The level reached this run.
    """

    try:
        content = load_content(filename)
        score = Score(
            name=player.name,
            score=player.score,
            level=level
        )
        if not content.strip():
            scores = []
        else:
            scores = json.loads(content)
        scores.append(score.model_dump())
        scores.sort(key=lambda score: score["score"], reverse=True)
        with open(filename, "w") as file:
            json.dump(scores[:10], file, indent=4)
    except ValidationError as e:
        error_messages = []
        for err in e.errors(include_url=False):
            loc = " -> ".join(str(p) for p in err["loc"])
            error_messages.append(f"{loc}: {err['msg']} [type={err['type']}]")

        clean_error = "; ".join(error_messages)
        print(f"write_scores: Error writing scores: {clean_error}. "
              "Scores not recorded.", file=stderr)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError,
            AttributeError, KeyError, TypeError) as e:
        print(f"write_scores: Error writing scores: {e}. Scores not recorded.",
              file=stderr)
