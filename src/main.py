"""Main entry point for the Pyc-Man game.

This module initializes Pygame, the game map, entities, and runs the main game loop.
"""

import sys
from typing import List

import pygame

from src.ghost_init import *
from src.game_map import GameMap
from src.ghost import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from src.pacman import PacMan
from src.settings import (
    BLACK,
    FPS,
    GHOST_MODE_CYCLES,
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

    game_map = GameMap()

    # Pacman creation
    pacman = PacMan(
        game_map, 9 * TILE_SIZE + TILE_SIZE / 2, 16 * TILE_SIZE + TILE_SIZE / 2
    )

    # Ghost creation
    ghosts: List[Ghost] = ghost_creation(game_map)

    ghost_release_timer = 0
    current_ghost_mode = "SCATTER"  # Initial mode

    # ----Main loop----------
    running = True
    while running:
        # Events handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Ghost exit timers
        ghost_release_timer += 1

        # Release ghosts from house based on pellets eaten and timer
        handle_ghost_release(
            pacman.pellets_eaten, ghost_release_timer, ghosts[1], ghosts[2], ghosts[3]
        )

        # Update ghost modes based on timer (SCATTER/CHASE cycles)
        new_ghost_mode = get_ghost_mode(ghost_release_timer)
        if new_ghost_mode != current_ghost_mode:
            set_ghost_modes(ghosts, new_ghost_mode, current_ghost_mode)
            current_ghost_mode = new_ghost_mode

        # Pacman logic update
        pacman.handle_input()
        pacman.update(ghosts)

        # Calculate pacman directiopn for ghosts
        current_dir = pacman.direction.value if pacman.direction else (0, 0)

        for ghost in ghosts:
            ghost.update(pacman.x, pacman.y, current_dir)

        # Game Over check
        if pacman.lives <= 0:
            print("Game Over")
            running = False

        # Draw
        screen.fill(BLACK)

        game_map.draw(screen)  # map draw
        pacman.draw(screen)  # Pac-Man draw

        for ghost in ghosts:
            ghost.draw(screen)  # Ghosts draw

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
