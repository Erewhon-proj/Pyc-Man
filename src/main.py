"""Main entry point for the Pyc-Man game.

This module initializes Pygame, the game map, entities, and runs the main game loop.
"""

from typing import List

import pygame

from src import highscore, menu
from src.difficulty import DifficultyManager
from src.game_loop import level_finished, pacman_eaten
from src.game_map import GameMap
from src.ghost import Ghost
from src.ghost_init import (
    get_ghost_mode,
    ghost_creation,
    handle_ghost_release,
    set_ghost_modes,
)
from src.highscore import save_high_score
from src.key_handler import wants_to_pause, wants_to_run
from src.pacman import PacMan
from src.pause import pause
from src.settings import (
    BLACK,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
)


def main() -> None:  # pylint: disable=too-many-locals
    """main game loop setup"""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pyc-Man")
    clock = pygame.time.Clock()

    while True:
        action = menu.show_start_screen(screen, clock)

        if action == "PLAY":
            game_map = GameMap()

            # Difficulty and level tracking
            level = 1
            difficulty_manager = DifficultyManager(level)

            # Pacman creation
            pacman = PacMan(
                game_map, 9 * TILE_SIZE + TILE_SIZE / 2, 16 * TILE_SIZE + TILE_SIZE / 2
            )
            pacman.set_difficulty_manager(difficulty_manager)

            # Ghost creation with difficulty manager
            ghosts: List[Ghost] = ghost_creation(game_map, difficulty_manager)

            ghost_release_timer = 0
            current_ghost_mode = "SCATTER"  # Initial mode
            is_paused = False

            # ----Main loop----------
            running = True
            while running:
                # Events handler
                events = pygame.event.get()
                running = wants_to_run(events)
                is_paused = wants_to_pause(events, is_paused)

                if not is_paused:
                    ghost_release_timer, level = level_finished(
                        pacman, ghosts, game_map, ghost_release_timer, level
                    )
                    pacman_eaten(pacman, ghosts)

                    # Update difficulty manager when level changes
                    difficulty_manager = DifficultyManager(level)
                    pacman.set_difficulty_manager(difficulty_manager)

                    # Ghost exit timers
                    ghost_release_timer += 1

                    # Release ghosts from house based on pellets eaten and timer
                    handle_ghost_release(
                        pacman.pellets_eaten,
                        ghost_release_timer,
                        ghosts,
                        difficulty_manager,
                    )

                    # Update ghost modes based on timer (SCATTER/CHASE cycles)
                    new_ghost_mode = get_ghost_mode(
                        ghost_release_timer, difficulty_manager
                    )
                    if new_ghost_mode != current_ghost_mode:
                        set_ghost_modes(ghosts, new_ghost_mode, current_ghost_mode)
                        current_ghost_mode = new_ghost_mode

                    # Pacman logic update
                    pacman.handle_input()
                    pacman.update(ghosts)

                    # Calculate pacman direction for ghosts
                    current_dir = pacman.direction.value if pacman.direction else (0, 0)

                    for ghost in ghosts:
                        ghost.update(pacman.x, pacman.y, current_dir)

                    # Game Over check
                    if pacman.lives <= 0:
                        print("Game Over")
                        running = False
                        save_high_score(screen, clock, pacman.score)

                    # Draw
                    screen.fill(BLACK)

                    game_map.draw(screen)  # map draw
                    pacman.draw(screen)  # Pac-Man draw
                    pacman.draw_score(screen)  # Draw score
                    pacman.draw_lives(screen)  # Draw lives counter

                    for ghost in ghosts:
                        ghost.draw(screen)  # Ghosts draw

                pause(is_paused, screen)

                pygame.display.flip()
                clock.tick(FPS)

        elif action == "HIGH_SCORE":
            highscore.show_high_scores_screen(screen, clock)  # show top 10 screen


if __name__ == "__main__":
    main()
