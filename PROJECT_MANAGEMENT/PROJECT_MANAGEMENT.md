# Project Management

## 1. Project Overview

This project is a Pac-Man game developed as part of the 42 curriculum.

The project was completed by two developers over a period of two weeks.

The main objectives were to implement the required Pac-Man gameplay, integrate the assigned A-Maze-ing maze generator, provide a persistent highscore system, handle configuration files robustly, and deliver a functional and testable game.

## 2. Team Organization

The project was developed by:

- `mde-cat`
- `speterse`

### `mde-cat`

Main responsibilities:

- Configuration parsing.
- Algorithmic work.
- Part of the game logic.
- Ghost algorithms and behavior.

### `speterse`

Main responsibilities:

- Rendering "engine" (Visualiser class).
- Sprite animation and rendering.
- Part of the game logic.
- HUDs.
- Debugging/testing.
- Menu logic.
- Pause menu.
- Victory/game over screens.
- High score screen.
- Instructions screen.
- Player movement and controls.
- Collision detection.
- Integration of visual elements and gameplay.
- Mypy/Flake8 compliance.
- Updating project management documentation.
- Docstrings. 
- Overall codebase cohesion.

Both developers contributed to the game logic and integration of the different components.

## 3. Communication

The team used two main communication methods:

- In-person discussions.
- Slack for remote communication.

Technical decisions and problems were generally discussed between the two members, with communication used to coordinate work and integrate the different parts of the project. Unfortunately some lapses and breakdowns in communication led to delays, misunderstandings and unnecessary refactoring.


## 4. Timeline

The project was developed over two weeks.

### Week 1

Main objectives:

- Configuration parsing.
- Initial visualization work.
- Initial game architecture.
- Ghost algorithms.
- Beginning of game logic.

The first week focused on establishing the main technical foundations of the project and implementing the first gameplay components.

### Week 2

Main objectives:

- Completion of visualization.
- Completion and integration of game logic.
- Integration of the different modules.
- Manual testing.
- Bug fixing and refactoring.

The second week focused on bringing the different components together and making the complete game functional.

### Week 3

Main objectives:

Completion of the pause menu.
Completion of cheat mode (Options menu bonuses, Ctrl+S level skip, Ctrl+L extra life).
Score handling.
Final bug fixing and polish.
Packaging and final manual testing.

## 5. Task Distribution

The work was handled according to the main areas of the project.

| Area | `mde-cat` | `speterse` |
|---|---|---|
| Parsing | Main responsibility | Support |
| Ghost status logic | Shared | Shared |
| Ghost movement algorithms | Main responsibility | Support |
| Game logic | Shared | Shared |
| Player movement and controls | Support | Main responsibility |
| Visualization / Rendering engine | None | Main responsibility |
| Sprite animation and rendering | None | Main responsibility |
| Maze rendering | None | Main responsibility |
| HUD | None | Main responsibility |
| Menu logic and rendering | None | Main responsibility |
| Pause menu | None | Main responsibility |
| Victory/game over screens | None | Main responsibility |
| High score screen | None | Main responsibility |
| Score JSON writing | Main responsibility | None |
| Instructions screen | None | Main responsibility |
| Collision detection | Support | Main responsibility |
| Integration | Support | Main responsibility |
| Testing | Support | Main responsibility |
| Code quality (Mypy/Flake8) | None | Main responsibility |
| Docstrings | None | Main responsibility |
| Documentation (PM doc, README) | Shared | Shared |
| Codebase cohesion | Support | Main responsibility |

At first, we decided to work independently on tasks that took our own interests, which  allowed both developers to work independently on different parts while keeping game logic  as a shared responsibility.

## 6. Development Approach

The project was developed incrementally.

The team first implemented the core technical components, then added gameplay features and visualization, and finally integrated and tested the complete game.

Because the project initially had a short two-week deadline, priority was given to the mandatory requirements of the subject.

Features were integrated progressively rather than waiting until the end of the project.

## 7. Project Risks

Several risks were identified during development.

| Risk | Impact | Mitigation |
|---|---|---|
| Different availability between developers | High | Attempted to divide work and communicate through Slack |
| Limited time to work together | High | Work independently on defined components and integrate regularly |
| Different coding styles | Very High | Refactor and adapt interfaces during integration |
| Configuration errors | Medium | Validate configuration values and provide safe defaults |
| Maze generator failure | High | Handle generator errors without uncontrolled crashes |
| Integration problems | Mid-High | Test the complete game manually after integrating components |
| Limited development time | High | Prioritize mandatory subject requirements |

