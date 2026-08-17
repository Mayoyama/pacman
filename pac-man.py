import pygame
import sys
from src import (parsing, MazeState, SpriteRenderState, Menu,
                 check_keypress, Direction, check_collision, BonusState)


def game_run(maze: MazeState) -> bool:
    if not maze.vis.running:
        return False
    if not len(maze.gummis.pacgums) and not len(maze.gummis.superpacgums):
        return False
    return True


def main() -> None:
    config = parsing()
    pygame.init()
    display_info = pygame.display.Info()
    screen_size = (display_info.current_w, display_info.current_h)
    bonuses = BonusState()
    maze = MazeState((15, 15), config, screen_size, bonuses)
    menu = Menu()

    while not menu.start_game:
        if menu.run_menu(maze.vis, bonuses) == "QUIT":
            pygame.quit()
            sys.exit(0)

    game_over = False
    for level in config.levels:
        maze = MazeState((level.width, level.height), config, screen_size,
                         bonuses)
        start_col, start_row = maze.maze_entry
        start = (start_row, start_col)

        scared_timers: dict[str, int] = {}
        ghost_respawn_timers: dict[str, int] = {}
        ghost_pos: dict[str, tuple[int, int]] = {}
        ghosts = (maze.blinky, maze.inky, maze.pinky, maze.clyde)
        for ghost in ghosts:
            scared_timers[ghost.name] = 0
            ghost_respawn_timers[ghost.name] = 0
            ghost.init_pixel_pos(maze)
            ghost_pos[ghost.name] = ghost.pixel_pos

        died = False
        death_step = 0
        death_timer = 0
        death_frames: list[int] = [15, 7, 5, 3, 1, 90]
        pac_respawn_timer = 0
        pac_respawn_frames = 150
        ghost_freeze_frames = 60
        ghost_scatter_timer = 240  # duration=(value - ghost_freeze_frames)

        maze.gummis.set_pacgums(maze._maze, config.pacgum, bonuses.max_gums)
        while game_run(maze):
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
                    pac_respawn_timer = pac_respawn_frames
                    for ghost in ghosts:
                        ghost.set_scatter_mode(pac_respawn_frames)
                        scared_timers[ghost.name] = 0
                    if not maze.player.get_lives():
                        game_over = True
                        break
            else:
                locked = pac_respawn_timer > 0
                if locked:
                    pac_respawn_timer -= 1
                else:
                    direction = check_keypress(events)
                    if direction is not None:
                        maze.player.set_desired_direction(direction)
                    # This must occur BEFORE other animation logic
                    maze.player.update()

                maze.handle_eaten_gums()

                for ghost in ghosts:
                    if ghost.freeze_timer > 0:
                        ghost.freeze_timer -= 1
                    else:
                        if ghost.frightened:
                            ghost.advance_pixel_pos(maze, int(
                                max(2, maze.ghost_speed * 0.8)))
                        else:
                            ghost.advance_pixel_pos(maze, maze.ghost_speed)
                    ghost_respawn_timers[ghost.name] = ghost.freeze_timer
                    ghost_pos[ghost.name] = ghost.pixel_pos
                    r, c = maze.player.pixel_pos
                    if ghost.scatter:
                        scared_time = ghost.handle_scatter_mode()
                        if scared_time == 0:
                            ghost.dead = False
                    if ghost.frightened:
                        scared_time = ghost.handle_frightened_status()
                        scared_timers[ghost.name] = scared_time
                        if ghost.curr_pos == maze.player.pixel_to_cell(r, c):
                            ghost.curr_pos = ghost.start_pos
                            ghost.previous_pos = None
                            ghost.init_pixel_pos(maze)
                            ghost_pos[ghost.name] = ghost.pixel_pos
                            ghost.next_pos = ghost.curr_pos
                            ghost.handle_frightened_status(reset=True)
                            ghost.dead = True
                            ghost.freeze_timer = ghost_freeze_frames
                            scared_timers[ghost.name] = 0
                            ghost_respawn_timers[ghost.name] = \
                                ghost.freeze_timer
                            ghost.set_scatter_mode(ghost_scatter_timer)
                if not locked and not bonuses.invincible:
                    for ghost in ghosts:
                        if check_collision(ghost.pixel_pos,
                                           maze.player.pixel_pos,
                                           maze.collision_threshhold):
                            if ghost.frightened or ghost.dead:
                                pass
                            else:
                                died = True
                                maze.player.decrease_lives()
                                break

            sprite_state = SpriteRenderState(
                maze.player.direction.value, maze.player.position, ghost_pos,
                maze.gummis.superpacgums, maze.gummis.pacgums,
                maze.player.pixel_pos, scared_timers, ghost_respawn_timers,
                maze.player.tolerance)

            maze.vis.handle_events(events)
            maze.vis.render_frame(sprite_state, died, death_step)

        if not maze.player.get_lives():
            break
        if not maze.vis.running:
            break
        pygame.quit()

    # PLACEHOLDER: will keep window open after lives = 0
    if game_over:
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
