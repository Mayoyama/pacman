*This project has been created as part of the 42 curriculum by mde-cat, speterse.*

# Pacman

## Description

Pacman is a Python game inspired by the classic Pac-Man arcade game.

The goal is to complete a series of mazes by eating all pacgums while
avoiding ghosts. The player starts with three lives and must navigate
through corridors, collect pacgums and super-pacgums, and deal with
ghosts that behave similarly to those in the original Pac-Man.

The game contains multiple configurable levels, a scoring system, a
persistent top-10 highscore system, a pause system, and a cheat mode
designed to facilitate peer review and testing.

The project is written in Python 3.10+ and uses Pygame for visualization
and Pydantic for configuration and data validation.

## Features

- Multiple levels, with at least 10 provided and no fixed upper limit.
- Per-level wall and '42' logo colors, cycled from a fixed palette.
- Per-level difficulty scaling: ghost speed increases and
  frightened-ghost duration shortens as the player advances through
  the levels.
- Instructions screen showing controls, gameplay rules, and live
  scoring values pulled from the configuration.
- A level-complete splash screen shown between levels.
- A first maze generated using a fixed seed.
- Randomly generated mazes for subsequent levels.
- Four ghosts with Pac-Man-inspired behavior.
- Pacgums and super-pacgums.
- Player lives and respawning, with lives and score carried over
  between levels.
- Score system.
- Persistent top-10 highscores.
- Configurable game parameters.
- Configuration validation and safe fallback values.
- Pause system.
- Cheat mode for peer review.
- Clean shutdown on Ctrl+C/Ctrl+Z, instead of a raw traceback.
- Manual testing of the main game features.
- Packaged Python distribution using the project `pyproject.toml`.

## Instructions

### Requirements

The project requires:

- Python 3.10 or later.
- `uv`.
- The dependencies specified in `pyproject.toml`.

The project also requires the assigned A-Maze-ing package:

    mazegenerator-2.1.0-py3-none-any.whl

### Installation

Install the project dependencies using:

    make install

The Makefile installs the dependencies defined in `pyproject.toml`
and installs the provided A-Maze-ing wheel.

### Running the game

The game can be launched with:

    make run

A configuration file can also be provided:

    make run configs.json

The underlying command used to launch the game is:

    uv run python3 pac-man.py <configuration_file>

If the configuration file is invalid or unavailable, the program falls
back to the default configuration handling implemented by the parser.

### Useful Makefile commands

    make install

Installs the project dependencies and the A-Maze-ing package.

    make run

Launches the game.

    make debug

Launches the game using the Python debugger.

    make lint

Runs Flake8 and Mypy checks.

    make lint-strict

Runs stricter Flake8 and Mypy checks.

    make clean

Removes Python and type-checking cache files.

    make clean_cache

Cleans the UV and pip caches.

    make help

Displays basic usage information.

## Controls

### Movement

The player moves using the arrow keys:

- Up: Up arrow
- Down: Down arrow
- Left: Left arrow
- Right: Right arrow

### Pause

Press `P` to pause the game and open the pause menu, which allows
resuming or returning to the main menu.

### Cheat mode

Cheat and challenge mode options are available from the Options menu:

- Max Pacgums - fills every eligible cell with a pacgum instead of the
  configured amount. (challenge mode)
- Bonus Time - doubles the level time limit.
- Invincible - disables ghost collisions.
- Ultra-pacgums - doubles the frightened-ghost duration.
- Lethargic ghosts - halves ghost movement speed.

Two additional hidden shortcuts are available during gameplay, intended
for peer review:

- `Ctrl+S` - skips the current level immediately.
- `Ctrl+L` - grants the player an extra life.

Cheat modes are intended primarily for peer review and testing.

### End screen

After a win or loss, the player is prompted to enter a name to save
their score:

- Enter/Return - Confirm the entered name and save the score.
- Backspace - Delete the last character typed.
- Esc - Skip saving and return to the main menu.

## Configuration

The game configuration is stored in a JSON file.

The configuration is validated using Pydantic models.

The main configuration fields are:

| Field | Type | Default | Allowed values / description |
|---|---|---:|---|
| `highscore_filename` | path | `Unknown` | Path to the highscore JSON file |
| `pacgum` | integer | `42` | Number of pacgums, from 1 to 100 |
| `points_per_pacgum` | integer | `10` | Points per pacgum, from 1 to 15 |
| `points_per_super_pacgum` | integer | `50` | Points per super-pacgum, from 16 to 50 |
| `points_per_ghost` | integer | `200` | Points per ghost, from 51 to 200 |
| `seed` | integer | `42` | Seed used for the first level's maze, must be greater than 0 |
| `level_max_time` | integer | `90` | Maximum time per level, from 1 to 1000 seconds |
| `levels` | list | 1 level by default | Level configuration list |

