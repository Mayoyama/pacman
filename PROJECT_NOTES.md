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
├── rendering/
│   ├── __init__.py        # re-exports Visualizer — other exports pending re-decision,
│   │                       # see visualizer.py notes below
│   ├── settings.py        # RenderSettings (frozen) + UI_state (mutable) dataclasses
│   ├── frame_buffer.py    # FrameBuffer class — DONE, flake8+mypy clean except one
│   │                       # open None-safety gap, see below
│   ├── map_rendering.py   # MapRenderer class — DONE for now (renders static maze
│   │                       # walls + "42" logo)
│   ├── sprite_rendering.py# SpriteRenderer class — ported, NOT wired at all
│   └── visualizer.py      # NEW — orchestrates FrameBuffer/MapRenderer (SpriteRenderer
│                           # not yet added), owns the pygame window + render_frame()
├── main.py                # TEMPORARY wiring/test entry point — now just constructs
│                           # Visualizer + runs the game loop; will move into Engine
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
Both are meant to be constructed **once** — currently inside `Visualizer.__init__` — and
the *same instance* passed into `FrameBuffer`/`MapRenderer`/`SpriteRenderer`
constructors — single source of truth for shared values like `cell_size`, not
duplicated per class.

Design pattern: `rendering/__init__.py` re-exports what *external* code (`main.py`,
future `Engine`) needs. Sibling modules *inside* the `rendering` package (e.g.
`map_rendering.py` importing `UI_state`) should import directly from `.settings`, not
round-trip through `__init__.py`.

### `rendering/frame_buffer.py` — done for now, one open risk
`FrameBuffer(dimensions: tuple[int,int], rend_settings: RenderSettings)`:
- Computes its own pixel size from `dimensions` (grid width/height in cells) and
  `rend_settings.cell_size`/`padding`, creates its own `pygame.Surface(...,
  pygame.SRCALPHA, 32)` — FrameBuffer owns Surface creation itself.
- `_put_pixel`, `_cell_to_pixel`, `_draw_horizontal_line`/`_draw_vertical_line` were
  **made public this session** (`draw_horizontal_line`, `draw_vertical_line`,
  `cell_to_pixel`, `fill_cell` — no leading underscore) — deliberate, so `MapRenderer`/
  `SpriteRenderer` can call them from outside the class.
- **Buffer locking, reworked this session**: `self.data` used to be set once in
  `__init__` and held for the object's whole lifetime as `memoryview(self.surf.get_buffer())`.
  This kept the surface permanently locked, which crashes `blit_to_window` with
  `pygame.error: Surfaces must not be locked during blit`, since pygame refuses to blit
  a surface while something still holds direct buffer access to it. Fix: `self.data` is
  now typed `memoryview | None`, defaulting to `None`. Two new methods:
  - `lock_memview()` — sets `self.data = memoryview(self.surf.get_buffer())`.
  - `unlock_memview()` — calls `self.data.release()` (reassigning `self.data = None`
    alone does *not* release the underlying buffer/lock — the `memoryview` needs its
    own explicit `.release()`), then sets `self.data = None`.
  Lock/unlock happens **once per frame total**, not once per shape or sprite — walls,
  the logo, and (eventually) every sprite all write into the same `self.surf`, so there
  is only one lock cycle per frame regardless of how many things get drawn during it.
  This fix has not yet been re-confirmed by an actual rerun.
- **Open risk, not yet resolved**: `self.data` being `memoryview | None` means
  `_put_pixel` (and anything else indexing into `self.data`) needs an explicit
  None-check/narrowing, or mypy's None-safety checking will flag it — independent of
  the PDF's specific required flags. Not yet verified this session.
- `self.size_line = self.surf.get_pitch()` — real row byte-stride.
- Byte order verified empirically for 32-bit `SRCALPHA` pygame surfaces on
  little-endian: Blue, Green, Red, Alpha in memory.
- `blit_to_window(win_surf)` centers the maze surface in the window, accounting for
  `top_hud_height`/`btm_hud_height` reserved bands.
- Passes flake8 and the PDF's exact required mypy flags with zero issues — **except**
  the None-safety gap above, not yet checked/fixed.

