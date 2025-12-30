import sys
from typing import List

import pygame

from src.game_map import GameMap
from src.ghost import Blinky, Clyde, Ghost, Inky, Pinky
from src.pacman import PacMan
from src.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pyc-Man")
    clock = pygame.time.Clock()

    game_map = GameMap()

    # Crea Pac-Man (es. riga 23, colonna 14)
    # + TILE_SIZE/2 per centrarlo
    start_x = 9 * TILE_SIZE + TILE_SIZE / 2
    start_y = 16 * TILE_SIZE + TILE_SIZE / 2
    pacman = PacMan(game_map, start_x, start_y)

    # Crea i Fantasmi
    # Coordinate della Ghost House (approssimative, riga 14, colonne 12-16)
    blinky = Blinky(game_map, 9.5 * TILE_SIZE, 8.5 * TILE_SIZE)  # Blinky parte fuori
    pinky = Pinky(game_map, 8.5 * TILE_SIZE, 10.5 * TILE_SIZE)
    inky = Inky(game_map, 9.5 * TILE_SIZE, 10.5 * TILE_SIZE, blinky)
    clyde = Clyde(game_map, 10.5 * TILE_SIZE, 10.5 * TILE_SIZE)

    ghosts: List[Ghost] = [blinky, pinky, inky, clyde]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input e Update
        pacman.handle_input()

        # Verifica collisione Pac-Man -> Fantasmi
        pacman.update(ghosts)

        # Aggiorna IA Fantasmi
        # Se Pac-Man è fermo, passiamo (0,0) o l'ultima direzione valida
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
