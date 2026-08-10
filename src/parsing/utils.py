import json
from typing import Any

from .models import Score


def load_content(filename: str) -> str:
    """
    Parse a file to get only the conent without argument line
    Args:
        filename (str): name of the file contianing the content to load
    Return:
        content (str): the content of the file with no argument line
    """
    content = ""
    with open(filename, "r") as f:
        for line in f.readlines():
            if not line.strip().startswith(("#", "//")):
                content += line
    return content


def write_scores(filename: str, player: Any, level: int):
    content = load_content(filename)
    score = Score(
        name=player._name,
        score=player._score,
        level=level
    )
    scores = json.loads(content)
    scores.append(score.model_dump())
    scores.sort(key=lambda score: score["score"], reverse=True)
    print(filename)
    print(scores)
    with open(filename, "w") as file:
        json.dump(scores[:10], file, indent=4)