### `rendering/map_rendering.py` — done for now
`MapRenderer(maze, frame_buffer, render_setting, ui_state)` — `start` parameter (used
in an earlier draft) was dropped entirely; unused.

Bugs found & fixed this session:
- `get_42_cells` looped `range(self.maze)` / `range(self.maze[0])` — ranging over a
  list, not an int. Fixed to `range(len(self.maze))` / `range(len(self.maze[0]))`.
- Coordinate order bug: `get_42_cells` appended `(c, r)`, but `_fill_logo42` unpacks
  `for r, c in self.ft_cells` and calls `frame_buff.fill_cell(r, c, ...)` —
  inconsistent with `render_grid`'s own `(row, col)` convention into
  `cell_to_pixel(r, c)`. Fixed: `get_42_cells` now appends `(r, c)` consistently.
- `_fill_logo42(self, color)` was being called from `render_grid` with no argument.
  Fixed — now called with `self.ui.logo42_color`.
- `update_grid` wasn't updating what `render_grid`/`_fill_logo42` actually read (it set
  `self._grid`/`self._fixed_cells`, but those methods read `self.maze`/`self.ft_cells`).
  Fixed to assign `self.maze = grid` / `self.ft_cells = fixed_cells` directly. Also
  fixed a type mismatch — `fixed_cells` is now typed `list[tuple[int, int]]` to match
  `self.ft_cells`'s declared type (was previously `set[tuple[int, int]]`).
- `UI_state` now injected (`ui_state: UI_state` constructor param, stored as `self.ui`)
  and actually used: `_draw_cell` passes `self.ui.wall_color` into
  `draw_horizontal_line`/`draw_vertical_line`; `_fill_logo42` is called with
  `self.ui.logo42_color`.
- Leftover dead line `self.rend_sett.cell_size` (no assignment, no use) removed from
  `__init__`.

`draw_path`, `_fill_end_cell`, `_fill_start_cell` remain deliberately removed — no
meaningful "reach the exit" concept in actual Pac-Man gameplay. `_fill_logo42` was kept
(decorative, optional) and is now wired up.

