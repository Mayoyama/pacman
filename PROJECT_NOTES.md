# Pacman Project — Working Notes

*Purpose of this file: continuity across separate AI chat sessions. This is a working
document for the WIP repo, not the final submitted README (see PDF section IX for those
separate requirements). Update it as work progresses. Anything below reflects the state
of the repo as of the last edit to this file — verify against actual files if in doubt.*

## How to work with me (the human) on this project

This is a 42 school peer-learning project, not a "build it for me" task. Ground rules
that apply to any AI session helping on this repo:

- No assumptions. Ask before proceeding if anything is unclear.
- Never create or edit a file without explicit permission for that specific action.
  Permission from earlier in a conversation does not carry forward automatically.
- No code blocks in chat unless explicitly asked for.
- Before writing code, check that I understand the underlying concept first - ask me to
  explain it first. Guide me to the answer, don't hand it over, unless I've genuinely
  gotten stuck after real attempts (then it's fine to just give it directly).
- Point me at the problem, not the solution. Ask what I think should be done. Refer
  back to the project PDF where relevant.
- Call out style violations (flake8/PEP 8) and flag anything that risks not meeting a
  PDF requirement.
- Suggest tests rather than running/validating my code for me, unless asked directly.
- When referencing code, cite file name + function/class name + line number.
- Direct and succinct - no padding, no over-explaining.

## Team split

Two-person group.

- **Partner**: config parsing, game mechanics/algorithms (exact scope of "game
  mechanics" not fully clarified — likely ghost AI, scoring, level progression logic;
  confirm if unsure).
- **Me**: everything pygame-related — rendering, controls, and player movement.
  Lives/invincibility currently live on a `Player` class here too, but that's flagged as
  likely to be adjusted once the partner's game-mechanics/scoring logic is settled (see
  `player/player.py` below).

Neither of us wrote the maze generator — it's an externally assigned package (see
below), used as-is per PDF rules.

## Architecture principle: package self-containment

Standing rule, applies project-wide, not just to one file: **packages should not import
from each other.** `player/` and `rendering/` are meant to be blind, independent of one
another. This has driven several concrete decisions below, listed here once instead of
repeated per-section:

- Small pieces of logic needed by more than one package (e.g. cell↔pixel math, wall-bit
  checks) are **duplicated** locally in each package rather than imported from wherever
  they were first written. Accepted trade-off: a few lines of duplicated logic is
  preferable to a cross-package import.
- Shared *values* (not types) are constructed once, in `main.py`, and passed down as
  plain primitives (ints, tuples) — never as a shared custom class that both packages
  would need to import for typing purposes. See `PixelMath` below for the concrete
  case and the type-safety trade-off this implies.
- The one-way exception is `main.py`/the future `Engine`: it's allowed to import from
  both `player` and `rendering`, since it's the wiring layer sitting above both, not a
  peer package.

## Critical constraint: pygame vs MLX equivalence

PDF page 7 (Chapter IV): *"A graphical library is considered similar to MLX if each
function you use has an equivalent in the MLX library. If a function you rely on has no
MLX equivalent, it is not allowed."* This applies to pygame usage throughout the project.

Verified against the actual `42Paris/minilibx-linux` source (`mlx.h`):
- MLX has **no** shape-drawing primitives at all — no line, rect, or circle functions.
  Only `mlx_pixel_put` (single pixel), image buffer access (`mlx_new_image`,
  `mlx_get_data_addr`, `mlx_put_image_to_window`), `mlx_string_put`/`mlx_set_font`
  (bitmap text), xpm/png image loading, and event hooks (`mlx_key_hook`,
  `mlx_mouse_hook`, `mlx_loop_hook`, `mlx_hook`), plus a few utility calls
  (`mlx_get_screen_size`, mouse show/hide/move, key autorepeat toggle).
- Conclusion: manual pixel-by-pixel line drawing (looping `put_pixel`) is correct and
  required — this is what real MLX-based projects do too, not a workaround.