## 8. Blocking Points and Difficulties

### Availability

One of the main organizational difficulties was the different availability of the two developers.

`speterse` was a lifeguard, while `mde-cat` was mainly available in the morning.

`speterse` also experienced health complications during the second and third week, which delayed parts of the code.

This limited the amount of time during which both developers could work together.

The team compensated for this by dividing the work and using Slack to communicate when working separately.

`speterse` also spend extra time every evening and on both days every weekend to try stay on schedule, to compensate for not being as available on weekdays during the day.

### Refactoring and Integration

The two developers had different coding styles.

As a result, a modertate amount of refactoring was more complicated that necessary when combining the different parts of the project.

This was especially relevant because the project was planned to be completed in only two weeks.

Attempts were made to reduce impact through discusions.

### Time Management

A short project duration projection of about 2 weeks was another important constraint.

The majority of the project was developed within a 2-3 week period, so the team prioritized individual tasks that could be completed without requiring components of the other member's code.

## 9. Configuration Management

The configuration system was implemented using Pydantic models.

Configuration values are checked against their allowed ranges.

Unknown configuration keys are ignored.

Invalid values generate warnings and are replaced by safe default values so that the game can continue instead of crashing.

The game also creates or falls back to appropriate configuration and highscore files when required.

The configuration can be modified before launching the game and is expected to be updated during the defense.

## 10. Maze Generator Management

The project uses the assigned A-Maze-ing package without modifying it.

The maze generator is installed from the provided wheel:

    mazegenerator-2.1.0-py3-none-any.whl

The project adapts its own loader to the interface of the assigned package.

`PERFECT=False` is used to generate corridors suitable for Pac-Man.

The first level uses the fixed seed `42`, while subsequent levels are randomly generated.

Generator errors are handled so that they do not result in an uncontrolled traceback.

## 11. Highscore Management

The highscore system stores scores persistently in a JSON file.

The data is represented as a list of dictionaries containing:

- player name;
- score;
- last level reached.

Only the top 10 scores are retained.

Scores are sorted in descending order.

Player names are limited to 10 characters and are validated separately before being stored.

The system is designed to continue operating even when the highscore file is missing or contains invalid data.



## 12. Acceptance Test Plan

Testing was performed manually rather than through an automated test suite.

The following features were checked during development.

| Feature | Test | Expected result | Actual result | Bug(s) found / fixed |
|---|---|---|---|---|
| Player movement | Press arrow keys | Player moves in the selected direction | feature worked as intended on initial testing | only minor tweaks with movement speed needed. Also minor drifting of pacman sprite from the center of the cell, which was fixed while fixing the movement speed (related) |
| Wall collision | Move into a wall | Player cannot pass through the wall | no bugs found | None |
| Pacgum | Eat a pacgum | Score increases by 10 | Matches expected behavior | None |
| Super-pacgum | Eat a super-pacgum | Score increases by 50 and ghosts become edible | Matches expected behavior | None |
| Ghost collision | Touch a normal ghost | Player loses a life | Matches, once fixed | Death animation could be cut short if lives hit 0 mid-animation, skipping straight to game over; fixed by decoupling the lives-check from the frame loop's exit condition |
| Respawn | Lose a life | Player respawns in the middle | Matches, once fixed | Player could be instantly re-killed by a ghost standing near the respawn point; fixed with a temporary invincibility + movement lock after respawn |
| Lives | Lose all lives | Game ends | Matches expected behavior | None |
| Ghost eating | Eat an edible ghost | Score increases by 200 | DONE | Score-per-ghost logic was missing initially; added so eating an edible ghost awards the configured points; Problem occured when pacman sat in the corner and received infinite points by consming the still frightened ghost |
| Ghost behavior | Observe normal ghosts | Ghosts chase the player | generally works ok | known bugs include ghosts getting trapped in small square rooms and dead ends, and ghosts beelining for pacman after being eaten |
| Ghost edible behavior | Eat a super-pacgum | Ghosts become edible and move away | Matches, once fixed | Reusing "frightened" to make eaten ghosts retreat also triggered their blue tint/pulse unintentionally; a separate scatter mechanism was built to decouple movement behavior from visual state. Eaten ghosts also briefly flashed visible for one frame before disappearing; fixed by correcting when the invisibility timer gets recorded |
| Pause | Press P | Game pauses/resumes | DONE | no problems |
| Cheat mode | Cheat menu and hidden keys | Player receives the cheat-mode behavior | DONE | no bugs found |
| Level completion | Eat all pacgums | Level is completed | implemented and working | None |
| Level progression | Complete a level | Next level starts | implemented and working | None |
| Multiple levels | Play through levels | Configured levels can be completed | Matches expected behavior | None |
| Time limit | Wait until the limit | Game ends and final score can be saved | Matches expected behavior | None |
| Highscore | Finish a game | Player can enter a name and save the score | Matches expected behavior | None |
| Highscore limit | Add more than 10 scores | Only the top 10 are retained | Matches expected behavior | None |
| Configuration | Use valid values | Values are accepted | Matches expected behavior | None |
| Invalid configuration | Use invalid values | Warning is displayed and safe defaults are used | Matches expected behavior | None |
| Unknown keys | Add unknown configuration keys | Unknown keys are ignored | Matches expected behavior | None |
| Maze generation | Start levels | Mazes are generated correctly | Matches expected behavior | None |
| Cheat mode (reviewer) | Test gameplay with cheat enabled | Reviewer can test features more easily | Matches expected behavior | None |


