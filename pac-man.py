from mazegenerator import MazeGenerator
from sys import stderr
import pygame
import math
from src import (parsing, MazeState, Visualizer, PixelMath, SpriteRenderState,
                 check_keypress, Direction, Movement, Player, Gummis, Ghost,
                 Blinky, Pinky, Inky, Clyde, check_collision)


def main() -> None:
    config = parsing()
    maze_level = 0
    lv1_maze_w = config.levels[maze_level].width
    lv1_maze_h = config.levels[maze_level].height
    lv1_center = (lv1_maze_w // 2, lv1_maze_h // 2)
    if isinstance(config.seed, int) and config.seed > 0:
        seed = config.seed
    else:
        print("Invalid starting seed value, defaulting to 42", file=stderr)
        seed = 42
    mazegen = MazeGenerator((lv1_maze_w, lv1_maze_h), False, lv1_center,
                            (-1, -1), seed)
    maze = mazegen.maze
    start_col, start_row = mazegen.maze_entry
    start = (start_row, start_col)

    player = Player()  # NEEDS WIRING IN
    gums = Gummis(maze, start)
    pinky = Pinky(0, 0)
    blinky = Blinky(0, len(maze[0]) - 1)
    clyde = Clyde(len(maze) - 1, 0)
    inky = Inky(len(maze) - 1, len(maze[0]) - 1)

    ghosts_palette: dict[str, tuple[int, int, int]] = {
        "Blinky": blinky.color,
        "Pinky": pinky.color,
        "Inky": inky.color,
        "Clyde": clyde.color}

    pixel_math = PixelMath()
    vis = Visualizer(start, maze, pixel_math, ghosts_palette)
    movement = Movement(start, maze, vis.get_maze_offset(),
                        pixel_math.cell_size)

    ghosts: dict[str, Ghost] = {
        "Blinky": blinky,
        "Pinky": pinky,
        "Inky": inky,
        "Clyde": clyde}

    maze_state = MazeState(maze, movement, ghosts)

    ghost_pos: dict[str, tuple[int, int]] = {
        "Blinky": blinky.curr_pos,
        "Pinky": pinky.curr_pos,
        "Inky": inky.curr_pos,
        "Clyde": clyde.curr_pos,
    }

    died = False
    death_step = 0
    death_timer = 0
    death_frames: list[int] = [15, 7, 5, 3, 1, 90]

    # Pacman starts facing right, fully open
    last_openness = 1.0
    last_dir = Direction.RIGHT.value
    while vis.running:
        vis.set_tick()
        events = pygame.event.get()
        if died:
            if death_step < len(death_frames):
                if death_timer >= death_frames[death_step]:
                    death_timer = 0
                    death_step += 1
                else:
                    death_timer += 1

            if death_step >= len(death_frames):
                movement.direction = Direction.PAUSED
                movement.buffer_dir = Direction.PAUSED
                movement.position = start
                movement.pixel_pos = movement.cell_center(*start)
                last_openness = 1.0
                last_dir = Direction.RIGHT.value
                died = False
                death_step = 0
                death_timer = 0
        else:
            direction = check_keypress(events)
            if direction is not None:
                movement.set_desired_direction(direction)
            movement.update()  # This must occur BEFORE other animation logic

            # ghost actual pixel pos needs to be calculated and plugged in
            # after movement logic is finalised
            collision_threshhold = 12
            for ghost in (blinky, pinky, inky, clyde):
                gr, gc = ghost_pos[ghost.name]
                if check_collision(movement.cell_center(gr, gc),
                                   movement.pixel_pos, collision_threshhold):
                    died = True
                    break

            if movement.direction != Direction.PAUSED:
                last_dir = movement.direction.value
                px, py = movement.pixel_pos
                cx, cy = movement.cell_center(*movement.position)
                distance = abs(px - cx) + abs(py - cy)
                fraction = ((movement.cell_size - distance)
                            / (movement.cell_size - movement.tolerance))
                fraction = max(0.0, min(1.0, fraction))
                last_openness = math.sin(math.pi * fraction)
            # else: leave last_openness frozen at whatever it was last

            if last_openness < 0.33:
                mouth_state = "closed"
            elif last_openness < 0.66:
                mouth_state = "half"
            else:
                mouth_state = "open"

        sprite_state = SpriteRenderState(last_dir, ghost_pos,
                                         gums.superpacgums, gums.pacgums,
                                         movement.pixel_pos, mouth_state)

        vis.handle_events(events)
        vis.render_frame(sprite_state, died, death_step)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"ValueError: {e}")
    except KeyError as e:
        print(f"KeyError: {e}")
    except AssertionError as e:
        print(f"Internal logic error: {e}")
    except Exception as e:
        print(f"Caught {e.__class__.__name__}: {e}")
