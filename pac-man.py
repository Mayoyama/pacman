import pygame
import sys
import signal
from typing import Any
from random import randint
from src import (parsing, MazeState, SpriteRenderState, Menu, HUDState,
                 check_keypress, Direction, check_collision, BonusState,
                 write_scores)


def game_run(maze: MazeState, died: bool) -> bool:
    """Checks whether the game loop should keep running this frame.

    Args:
        maze: Current level's MazeState.
        died: Whether pacman died this frame - kept running through
            the death animation even after lives/gums/time would
            otherwise end it.

    Returns:
        False once the window closed, lives are exhausted, all gums
        are eaten, or the level timer expires - except while died is
        True, so the death animation can finish playing.
    """

    if not maze.vis.running:
        return False
    if not maze.player.lives and not died:
        return False
    if not len(maze.gummis.pacgums) and not len(maze.gummis.superpacgums):
        return False
    if maze.time < 1 and not died:
        return False
    return True


def main() -> None:
    """Runs the full game: menu, levels, scoring, and highscore saving.

    Loops forever - each pass shows the main menu, then plays through
    every configured level, then shows the game-over/victory screen
    and returns to the menu.
    """

    config = parsing()

    pygame.init()

    display_info = pygame.display.Info()
    screen_size = (display_info.current_w, display_info.current_h)

    def handle_termination(signum: int, frame: Any) -> Any:
        """Signal handler for Ctrl+C/Ctrl+Z: shuts pygame down and exits.

        Registered for SIGINT (and SIGTSTP where available) so the game
        quits cleanly.

        Args:
            signum: The signal number that triggered this handler.
            frame: The interrupted stack frame, unused - see del below.
        """

        del frame
        sig_name = "Ctrl+C" if signum == signal.SIGINT else "Ctrl+Z"

        print(f"{sig_name} detected! Terminating program.", file=sys.stderr)

        pygame.quit()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_termination)

    if hasattr(signal, "SIGTSTP"):
        sig_TSTP = getattr(signal, "SIGTSTP")
        signal.signal(sig_TSTP, handle_termination)

    while True:
        bonuses = BonusState()
        maze = MazeState((15, 15), config, screen_size, bonuses)
        menu = Menu()

        while not menu.start_game:
            if menu.run_menu(maze.vis, bonuses, str(
                    config.highscore_filename)) == "QUIT":
                pygame.quit()
                sys.exit(0)

        game_over = False
        return_to_menu = False

        for i, level in enumerate(config.levels):
            score = maze.player.score
            lives = maze.player.lives

            if i == 0:
                config.seed = 42 if config.seed is None else config.seed
            else:
                config.seed = randint(1, 200)
            maze = MazeState(
                (level.width, level.height),
                config,
                screen_size,
                bonuses,
                lv_index=i + 1
            )

            maze.player.set_score(score)
            maze.player.set_lives(lives)

            scared_timers: dict[str, int] = {}
            ghost_respawn_timers: dict[str, int] = {}
            ghost_pos: dict[str, tuple[int, int]] = {}

            for ghost in maze.ghosts:
                scared_timers[ghost.name] = 0
                ghost_respawn_timers[ghost.name] = 0
                ghost.init_pixel_pos(maze)
                ghost_pos[ghost.name] = ghost.pixel_pos

            died = False
            timed_out = False
            death_step = 0
            death_timer = 0
            death_frames: list[int] = [15, 7, 5, 3, 1, 90]

            maze.gummis.set_pacgums(
                maze._maze, config.pacgum, bonuses.max_gums)

            while game_run(maze, died):
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
                        maze.player.respawn(maze.pacstart)
                        maze.vis.reset_pac_sprite(Direction.RIGHT.value)

                        died = False
                        death_step = 0
                        death_timer = 0

                        if timed_out:
                            maze.time = maze.set_lv_timer(
                                config.level_max_time)
                            timed_out = False

                        maze.player.start_respawn_immunity_timer(75)

                        for ghost in maze.ghosts:
                            ghost.respawn(maze)
                            ghost_pos[ghost.name] = ghost.pixel_pos

                            ghost.set_scatter_mode(60)
                            scared_timers[ghost.name] = 0
                            ghost_respawn_timers[ghost.name] = 0

                        if not maze.player.lives:
                            game_over = True
                            break

                else:
                    action = check_keypress(events)

                    if action == "pause_toggle":
                        pause_action = menu.handle_pause_menu(maze.vis)

                        if pause_action == "MAIN_MENU":
                            return_to_menu = True
                            break
                        elif pause_action == "QUIT":
                            pygame.quit()
                            sys.exit(0)

                        continue

                    elif action == "skip_level":
                        maze.gummis.pacgums.clear()
                        maze.gummis.superpacgums.clear()

                        continue

                    elif action == "add_life":
                        maze.player.increase_lives()

                    elif isinstance(action, Direction):
                        maze.player.set_desired_direction(action)

                    # This must occur BEFORE other animation logic
                    # Updates player pos
                    maze.player.update()
                    maze.player.handle_immunity_timer()

                    if (
                      maze.player.direction != Direction.PAUSED
                      and not bonuses.invincible):
                        maze.player.set_invincible(False)

                    maze.handle_eaten_gums()

                    for ghost in maze.ghosts:
                        if ghost.freeze_timer > 0:
                            ghost.freeze_timer -= 1

                            if not ghost.freeze_timer:
                                ghost.dead = False

                        else:
                            if ghost.frightened:

                                if bonuses.slowpoke_ghost:
                                    frightned_speed = 1
                                else:
                                    frightned_speed = int(
                                        maze.ghost_speed * 0.7)
                                ghost.advance_pixel_pos(maze, int(
                                    max(1, frightned_speed)))

                            else:
                                ghost.advance_pixel_pos(maze, maze.ghost_speed)

                        ghost_respawn_timers[ghost.name] = ghost.freeze_timer

                        ghost_pos[ghost.name] = ghost.pixel_pos

                        if ghost.scatter:
                            scared_time = ghost.handle_scatter_mode()

                        if ghost.frightened:
                            scared_time = ghost.handle_frightened_status()
                            scared_timers[ghost.name] = scared_time

                            if (check_collision(
                                    ghost.pixel_pos,
                                    maze.player.pixel_pos,
                                    maze.collision_threshhold)
                                    and not ghost.dead):
                                maze.player.increase_score(
                                    config.points_per_ghost)
                                remaining_frightened = ghost.scared_timer

                                ghost.respawn(maze)
                                ghost_pos[ghost.name] = ghost.pixel_pos

                                ghost.eaten(
                                    maze.ghost_freeze_frames,
                                    remaining_frightened)
                                ghost_respawn_timers[ghost.name] = \
                                    ghost.freeze_timer
                                scared_timers[ghost.name] = ghost.scared_timer

                    if (not bonuses.invincible
                            and not maze.player.is_invincible):
                        for ghost in maze.ghosts:
                            if check_collision(
                                ghost.pixel_pos,
                                maze.player.pixel_pos,
                                maze.collision_threshhold
                              ):

                                if ghost.frightened or ghost.dead:
                                    pass
                                else:
                                    died = True
                                    maze.player.decrease_lives()
                                    break

                sprite_state = SpriteRenderState(
                    maze.player.direction.value,
                    maze.player.position, ghost_pos,
                    maze.gummis.superpacgums,
                    maze.gummis.pacgums,
                    maze.player.pixel_pos,
                    scared_timers,
                    ghost_respawn_timers,
                    maze.player.tolerance
                )

                maze.time -= 1

                if maze.time < 1 and not died:
                    died = True
                    maze.player.decrease_lives()
                    timed_out = True

                hud_state = HUDState(
                    maze.player.score,
                    maze.player.lives,
                    i + 1, maze.time
                )

                maze.vis.handle_events(events)
                maze.vis.render_frame(
                    sprite_state, died, death_step, hud_state)

            if return_to_menu:
                break

            if not maze.vis.running:
                pygame.quit()
                sys.exit(0)

            if not maze.player.lives:
                game_over = True
                break

            if i < len(config.levels) - 1:
                maze.vis.handle_lv_done()

        else:
            game_over = False

        if return_to_menu:
            continue

        if not maze.vis.running:
            pygame.quit()
            sys.exit(0)

        name = maze.vis.handle_end_screen(
            game_over, maze.player.score)

        if not maze.vis.running:
            pygame.quit()
            sys.exit(0)

        if name:
            maze.player.set_name(name)
            write_scores(str(
                config.highscore_filename), maze.player, level.level_id)


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"ValueError: {e}", file=sys.stderr)
    except KeyError as e:
        print(f"KeyError: {e}", file=sys.stderr)
    except AssertionError as e:
        print(f"Internal logic error: {e}", file=sys.stderr)
    except OSError as e:
        print(f"File error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Caught {e.__class__.__name__} error: {e}", file=sys.stderr)
