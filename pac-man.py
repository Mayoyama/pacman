import pygame
import math
from src import (parsing, MazeState, SpriteRenderState, Gummis,
                 check_keypress, Direction, check_collision)


def main() -> None:
    config = parsing()
    maze_level = 0
    lv1_maze_w = config.levels[maze_level].width
    lv1_maze_h = config.levels[maze_level].height
    maze = MazeState((lv1_maze_w, lv1_maze_h), config)
    start_col, start_row = maze.maze_entry
    start = (start_row, start_col)

    scared_timers: dict[str, int] = {}
    ghost_pos: dict[str, tuple[int, int]] = {}
    ghosts = (maze.blinky, maze.inky, maze.pinky, maze.clyde)
    for ghost in ghosts:
        scared_timers[ghost.name] = 0
        ghost.init_pixel_pos(maze)
        ghost_pos[ghost.name] = ghost.pixel_pos


    died = False
    death_step = 0
    death_timer = 0
    death_frames: list[int] = [15, 7, 5, 3, 1, 90]

    while maze.vis.running:
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
                maze.vis.reset_pac_sprite(Direction.RIGHT.value)
                died = False
                death_step = 0
                death_timer = 0
                if not maze.player.get_lives():
                    break
        else:
            direction = check_keypress(events)
            if direction is not None:
                maze.player.set_desired_direction(direction)
            maze.player.update()  # This must occur BEFORE other animat logic

            maze.handle_eaten_gums()

            for ghost in ghosts:
                ghost.advance_pixel_pos(maze, maze.ghost_speed)
                ghost_pos[ghost.name] = ghost.pixel_pos
                if ghost.frightened:
                    scared_time = ghost.handle_frightened_status()
                    scared_timers[ghost.name] = scared_time

            for ghost in ghosts:
                if check_collision(ghost.pixel_pos, maze.player.pixel_pos,
                                   maze.collision_threshhold):
                    if ghost.frightened:
                        pass
                    else:
                        died = True
                        maze.player.decrease_lives()
                        break

        sprite_state = SpriteRenderState(
            maze.player.direction.value, maze.player.position, ghost_pos,
            maze.gummis.superpacgums, maze.gummis.pacgums,
            maze.player.pixel_pos, scared_timers, maze.player.tolerance)

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
