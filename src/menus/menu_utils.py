from json import JSONDecodeError, loads
from sys import stderr


def load_scores_or_fallback(path: str) -> list[tuple[str, int, int]]:
    """Loads and sorts the highscore file, falling back to dummy data on error.

    Args:
        path: Path to the highscore JSON file.

    Returns:
        (name, score, level) tuples sorted by score, descending.
    """

    try:
        content = ""
        with open(path, "r") as f:
            for line in f.readlines():
                if not line.strip().startswith(("#", "//")):
                    content += line
        scores = loads(content)
        scoreboard = []
        for entry in scores:
            name = entry["name"]
            score = entry["score"]
            level = entry["level"]
            scoreboard.append((name, score, level))
        return sorted(scoreboard, key=lambda item: item[1], reverse=True)
    except (JSONDecodeError, OSError, KeyError, TypeError,
            UnicodeDecodeError):
        print(f"load_scores_or_fallback: unable to load {path}. "
              "Defaulting to dummy data", file=stderr)
        dummy_score = [("PAC", 999, 9), ("MARS", 666, 6), ("SPP", 333, 3)]
        return dummy_score
