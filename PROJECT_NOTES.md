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
- Before writing code, check that I understand the underlying concept — ask me to
  explain it first. Guide me to the answer, don't hand it over, unless I've genuinely
  gotten stuck after real attempts (then it's fine to just give it directly).
- Point me at the problem, not the solution. Ask what I think should be done. Refer
  back to the project PDF where relevant.
- Call out style violations (flake8/PEP 8) and flag anything that risks not meeting a
  PDF requirement.
- Suggest tests rather than running/validating my code for me, unless asked directly.
- When referencing code, cite file name + function/class name + line number.
- Direct and succinct — no padding, no over-explaining.

## Team split

Two-person group.

- **Partner**: config parsing, game mechanics/algorithms (exact scope of "game
  mechanics" not fully clarified in this session — likely ghost AI, scoring, level
  progression logic; confirm if unsure).
- **Me (this repo's rendering side)**: pygame-based visual rendering and controls.

Neither of us wrote the maze generator — it's an externally assigned package (see
below), used as-is per PDF rules.

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
- Conclusion: manual pixel-by-pixel line drawing (looping `_put_pixel`) is correct and
  required — this is what real MLX-based projects do too, not a workaround.
- Movement/input: `pygame.event.get()` + tracking `KEYDOWN`/`KEYUP` into your own
  "held keys" dict, checked once per frame, maps cleanly to `mlx_key_hook` +
  `mlx_loop_hook`. **`pygame.key.get_pressed()` should be avoided** — it's a full
  keyboard-state snapshot with no MLX equivalent at all.
- Text rendering (for HUD) will need its own equivalence check when it comes up —
  `mlx_string_put`/`mlx_set_font` exist, so pygame's font module should be fine, but
  verify the specific functions used.
- Unresolved risk, not settled in this session: whether the equivalence rule scopes to
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

Gotchas discovered this session:
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
├── rendering/
│   ├── __init__.py        # re-exports RenderSettings, UI_state, FrameBuffer
│   ├── settings.py        # RenderSettings (frozen) + UI_state (mutable) dataclasses
│   ├── frame_buffer.py    # FrameBuffer class — DONE, functional, flake8+mypy clean
│   ├── map_rendering.py   # MapRenderer class — partially wired, NOT finished
│   └── sprite_rendering.py# SpriteRenderer class — ported, NOT wired at all
├── main.py                # TEMPORARY wiring/test entry point, will move into Engine
├── pyproject.toml
└── uv.lock
```

No `Controls` module and no `Engine` module exist yet as files.

## Component status

### `rendering/settings.py` — done for now
```
RenderSettings (frozen dataclass): padding=10, cell_size=10, target_fps=30,
    top_hud_height=40, btm_hud_height=40
UI_state (mutable dataclass): wall_color, logo42_color, animate_sprite, show_sprite
```
Both are meant to be constructed **once** (currently in `main()`, eventually by
`Engine`) and the *same instance* passed into `FrameBuffer`/`MapRenderer`/
`SpriteRenderer` constructors — single source of truth for shared values like
`cell_size`, not duplicated per class. `path_color`/`show_path` were deliberately
removed from `UI_state` after `draw_path` was dropped (see below).

Design pattern: `rendering/__init__.py` re-exports these (and `FrameBuffer`) so
*external* code (`main.py`, future `Engine`) does `from rendering import X`. Sibling
modules *inside* the `rendering` package (e.g. `map_rendering.py` importing
`UI_state`) should import directly from `.settings`, not round-trip through
`__init__.py`.

### `rendering/frame_buffer.py` — done for now, verified clean
`FrameBuffer(dimensions: tuple[int,int], rend_settings: RenderSettings)`:
- Computes its own pixel size from `dimensions` (grid width/height in cells) and
  `rend_settings.cell_size`/`padding`, creates its own `pygame.Surface(..., 
  pygame.SRCALPHA, 32)` — **FrameBuffer owns Surface creation itself** (decided
  deliberately: keeps pygame-buffer-format knowledge encapsulated, so `Engine` never
  needs to know how pixels are stored, just calls `frame_buffer.blit_to_window(screen)`).
- `self.data = memoryview(self.surf.get_buffer())` needs
  `# type: ignore[arg-type]` — verified real mypy limitation (pygame's `BufferProxy`
  stub doesn't declare the buffer protocol even though it works fine at runtime), not
  a bug. Confirmed no cleaner alternative exists (tried `cast`, checked for a
  `pygame-stubs` package — neither helps).
- `self.size_line = self.surf.get_pitch()` — real row byte-stride, replaces an earlier
  broken hardcoded placeholder.
- Byte order verified empirically for 32-bit `SRCALPHA` pygame surfaces on
  little-endian: Blue, Green, Red, Alpha in memory — same order the old MLX code
  assumed, so that part of the ported code needed no changes.
- `_put_pixel`, `_cell_to_pixel`, `_draw_horizontal_line`/`_draw_vertical_line` (take
  `color` as an explicit required-with-default param, not read from `UI_state` —
  keeps `FrameBuffer` fully generic/decoupled from "what a wall is"), `clear_map`,
  `_fill_cell`, `blit_to_window(win_surf)` (centers the maze surface in the window,
  accounting for `top_hud_height`/`btm_hud_height` reserved bands).
- Passes flake8 and `mypy --warn-return-any --warn-unused-ignores
  --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` (the PDF's
  exact required lint flags) with zero issues.

### `rendering/map_rendering.py` — in progress, not finished
`MapRenderer(maze, start)` — constructor now correctly holds maze data (this belongs
here, not on `FrameBuffer` — that was a mistake caught and fixed earlier in the
session). **Still missing**: no `FrameBuffer` reference, no `RenderSettings`/`UI_state`
reference. All of `_draw_cell`, `render_grid`, `_fill_logo42` still call
`self._draw_horizontal_line`/`self._draw_vertical_line`/`self._cell_to_pixel`/
`self.cell_size` as if `MapRenderer` had them itself — these need to route through an
injected `FrameBuffer` instance instead, and `cell_size` needs to come from an injected
`RenderSettings` instance (not a bare `self.cell_size`).

`render_grid`'s calls to `_fill_logo42` and dead references to the since-deleted
`draw_path`/`_fill_start_cell`/`_fill_end_cell` are still commented out — need
reactivating (for `_fill_logo42`, which was kept) and cleaning up (for the deleted
ones, which shouldn't be referenced at all anymore).

`draw_path`, `_fill_end_cell`, `_fill_start_cell` were **deliberately removed** —
ported from the old MLX project but don't apply to Pac-Man: there's no meaningful
"reach the exit" concept in actual gameplay (you win by eating pacgums), so
visualizing the entry→exit `shortest_path` or marking the exit cell isn't relevant.
`_fill_logo42` was kept (decorative, optional — my call to actually wire it up later).

### `rendering/sprite_rendering.py` — ported, not wired at all
`SpriteRenderer` has `SPRITE_OFFSET_X`/`SPRITE_OFFSET_Y` (= 8, 7 — tuned to the *old*
project's sprite, will need re-tuning for real pacman/ghost sprite assets),
`set_sprite`, `draw_sprite` (alpha-blending pixel loop, ported verbatim). Reaches
directly into buffer internals (`self._data`, `self._size_line`, `self._image_width`,
`self._image_height`, `self._cell_to_pixel`) rather than composing a `FrameBuffer` —
not yet decided whether to keep direct internal access (matches old perf-motivated
design) or go through `FrameBuffer`'s public interface instead. Only supports one
sprite at a time currently — will need extending for simultaneous sprites (pacman + 4
ghosts + many pacgums on screen at once).

### `main.py` — temporary only
Explicitly a throwaway wiring/test spot, not final structure. Currently: constructs
`MazeGenerator`, `UI_state`, `RenderSettings`, computes `maze_w`/`maze_h`, constructs
`FrameBuffer`. Will move into `Engine` once that exists.

### `Engine` — does not exist yet
Whoever/whatever this ends up being needs to: create the actual game window
(`pygame.display.set_mode`, sized for grid + both HUD bands), own the main game loop,
construct `RenderSettings`/`UI_state` once and inject the same instances into
`FrameBuffer`/`MapRenderer`/`SpriteRenderer`, own `Controls`, and take over
`MazeGenerator` construction from `main.py`.

### `Controls` — does not exist yet
Decided: separate module/package, must have **no knowledge of rendering** — only
translates input into game-facing intent. Must use event-based key tracking
(`pygame.event.get()` → `KEYDOWN`/`KEYUP` into your own held-keys dict), not
`pygame.key.get_pressed()` (see MLX-equivalence section above). Movement model itself
— continuous-while-held vs. classic Pac-Man behavior (commit to a direction, keep
moving until blocked or a new valid direction is pressed) — **not yet decided**.

## HUD

Decided: split top/bottom like the original arcade (score top, lives/level/fruit
bottom) rather than one unified band — this is why `RenderSettings` has
`top_hud_height`/`btm_hud_height` instead of a single `hud_height`. No separate
"heading" reserved dimension — if a title/heading is wanted later, it'll just be text
blitted onto the top HUD surface, no extra dimension needed. **No HUD-drawing
component exists yet at all** — reserving the pixel space is done, but nothing
actually draws score/lives/level/time text into it yet. This will need pygame's font
module, which needs its own MLX-equivalence check when it's built (likely fine, since
`mlx_string_put`/`mlx_set_font` exist, but verify the actual calls used).

## Other build/tooling notes

- `pyproject.toml` deps: `mazegenerator` (path source, see above), `pygame>=2.6.1`,
  `pydantic>=2.13.4` (likely partner's config-parsing side — not discussed in this
  session, confirm its role if picking this up cold).
- mypy note: if mypy throws `INTERNAL ERROR ... sqlite3.OperationalError: disk I/O
  error`, that's a sandbox/mounted-filesystem quirk with mypy's cache DB, not a real
  code issue — rerun with `--cache-dir` pointed at a normal local path.
- Makefile, `.gitignore`, config file (JSON with comments), highscore system, cheat
  mode, packaging, README, and project-management docs: **not started at all** in this
  session — all still outstanding per the PDF's mandatory requirements.

## Not started / TODO (not exhaustive, just what's been surfaced so far)

- Wire `MapRenderer` to compose `FrameBuffer` + hold `RenderSettings`/`UI_state`.
- Decide `SpriteRenderer`'s relationship to `FrameBuffer` (direct buffer access vs.
  public interface) and extend it to handle multiple simultaneous sprites.
- Build `Controls` and decide the movement model.
- Build `Engine`, move `main.py`'s temporary wiring into it, create the real window.
- Decide who owns pacgum/super-pacgum/ghost-corner placement logic (not provided by
  `mazegenerator`).
- Build the HUD-drawing component (text rendering).
- Get the pygame/MLX-equivalence interpretation confirmed with 42 staff.
- Fix level-1 seed once real level progression exists (currently hardcoded `seed=0`,
  fully random, in the temporary `main.py`).
- Everything else in the PDF not yet touched: config loading/validation, highscore
  system, cheat mode, scoring, ghosts, Makefile, README, project management docs,
  packaging/deployment.