Each level contains:

| Field | Type | Default | Allowed values |
|---|---|---:|---|
| `level_id` | integer | `1` | Greater than or equal to 0 |
| `width` | integer | `10` | 10 to 30 |
| `height` | integer | `10` | 10 to 30 |

The game always provides at least 10 levels. Additional levels beyond
10 can be configured, with no fixed upper limit.

If fewer than 10 levels are provided, additional levels are generated
with valid dimensions.

Unknown configuration keys are ignored.

When a configuration contains invalid values, the parser reports a
warning and falls back to safe default values so that the game can
continue instead of crashing.

If the configuration file is not a valid JSON configuration file, the
program falls back to its default configuration handling.

The game configuration can be modified before launching the game and is
intended to be updated during the defense.

## Highscore

The game uses a persistent highscore system stored in a JSON file.

The highscore file contains a list of dictionaries. Each entry stores:

- the player's name;
- the player's score;
- the last level reached.

Only the top 10 scores are kept. Scores are sorted in descending order.

A player name must be 3 to 10 characters long, and may only contain
letters, digits, and spaces.

Scores are non-negative integers.

Highscores are loaded when the game starts and updated when a game ends.
The final score can be saved after either a victory or a game over,
including when the level time limit is reached, or skipped by pressing
Esc during name entry. Highscores are also viewable at any time from
the main menu.

The highscore system is stored in JSON because the amount of data is
small, the format is easy to inspect and modify, and it does not require
an external database.

The implementation also handles missing or invalid highscore files
through the parsing and validation mechanisms of the project.

## Maze Generation

The project uses the assigned A-Maze-ing package provided by another
group.

The package is used as-is and is not modified by this project.

The game adapts its maze-loading logic to the interface provided by the
assigned package, including picking a maze-center entry cell that avoids
landing on one of the '42' logo's blocked cells.

The generator's `perfect` parameter defaults to `False` in the assigned
package itself, which the game relies on rather than passing it
explicitly, so the generated mazes contain the loops needed for
Pac-Man-compatible corridors.

The first level uses the fixed seed `42`. Subsequent levels are randomly
generated.

The game also handles errors from the maze generator so that a generator
failure does not result in an uncontrolled traceback.

The assigned package is provided as:

    mazegenerator-2.1.0-py3-none-any.whl

## Implementation

The project is written in Python 3.10+.

The main technologies used are:

- Python for the game logic.
- Pygame for rendering and user interaction.
- Pydantic for configuration and data validation.
- The assigned A-Maze-ing package for maze generation.

The source code is divided into several functional modules.

### Parsing

The `src/parsing` module is responsible for:

- loading configuration files;
- validating configuration values;
- validating highscore data;
- handling invalid configuration values;
- managing default values.

### Game logic

The `src/game_logic` module contains the main gameplay-related logic,
including maze state, collision handling, cheat-mode bonus state, and
maze entry-cell adjustment.

### Menus

The `src/menus` module drives the main menu, options, instructions, and
high-scores screens shown before and between games.

### Player

The `src/player` module manages:

- player state;
- player movement;
- keyboard controls.

### Objects

The `src/objects` module contains gameplay objects such as:

- ghosts;
- pacgums;
- super-pacgums.

### Rendering

The `src/rendering` module handles the visual part of the game,
including:

- map rendering;
- sprite rendering and animation;
- HUD (score, lives, level, time);
- menu, high-score, and instructions screens;
- frame buffering;
- visual settings;
- game assets.

## General Software Architecture

The project follows a modular architecture organized by responsibility.

The main components are:

pac-man.py
    |
    v
Menu (Main Menu / Options / Instructions / High Scores)
    |
    v
Game / Main Logic (via MazeState)
    |
    +----------------+
    |                |
    v                v
Parsing          Game Logic
    |                |
    |                +------ Collision
    |                +------ BonusState (cheat mode)
    |                +------ Maze State
    |
    +------ Configuration
    +------ Highscores

Game Logic (via MazeState)
    |
    +------ Player
    +------ Ghosts
    +------ Pacgums
    |
    v
Rendering (Visualizer class)
    |
    +------ Frame Buffer
    +------ Map Renderer
    +------ Sprites
    +------ HUD
    +------ Menu Render
    +------ Scoreboard Render
    +------ Instructions Renderer
	