## 13. Bugs and Corrections

During development, problems were identified mainly during manual integration and gameplay testing.

The main areas requiring attention were:

- Time management and level timeout behavior.
- Integration between visualization and game logic.
- Refactoring caused by differences in coding styles.
- Configuration validation and error handling.
- Integration of the maze generator.
- Correct interaction between ghosts, the player, and scoring.
- Correct handling of pygame ticks/windows/etc and ensuring that all 
   visualisation used only things that had MLX equivalents
- Ensuring correct Main menu -> game -> win/lose -> record score ->Main menu loop

These issues were mostly addressed during the second week while integrating the different components.

### Actual Progress Tracking

| Week | Planned (Section 4) | Actual | Notes / Deviations |
|---|---|---|---|
| Week 1 | Configuration parsing; initial visualization; initial game architecture; ghost algorithms; beginning of game logic | all goals achieved | differences in coding practices meant that the overall base structure of the code was reworked several times |
| Week 2 | Completion of visualization; completion/integration of game logic; integration of modules; manual testing; bug fixing and refactoring | mostly complete | no menu, still bugs in the code, though most were identified and removed this week |
| Week 3 | Develeopment wrap up and finalisation.  | complete | Pause menu, several screens (victory/gameover/lv complete), cheat mode (Options menu bonuses, Ctrl+S skip level, Ctrl+L extra life), and ghost-eating score handling were finished during this week, having still been incomplete at the end of Week 2 |


## 14. Code Quality

The project requires Python 3.10+ and Flake8 standards.

Mypy was used for static type checking.

The Makefile provides two relevant commands:

    make lint

and:

    make lint-strict

These commands run Flake8 and Mypy checks.

Wherever possible, the codebase was structured modularly. Most packages were written as stand-alone components that can be reused in other projects, provided the required data is supplied. Care was taken to ensure the codebase adhered to OOP principles.

The project also aims to handle exceptions gracefully, especially for configuration files, highscore files, and maze generation. Errors are printed to sys.stderr.

Context managers are used for file operations where appropriate.

All functions and classes are documented with docstrings.

## 15. Packaging

The project is prepared as a Python package using the project's
`pyproject.toml`.

The intended build command is:

    uv build

The generated wheel is placed in the `dist/` directory.

The package configuration is designed to allow the project to be
distributed independently from the development workflow.

The final packaged game can be distributed as a ZIP archive and
provided through the project's unlisted/private Itch.io page.

## 16. Use of AI

AI assistance was used during the project for:

- Assistance with writing the README.
- Assistance with project management documentation.
- Research purposes and explaining concepts
- Cross checking rendering code to ensure utilised pygame functions had MLX equivalents (as required in the PDF).
- Some debugging and detecting edge case bugs.
- Brainstorming ideas in the conceptualisation phase before code was written.
- Task management.
- Identifying merge conflicts (project was not hosted on github, so claude was used in place of github pull requests)
- Code review for docstring accuracy, unused code, and encapsulation, checked against the project's own Flake8/Mypy standards.

AI was used as a documentation and organizational aid. All implementation logic
and technical decisions were made and integrated by the
project members. Speterse used Claude co-work. 


## 17. Project Review

The project management process focused on dividing responsibilities,
communicating regularly, implementing the mandatory features first, and
using the second week for integration and manual testing.

The main constraints were the initial, tight two-week development timeline, combined with the differing availability and coding styles of the two developers.

Despite these constraints, the team successfully completed the required
functionality, including main gameplay, configuration, maze
generation, highscore, visualization, and testing requirements.
