from mazegenerator import MazeGenerator
from rendering import Visualizer, PixelMath, SpriteRenderState
from player import check_keypress, Direction, Movement, Player
from objects import Gummis, Blinky, Pinky, Inky, Clyde
from game_logic import check_collision
import pygame
import math


def main() -> None:
    # Testing code, all of this needs to be reorganised, but
    # the overall order of instantiation matters for visual things
    maze_w = 35
    maze_h = 25
    center = (maze_w // 2, maze_h // 2)
    mazegen = MazeGenerator((maze_w, maze_h), False, center, (-1, -1), 1)
    pixel_math = PixelMath()

    maze = mazegen.maze
    start_col, start_row = mazegen.maze_entry
    start = (start_row, start_col)
    player = Player()
    

    gums = Gummis(maze, start)
    pinky = Pinky(0, 0)
    blinky = Blinky(len(maze[0]) - 1, 0)
    clyde = Clyde(0, len(maze) - 1)
    inky = Inky(len(maze[0]) - 1, len(maze) - 1)

    ghosts: dict[str, tuple[int, int, int]] = {
        "Blinky": blinky.color,
        "Pinky": pinky.color,
        "Inky": inky.color,
        "Clyde": clyde.color,
    }

    # Dummy values, remove/update in live version
    died = False
    death_step = 0
    death_timer = 0
    death_frames: list[int] = [15, 7, 5 ,3 ,1, 90]


    # Testing code, offsets to be erased in real version
    bc, br = blinky.curr_pos
    b_offset = (bc, br + 1)
    pc, pr = pinky.curr_pos
    p_offset = (pc + 1, pr + 1)
    ic, ir = inky.curr_pos
    i_offset = (ic - 2, ir - 3)
    ghost_pos: dict[str, tuple[int, int]] = {
        "Blinky": b_offset,
        "Pinky": p_offset,
        "Inky": i_offset,
        "Clyde": clyde.curr_pos,
    }

    vis = Visualizer(start, maze, pixel_math, ghosts)
    movement = Movement(start, maze, vis.get_maze_offset(),
                        pixel_math.cell_size)

    last_openness = 1.0  # starts facing right, fully open
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
                gc, gr = ghost_pos[ghost.name]
                if check_collision(movement.cell_center(gr, gc), movement.pixel_pos,
                                   collision_threshhold):
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
            # else: leave last_openness untouched - frozen at whatever it last was

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
    except AssertionError as e:
        print(f"Internal logic error: {e}")