| Component | Relationship |
|---|---|
| `pac-man.py` | Builds one `MazeState` per level and drives the frame loop; never touches rendering or ghost internals directly. |
| `Menu` | Drives the main menu, options, instructions, and high-scores screens before/between games, then hands off to `MazeState` once a game starts. |
| `MazeState` | Shared context object composing `Player`, the four `Ghost` subclasses, and `Gummis`. `Ghost.move()`, `Player`, and the rendering classes all read from it, rather than passing state around as separate arguments. |
| `Ghost` (ABC) | Base class for `Blinky`/`Pinky`/`Inky`/`Clyde`. Each subclass implements its own targeting logic in `move()`; shared mode/timer state (frightened, scatter, dead) lives on the base class. |
| `BonusState` | Tracks cheat-mode toggles (max pacgums, bonus time, invincible, ultra-pacgums, lethargic ghosts) read by game logic during play. |
| `SpriteRenderState` | Built each frame from current player/ghost/gum state (`src/rendering/settings.py`), then passed to `Visualizer.render_frame()`. |
| `Visualizer` | Owns the pygame window and composes `FrameBuffer`/`MapRenderer` (maze/wall drawing), `Sprites` (player/ghost drawing), `HUD` (score/lives/level/time, game-over/victory/level-complete screens), `MenuRender`, `ScoreBoardRender`, and `InstructionsRenderer` (menu/highscore/instructions screens). Delegates actual drawing to these rather than drawing directly. |
| Parsing (`Configs`/`LevelConfig`/`Score`) | Validates the config file into typed models; the result feeds `MazeState` at construction. |

Configuration, gameplay state, ghost behavior, and rendering stay separate
layers that only communicate through `MazeState` and `SpriteRenderState`.

## Scoring

The default scoring values are:

- Pacgum: +10 points.
- Super-pacgum: +50 points.
- Edible ghost: +200 points.

The score never decreases.

Eating a super-pacgum makes the ghosts edible for a limited amount of
time.

## Game Progression

The game contains between 10 and 100 levels.

The first level uses the fixed seed `42`, while subsequent levels use
random generation.

The player keeps their score and remaining lives between levels.

A level is completed when all pacgums and super-pacgums have been eaten.
Between levels, a short "Level Complete!" splash is shown while the
next level loads.

The game ends when:

- all configured levels have been completed;
- the player loses all lives.

The default level time limit is 90 seconds. Reaching the time limit does
not end the game outright - it costs the player a life, the same as
being caught by a ghost, and the level continues once they respawn. The
game only ends once all lives are lost this way.

When the game ends, whether by victory or by running out of lives, the
player can save their final score in the highscore system.

## Ghosts

The game contains four ghosts.

Ghosts move autonomously through the maze and use behavior inspired by
the original Pac-Man game.

When normal, ghosts chase the player.

When the player eats a super-pacgum, ghosts become edible for a limited
period and move away from the player. Ghost speed increases and the
frightened duration shortens as the player advances through the levels.

When an edible ghost is eaten, it awards points and eventually returns
to its starting area.

## Testing

Testing was performed manually during development.

The main game features were tested through actual gameplay, including
movement, collisions, scoring, ghosts, configuration handling, level
progression, pause behavior, time limits, highscores, and cheat mode.

No separate automated test suite is included in the repository.

Static code quality is checked through the Makefile using:

    make lint

This runs Flake8 and Mypy.

## Project Management

The project was developed by two members over a period of three weeks.

The project management information, task distribution, timeline, risks,
blocking points, and testing plan are documented in:

[PROJECT_MANAGEMENT.md](PROJECT_MANAGEMENT.md)

## Resources

The project was developed using the following types of resources:
- Pygame documentation.
- Pydantic documentation.
- Documentation and interface information supplied with the assigned
  A-Maze-ing package.
- Classic Pac-Man gameplay references for ghost behavior and game rules.

### AI usage

AI tools were used as assistance during the project for:

- Assistance with writing the README.
- Assistance with project management documentation.
- Research purposes and explaining concepts
- Cross checking rendering code to ensure utilised pygame functions had MLX equivalents (as required in the PDF).
- Some debugging and detecting edge case bugs.
- Sprite and icon generation (generative AI)
- Brainstorming ideas in the conceptualisation phase before code was written.
- Task management.
- Identifying merge conflicts (project was not hosted on github, so claude was used in place of github pull requests)
- Code review for docstring accuracy, unused code, and encapsulation, checked against the project's own Flake8/Mypy standards.


AI was not used as a replacement for the implementation of the game.
The project code, game logic, integration, and testing were handled by
the project members.