import pygame
import math
from src import (parsing, MazeState, SpriteRenderState, Gummis,
                 check_keypress, Direction, check_collision)


def main() -> None:
    config = parsing()
    maze_level = 0
    lv1_maze_w = config.levels[maze_level].width
    lv1_maze_h = config.levels[maze_level].height
    maze = MazeState((lv1_maze_w, lv1_maze_h), config.seed)
    start_col, start_row = maze.maze_entry
    start = (start_row, start_col)
    gums = Gummis(maze.maze, start)

    ghosts = (maze.blinky, maze.inky, maze.pinky, maze.clyde)
    for ghost in ghosts:
        ghost.init_pixel_pos(maze)

    ghost_pos: dict[str, tuple[int, int]] = {
        "Blinky": maze.blinky.pixel_pos,
        "Pinky": maze.pinky.pixel_pos,
        "Inky": maze.inky.pixel_pos,
        "Clyde": maze.clyde.pixel_pos,
    }

    ghost_speed_factor: float = 1.0
    ghost_speed = int(maze.player.speed * ghost_speed_factor)
    collision_threshhold = 12
    died = False
    death_step = 0
    death_timer = 0
    death_frames: list[int] = [15, 7, 5, 3, 1, 90]

    # Pacman starts facing right, fully open
    last_openness = 1.0
    last_dir = Direction.RIGHT.value
    while maze.vis.running and maze.player.get_lives():
        maze.vis.set_tick()
        events = pygame.event.get()
        if died:
            if death_step < len(death_frames):
                if death_timer >= death_frames[death_step]:
                    death_timer = 0
                    death_step += 1
                else:
                    death_timer += 1

            if death_step >= len(death_frames):
                maze.player.direction = Direction.PAUSED
                maze.player.buffer_dir = Direction.PAUSED
                maze.player.position = start
                maze.player.pixel_pos = maze.player.cell_center(*start)
                last_openness = 1.0
                last_dir = Direction.RIGHT.value
                died = False
                death_step = 0
                death_timer = 0
        else:
            direction = check_keypress(events)
            if direction is not None:
                maze.player.set_desired_direction(direction)
            maze.player.update()  # This must occur BEFORE other animat logic

            for ghost in ghosts:
                ghost.advance_pixel_pos(maze, ghost_speed)
                ghost_pos[ghost.name.capitalize()] = ghost.pixel_pos

            for ghost in ghosts:
                if check_collision(ghost.pixel_pos, maze.player.pixel_pos,
                                   collision_threshhold):
                    died = True
                    maze.player.decrease_lives()
                    break

            if maze.player.direction != Direction.PAUSED:
                last_dir = maze.player.direction.value
                px, py = maze.player.pixel_pos
                cx, cy = maze.player.cell_center(*maze.player.position)
                distance = abs(px - cx) + abs(py - cy)
                fraction = ((maze.player.cell_size - distance)
                            / (maze.player.cell_size - maze.player.tolerance))
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
                                         maze.player.pixel_pos, mouth_state)

        maze.vis.handle_events(events)
        maze.vis.render_frame(sprite_state, died, death_step)


    # PLACEHOLDER: will keep window open after lives = 0
    while maze.vis.running:
        maze.vis.set_tick()
        events = pygame.event.get()
        maze.vis.handle_events(events)
        maze.vis.render_frame(sprite_state, died, death_step)

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