- Movement/input, resolved: `pygame.event.get()` + checking `KEYDOWN` events directly,
  once per frame — maps cleanly to `mlx_key_hook` + `mlx_loop_hook`.
  **`pygame.key.get_pressed()` should be avoided** — it's a full keyboard-state
  snapshot with no MLX equivalent at all. Turned out a persistent "held keys" dict
  isn't actually needed: the chosen movement style (see `player/movement.py` below)
  only ever needs "what was the last direction requested," a single discrete event,
  not continuous held-key state — simpler than originally anticipated, still
  event-based.
- Text rendering (for HUD) will need its own equivalence check when it comes up —
  `mlx_string_put`/`mlx_set_font` exist, so pygame's font module should be fine, but
  verify the specific functions used.
- Unresolved risk, not settled yet: whether the equivalence rule scopes to
  "the whole pygame library since it's your chosen graphical library" (stricter reading,
  which I lean toward) or something narrower. **Get this confirmed with 42 staff** —
  it's ambiguous enough to matter at defense.

## Assigned maze generator: `mazegenerator` v2.1.0

Installed via uv path-source dependency (see `pyproject.toml`), wheel vendored at
`installation/mazegenerator-2.1.0-py3-none-any.whl` and committed to the repo so
`uv sync` reproduces the environment for anyone (partner, peer reviewer) without
needing PyPI.

API: `MazeGenerator(size=(width, height), perfect=False, entry_cell=(x, y),
exit_cell=(x, y), seed=int)`. Generation happens inside `__init__` (construction *is*
generation). PDF requires `perfect=False` always (V.4).

Key properties:
- `.maze`: `list[list[int]]`, rows = height, cols = width. Each cell's 4 low bits
  encode walls: bit0=North(1), bit1=East(2), bit2=South(4), bit3=West(8) — a set bit
  means a wall on that side. Value `15` = a "42" logo cell (all walls closed,
  effectively solid/decorative, not just a normal wall).