### `rendering/sprite_rendering.py` — ported, not wired at all
Unchanged this session. `SpriteRenderer` has `SPRITE_OFFSET_X`/`SPRITE_OFFSET_Y` (= 8, 7
— tuned to the *old* project's sprite, will need re-tuning), `set_sprite`, `draw_sprite`
(alpha-blending pixel loop, ported verbatim). Reaches directly into buffer internals
(`self._data`, `self._size_line`, `self._image_width`, `self._image_height`,
`self._cell_to_pixel`) rather than composing a `FrameBuffer` — not yet decided whether
to keep direct internal access or go through `FrameBuffer`'s public interface. Only
supports one sprite at a time currently — will need extending for simultaneous sprites
(pacman + 4 ghosts + many pacgums on screen at once). Not yet constructed or called by
`Visualizer`.

### `rendering/visualizer.py` — NEW this session
Design principle decided this session, **"Engine should be dumb"** — modeled on a prior
(non-42) project where `Engine` contained zero rendering code and only ever called a
couple of public methods on one `Visualizer`-type object, which centralized all
rendering wiring/complexity internally. Applying the same principle here: once `Engine`
exists, it should never construct or hold direct references to `FrameBuffer`,
`MapRenderer`, or `SpriteRenderer` — `Visualizer` is the single point of contact.

Current `Visualizer(start, maze)`:
- Constructs `RenderSettings`, `UI_state`, `FrameBuffer`, `MapRenderer` internally.
  `SpriteRenderer` construction not yet added.
- `start` parameter is a placeholder for pacman's spawn point, not yet used anywhere.
- Owns `pygame.init()`, window caption, and the actual game window
  (`pygame.display.set_mode`, sized to 70% of the detected display's width/height via
  `pygame.display.Info()`).
- Owns `self.clock` (`pygame.time.Clock()`) and `self.running` (`bool`, always `True`
  on construction; currently only ever set `False` by a `QUIT` event inside
  `render_frame`).
- `render_frame()`: polls `pygame.event.get()` for `QUIT` (sets `self.running = False`);
  calls `self.frame_buff.lock_memview()`; calls `self.map_rend.render_grid()`; calls
  `self.frame_buff.unlock_memview()`; calls `self.frame_buff.blit_to_window(self.screen)`;
  calls `pygame.display.flip()`.

Open questions, not resolved yet:
- `rendering/__init__.py` currently re-exports `RenderSettings`/`UI_state`/
  `FrameBuffer`/`MapRenderer` for external code — now that `Visualizer` is meant to be
  the only thing `Engine`/`main.py` touches, should the package's public exports shrink
  to just `Visualizer`?
- `SpriteRenderer` isn't constructed or called anywhere in `Visualizer` yet — needs
  adding once its `FrameBuffer`-composition question (above) is settled. The lock/draw/
  unlock pattern in `render_frame()` will need to wrap sprite draws too, within the same
  single per-frame lock cycle as the map.

### `main.py` — temporary only, simplified this session
Now: constructs `MazeGenerator`, pulls `maze`/`start`, constructs
`Visualizer(start, maze)`, then `while vis.running: vis.clock.tick(30); vis.render_frame()`,
then `pygame.quit()`.

Removed this session: a redundant standalone `vis.render_frame()` call before the loop
(the loop's own first iteration already calls it, so it drew nothing the loop wouldn't
have drawn a moment later anyway).

**Still present, flagged as dead code, not yet removed**: `if not vis.running: return`
immediately after construction — `vis.running` is unconditionally `True` at that point
(set at the end of `Visualizer.__init__` and untouched by anything else in it), so this
check can never actually trigger there.

Will still move into `Engine` once that exists — per "Engine should be dumb," `Engine`'s
equivalent should construct and hold only `Visualizer`, not reach into `FrameBuffer`/
`MapRenderer`/`SpriteRenderer` directly.

### `Engine` — does not exist yet, design principle decided
**"Engine should be dumb"**: owns the main game loop and (eventually) `Controls` and
game logic, but never constructs or directly touches `FrameBuffer`, `MapRenderer`, or
`SpriteRenderer` — constructs one `Visualizer` instance and calls its public methods
only (e.g. `render_frame()`), the same way the prior project's `Engine` only ever called
`wait_to_start()`/`render_frame()` on its `Visualizer`.

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
- Makefile, `.gitignore`, config file (JSON with comments), highscore system, cheat
  mode, packaging, README, and project-management docs: **not started at all** — all
  still outstanding per the PDF's mandatory requirements.

## Not started / TODO (not exhaustive, just what's been surfaced so far)

- Add explicit None-guarding for `FrameBuffer.data` (typed `memoryview | None`)
  wherever it's indexed, to satisfy mypy's None-safety checks.
- Confirm the `blit`-lock fix (`lock_memview`/`unlock_memview` with explicit
  `memoryview.release()`) actually resolves the `pygame.error` by rerunning.
- Remove the dead `if not vis.running: return` check in `main.py`.
- Decide `rendering/__init__.py`'s public exports now that `Visualizer` is meant to be
  the package's single entry point.
- Decide `SpriteRenderer`'s relationship to `FrameBuffer` (direct buffer access vs.
  public interface), extend it to handle multiple simultaneous sprites, and wire it
  into `Visualizer` (construct it there, call its draw method from `render_frame()`
  inside the same lock/unlock cycle as the map).
- Build `Controls` and decide the movement model.
- Build `Engine` (dumb — owns only a `Visualizer` instance + the loop + eventually
  `Controls`/game logic), move `main.py`'s temporary wiring into it.
- Decide who owns pacgum/super-pacgum/ghost-corner placement logic (not provided by
  `mazegenerator`).
- Build the HUD-drawing component (text rendering).
- Get the pygame/MLX-equivalence interpretation confirmed with 42 staff.
- Fix level-1 seed once real level progression exists (currently hardcoded `seed=0`,
  fully random, in `Visualizer`/`main.py`).
- Everything else in the PDF not yet touched: config loading/validation, highscore
  system, cheat mode, scoring, ghosts, Makefile, README, project management docs,
  packaging/deployment.
