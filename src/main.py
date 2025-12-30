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


def main() -> None:
    """Run the main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pyc-Man")
    clock = pygame.time.Clock()

    game_map = GameMap()

    # Create Pac-Man
    start_x = 14 * TILE_SIZE + TILE_SIZE / 2
    start_y = 23 * TILE_SIZE + TILE_SIZE / 2
    pacman = PacMan(game_map, start_x, start_y)

    # Create Ghosts
    blinky = Blinky(game_map, 14 * TILE_SIZE, 11 * TILE_SIZE)
    pinky = Pinky(game_map, 14 * TILE_SIZE, 14 * TILE_SIZE)
    inky = Inky(game_map, 12 * TILE_SIZE, 14 * TILE_SIZE, blinky)
    clyde = Clyde(game_map, 16 * TILE_SIZE, 14 * TILE_SIZE)

    ghosts: List[Ghost] = [blinky, pinky, inky, clyde]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input and Update
        pacman.handle_input()
        pacman.update(ghosts)

        current_dir = pacman.direction.value if pacman.direction else (0, 0)

        for ghost in ghosts:
            ghost.update(pacman.x, pacman.y, current_dir)

        # Game Over check
        if pacman.lives <= 0:
            print("Game Over")
            running = False

        # Draw
        screen.fill(BLACK)
        game_map.draw(screen)
        pacman.draw(screen)

        for ghost in ghosts:
            ghost.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