- `.maze_entry` / `.maze_exit`: tuples. `exit_cell=(-1, -1)` is a sentinel (Python
  default args can't reference `size`), resolved internally to `(width-1, height-1)`
  when out of bounds — same bounds-check also clamps genuinely invalid input.
- `.shortest_path`: BFS path entry→exit as a string of N/E/S/W letters, or `False` if
  no path found.

Gotchas discovered:
- The "42" logo pattern is 5 rows × 7 cols, and only gets placed if
  `height >= 10 and width >= 14` (the fit-check doubles each pattern dimension).
  Below that, `MazeGenerator` just prints a warning and skips it — no crash.
- **Placing `entry_cell` directly on a logo cell (value 15) can break pathfinding
  entirely** — verified: `entry_cell=(8, 8)` on a 16×16 maze made `.shortest_path`
  resolve to `False`. The safe "center, between the 4 and the 2" column is
  `x = (width - 7) // 2 + 3` (the pattern's column index 3 is all-zero across every
  row of the logo, i.e. the visual gap between the digits) — any y within the logo's
  row span is safe at that x. For a 16×16 maze this is `x = 7`; `y` doesn't have to be
  exactly `7`, any row in the logo's span works.
- Current dev/test call everywhere so far: `MazeGenerator((16, 16), False, (7, 7),
  (-1, -1), 0)`. **`seed=0` means fully random (not reproducible)** per the package's
  own docstring — fine for throwaway testing, but the PDF requires level 1 specifically
  to use a fixed seed (e.g. 42); this will need to change once real level handling
  exists.
- Confirmed: nothing in `mazegenerator` places pacgums, super-pacgums, or ghost corner
  positions — it only gives you the wall grid + entry/exit + shortest path. That logic
  has to be built by one of us; not yet decided who or where.

## Repo structure (current)

```
pacman/
├── installation/
│   └── mazegenerator-2.1.0-py3-none-any.whl   (vendored, committed)
├── player/
│   ├── __init__.py
│   ├── movement.py        # Direction enum + Movement class — DONE (see below)
│   ├── controls.py        # check_keypress() function — DONE (see below)
│   └── player.py          # Player class — DONE (see below)
├── rendering/
│   ├── __init__.py        # re-exports Visualizer only
│   ├── settings.py        # RenderSettings (frozen) + UI_state (mutable) dataclasses
│   ├── frame_buffer.py    # FrameBuffer class — DONE
│   ├── map_rendering.py   # MapRenderer class — DONE for now
│   ├── sprite_rendering.py# SpriteRenderer class — ported, NOT wired at all
│   └── visualizer.py      # orchestrates FrameBuffer/MapRenderer, owns the pygame
│                           # window + game-loop-facing methods
├── main.py                # TEMPORARY wiring/test entry point (see below); will move
│                           # into Engine
├── pyproject.toml
└── uv.lock
```

No `Engine` module exists yet as a file.

## Component status

### `rendering/settings.py` — done for now
```
RenderSettings (frozen dataclass): target_fps=30, top_hud_height=40, btm_hud_height=40
UI_state (mutable dataclass): wall_color, logo42_color, animate_sprite, show_sprite
```
`padding`/`cell_size` used to live here but were **moved out** — see `PixelMath` below.
Reason: those two values are needed by both `rendering` and `player`, and the
self-containment rule (above) means neither package can import a shared dataclass type
from the other, or from a third location either, without breaking isolation. They now
live as plain values, constructed once in `main.py`.

### `main.py` — temporary, now includes `PixelMath`
Defines:
```python
class PixelMath(NamedTuple):
    cell_size: int = 20
    padding: int = 10
```
Constructed once in `main()`, passed as a plain `tuple[int, int]` to `Visualizer` (which
forwards it to `FrameBuffer`/`MapRenderer`) — single source of truth for these two
values, fanned out as primitives so no package has to import `PixelMath` itself.
`NamedTuple` chosen over a plain tuple literal so the definition is self-documenting and
mypy can catch typos in the one place it's constructed, but every consumer still
receives it as `tuple[int, int]` and unpacks it **positionally**
(`self.cell_size, self.padding = pixel_math`), not via attribute access — attribute
access was tried and reverted, because it requires the receiving parameter to be typed
as the specific `PixelMath` class, which would mean importing it from `main.py` into
`player`/`rendering`, breaking the self-containment rule. Known trade-off: mypy can't
guarantee a plain tuple passed in some other order wouldn't type-check; accepted, since
`main.py` is currently the only construction site.

Game loop now: constructs `MazeGenerator`, `PixelMath`, `Visualizer`; each frame calls
`vis.set_tick()`, pumps `events = pygame.event.get()` **once**, passes that same list to
`vis.handle_events(events)`, then calls `vis.render_frame()`. `pygame.quit()` after the
loop exits.

**Not yet wired here**: `Movement`, `Controls`, `Player` are not constructed or called
anywhere in `main.py` yet, despite all three being functionally complete on their own.
The `events` list is already available in the loop and ready to also feed
`check_keypress(events)` once that's added.

### `rendering/frame_buffer.py` — done
`FrameBuffer(dimensions: tuple[int, int], rend_settings: RenderSettings, pixel_math:
tuple[int, int])`. Unpacks `pixel_math` positionally into `self.cell_size`/
`self.padding` (see self-containment note above for why). Owns its own
`pygame.Surface(..., pygame.SRCALPHA, 32)`. Public methods: `cell_to_pixel`,
`put_pixel`, `draw_horizontal_line`/`draw_vertical_line`, `clear_map`, `fill_cell`,
`blit_to_window`, `lock_memview`/`unlock_memview`.

Buffer locking: `self.data: memoryview | None`, defaults to `None`. `lock_memview()`
sets it via `get_buffer()`; `unlock_memview()` calls `.release()` then sets back to
`None` — required because pygame refuses to blit a surface while something still holds
direct buffer access to it. `put_pixel`/`unlock_memview` both have explicit
`if self.data is not None: ... else: raise ValueError(...)` guards for mypy's
None-narrowing. One scoped `# type: ignore[arg-type]` on the `get_buffer()` call in
`lock_memview` — a real mypy stub gap (`BufferProxy` vs `Buffer` protocol), verified no
cleaner fix exists.

### `rendering/map_rendering.py` — done for now
`MapRenderer(maze, frame_buffer, render_setting, ui_state, pixel_math)` — also takes
`pixel_math` now, unpacks `self.cell_size` positionally (padding not needed here).
`get_42_cells()` scans `self.maze` for value `15` to derive logo-cell coordinates.
`render_grid()` draws walls per-cell via the wall-bitmask checks, then fills logo cells.

### `rendering/sprite_rendering.py` — ported, still not wired at all
Unchanged. `SpriteRenderer` reaches directly into buffer internals rather than
composing `FrameBuffer` through its public interface — not yet decided which way to go.
Only supports one sprite at a time. Not yet constructed or called by `Visualizer`. Will
need `Movement`'s `pixel_pos`/`direction` (or equivalent accessor methods) to know where
to draw Pac-Man each frame — not yet connected.

### `rendering/visualizer.py` — done for current scope
`Visualizer(start, maze, pixel_math)`: constructs `RenderSettings`, `UI_state`,
`FrameBuffer`, `MapRenderer` (all pass `pixel_math` through where needed); owns
`pygame.init()`, the window, `self.clock`, `self.running`.

`handle_events(events: list[pygame.event.Event])` — **new**, split out of
`render_frame()`. Only checks for `QUIT` and sets `self.running = False`. Exists so
`main.py` can own the single `pygame.event.get()` call per frame (pygame's event queue
is drained by that call — only one place per frame should call it) and hand the same
list to both `Visualizer` and, once wired in, `Controls`. Same encapsulation pattern as
`set_tick()` — `main.py` never touches `self.running` directly.

`render_frame()` no longer pumps events itself — just locks, clears, renders the grid,
unlocks, blits, and flips.

### `Engine` — does not exist yet
Still just a design principle: owns the main loop, constructs one `Visualizer` and
(eventually) `Movement`/`Controls`/`Player`, never reaches into `FrameBuffer`/
`MapRenderer`/`SpriteRenderer` directly. `main.py`'s current event-pump-once-and-fan-out
structure is effectively a preview of what `Engine`'s loop should look like.

### `player/movement.py` — done, functionally complete
`Direction` enum: `UP`, `DOWN`, `LEFT`, `RIGHT`, `PAUSED`.

`Movement(start: tuple[int, int], maze: list[list[int]], pixel_math: tuple[int, int])`:
- `self.cell` — the grid cell currently being walked **toward** (not necessarily the
  cell physically occupied mid-transit — see `update()` below).
- `self.pixel_pos` — continuous position, initialized via `cell_center(*start)`
  (center-based, not top-left — deliberate, see below).
- `self.direction` / `self.buffer_dir` — direction actually moving vs. last direction
  requested by input (buffered-input model, see Controls/MLX-equivalence above).
- `self.speed` / `self.tolerance` — derived from `cell_size`, not fixed constants:
  `frames_per_cell = 4; self.speed = max(1, self.cell_size // frames_per_cell)`,
  `self.tolerance = self.speed`. The `max(1, ...)` guards against `cell_size` small
  enough to floor-divide to zero. `frames_per_cell = 4` was picked by researching the
  actual Pac-Man Dossier speed tables (100% speed = 75.76 px/sec at 60fps/8px tiles;
  level 1 runs at 80% of that, ≈4 frames to cross a tile) and reproducing that same
  time-per-cell at this project's 30fps/`cell_size`-based scale.
- `tolerance` needs to be at least `speed`, or a given frame's movement can step clean
  over the "centered" window without ever registering — not just an arbitrary choice.

Own local copies (not imported from `rendering`, per the self-containment rule):
`cell_to_pixel` (top-left corner, matches `FrameBuffer`'s version in meaning), plus a
new `cell_center` (top-left + half `cell_size`, used for the actual centering/tolerance
math — `pixel_pos`/"centered" means distance to the cell's true center, not its corner).
Also local copies of the four `_has_N/E/S/W_wall` bit checks (bit0=N, bit1=E, bit2=S,
bit3=W, matching `mazegenerator`'s encoding and `MapRenderer`'s versions).

`has_blocked_wall(direction)` — takes a `Direction` param (not hardcoded to
`self.direction`), so it can check either the current direction or the buffered one.
Returns `True` when a wall blocks that direction — name and boolean sense agree.

`set_desired_direction(direction)` — buffers input, doesn't move anything itself.

`_is_centered()` — `abs(px - cx) <= tolerance and abs(py - cy) <= tolerance` against
`cell_center(*self.cell)`. (Must use `abs()` on both axes — an earlier draft without it
was silently direction-dependent: correct-looking when approaching from one side,
almost always `True` when approaching from the other.)

`update()` — the per-frame state machine, movement style = traditional Pac-Man (commit
to a direction, keep going until wall-blocked or a new valid buffered direction is
available at a cell center):
- Not centered: just advance `pixel_pos` by `speed` in `self.direction`. No wall checks
  happen mid-transit.
- Centered: if `buffer_dir` isn't wall-blocked, take it (`self.direction = buffer_dir`).
  Else if `self.direction` is now wall-blocked, stop (`Direction.PAUSED`). Otherwise
  leave `self.direction` as-is (keep going straight). If the resolved direction isn't
  `PAUSED`, retarget `self.cell` to `_next_cell(self.direction)` — the adjacent cell one
  step over — so `self.cell` again represents "where I'm walking toward" and next
  frame's `_is_centered()` check has a new target to measure against.

`_next_cell(direction)` — small helper, `(row, col)` shifted one step per direction; no
maze-bounds checking (relies on `mazegenerator` always walling off the maze's outer
edge, so `has_blocked_wall` should always catch an out-of-bounds step first — not
independently verified this session).

Not yet done: no `get_render_position()`/`get_facing()`-style accessors — `pixel_pos`/
`direction` are plain public attributes right now, not wrapped in getter methods.
Whether that's fine as-is or should be wrapped is undecided. `__init__`'s signature is
still one long unwrapped line — flagged as a likely flake8 line-length violation,
inconsistent with how `frame_buffer.py`'s constructor is wrapped; not yet fixed.
flake8/mypy have not actually been run against this file this session — only reviewed
by reading.

### `player/controls.py` — done
Deliberately **not** a class — reasoned through explicitly: a stateless
class-with-only-static-methods is unnecessary ceremony in Python, and the PDF's OOP
requirement is about the project's overall architecture (which has plenty of real
stateful classes elsewhere), not a mandate that literally everything must be wrapped in
one. `Controls` also doesn't hold a reference to `Movement` — kept decoupled, same as
the rest of the self-containment principle.

```python
def check_keypress(events: list[pygame.event.Event]) -> Direction | None:
```
Loops the frame's events, checks `event.type == pygame.KEYDOWN` and `event.key` against
`pygame.K_UP/DOWN/LEFT/RIGHT`, returns the matching `Direction` or `None` after checking
every event (an earlier draft returned `None` on the *first* non-matching event via an
`else` inside the loop — bug, since pygame batches multiple events per frame and that
would silently drop real key presses sitting later in the same batch; fixed).

No persistent "held keys" state — not needed for this movement style (see
MLX-equivalence section above).

**Not yet wired**: nothing in `main.py` calls `check_keypress(events)` or feeds its
result into `movement.set_desired_direction(...)` yet.

### `player/player.py` — done for now, likely to change
```python
class Player:
    def __init__(self, lives: int = 3) -> None: ...
    def get_lives(self) -> int: ...
    def increase_lives(self, amount: int = 1) -> None: ...  # raises if amount < 1
    def decrease_lives(self) -> int: ...  # raises if already at 0, else decrements + returns
    def set_invincible(self, value: bool) -> None: ...
    def get_invincible(self) -> bool: ...
```
Deliberately holds **no position** — that's `Movement`'s job entirely, to avoid two
sources of truth for where Pac-Man is. Converted from a pseudocode draft that had a
real bug (`decrease_lives` computed `self.lives - 1` but never actually assigned it, so
lives never actually decreased) — fixed so the mutation persists.

Flagged as likely to be adjusted once the partner's game-mechanics/scoring logic is
settled — lives/scoring will probably need to integrate with whatever they build for
collision/scoring rules.

## HUD

Decided: split top/bottom like the original arcade (score top, lives/level/fruit
bottom) rather than one unified band — this is why `RenderSettings` has
`top_hud_height`/`btm_hud_height` instead of a single `hud_height`. No separate
"heading" reserved dimension — if a title/heading is wanted later, it'll just be text
blitted onto the top HUD surface, no extra dimension needed. **No HUD-drawing
component exists yet at all**. This will need pygame's font module, which needs its own
MLX-equivalence check when it's built (likely fine, since `mlx_string_put`/
`mlx_set_font` exist, but verify the actual calls used).

## Other build/tooling notes

- `pyproject.toml` deps: `mazegenerator` (path source, see above), `pygame>=2.6.1`,
  `pydantic>=2.13.4` (likely partner's config-parsing side — confirm its role if
  picking this up cold).
- mypy note: if mypy throws `INTERNAL ERROR ... sqlite3.OperationalError: disk I/O
  error`, that's a sandbox/mounted-filesystem quirk with mypy's cache DB, not a real
  code issue — rerun with `--cache-dir` pointed at a normal local path.
- Pattern worth reusing: when a value (not a type) needs to be shared across
  self-contained packages, construct it once in `main.py`/`Engine`, type it precisely
  there (e.g. a `NamedTuple`) for that one construction site's own type-safety, but pass
  it to consumers as a plain structural type (`tuple[int, int]`) that needs no import.
  See `PixelMath` above.
- Makefile, `.gitignore`, config file (JSON with comments), highscore system, cheat
  mode, packaging, README, and project-management docs: **not started at all** — all
  still outstanding per the PDF's mandatory requirements.

## Not started / TODO (not exhaustive, just what's been surfaced so far)

- Wire `Movement`, `Controls`, `Player` into `main.py`: construct instances, call
  `check_keypress(events)` each frame and feed a non-`None` result into
  `movement.set_desired_direction(...)`, call `movement.update()` each frame.
- Decide how `SpriteRenderer` reads Pac-Man's position/direction from `Movement` for
  drawing — plain attribute access (`movement.pixel_pos`/`movement.direction`) or
  wrapper accessor methods.
- Fix `player/movement.py`'s `__init__` — one long unwrapped signature line, likely a
  flake8 line-length violation; wrap it like `frame_buffer.py`'s constructor. Run
  flake8/mypy against the file for real (only reviewed by reading so far).
- Decide `SpriteRenderer`'s relationship to `FrameBuffer` (direct buffer access vs.
  public interface), extend it to handle multiple simultaneous sprites, and wire it
  into `Visualizer`.
- Build `Engine` (owns a `Visualizer` + `Movement`/`Controls`/`Player` + the loop),
  move `main.py`'s temporary wiring into it.
- Decide who owns pacgum/super-pacgum/ghost-corner placement logic (not provided by
  `mazegenerator`).
- Build the HUD-drawing component (text rendering).
- Get the pygame/MLX-equivalence interpretation confirmed with 42 staff.
- Fix level-1 seed once real level progression exists (currently hardcoded `seed=0`,
  fully random, in `main.py`).
- Revisit `Player`'s lives/scoring once the partner's game-mechanics/scoring logic
  exists — likely needs integration, not just standalone methods.
- Everything else in the PDF not yet touched: config loading/validation, highscore
  system, cheat mode, ghosts, Makefile, README, project management docs,
  packaging/deployment.
