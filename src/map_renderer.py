"""Simple File to render screen"""

import pygame

from src.game_map import GameMap
from src.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH


def map_renderer():
    """Main function"""
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()
    game_map = GameMap()

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)
        game_map.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    map_renderer()
