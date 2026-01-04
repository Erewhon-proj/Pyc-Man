"""Main entry point for the Pyc-Man game.

This module initializes Pygame, the game map, entities, and runs the main game loop.
"""

import sys
from typing import List

import pygame

from src.game_map import GameMap
from src.ghost import Blinky, Clyde, Ghost, Inky, Pinky
from src.pacman import PacMan
from src.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


def handle_ghost_release(timer: int, blinky, pinky, inky, clyde) -> None:
    """Handles the progressive release of ghosts based on the timer."""
    if timer == 1:
        blinky.release_from_house()
    elif timer == 300:
        pinky.release_from_house()
    elif timer == 600:
        inky.release_from_house()
    elif timer == 900:
        clyde.release_from_house()


def main() -> None:
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
    blinky = Blinky(game_map, 9.5 * TILE_SIZE, 8.5 * TILE_SIZE)
    pinky = Pinky(game_map, 8.5 * TILE_SIZE, 10.5 * TILE_SIZE)
    inky = Inky(game_map, 9.5 * TILE_SIZE, 10.5 * TILE_SIZE, blinky)
    clyde = Clyde(game_map, 10.5 * TILE_SIZE, 10.5 * TILE_SIZE)

    ghosts: List[Ghost] = [blinky, pinky, inky, clyde]

    ghost_release_timer = 0  # Counter to relase ghosts

    # ----Main loop----------
    running = True
    while running:
        # Events handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Ghost exit timers
        ghost_release_timer += 1

        # Release ghosts from house each with his own timer
        handle_ghost_release(ghost_release_timer, blinky, pinky, inky, clyde)

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
