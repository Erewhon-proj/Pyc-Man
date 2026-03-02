"""Main menu module"""
# pylint: disable=duplicate-code

import sys

import pygame

from src.direction import Direction
from src.game_map import GameMap
from src.ghost_init import ghost_creation
from src.pacman import PacMan
from src.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW


def show_start_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    #pylint: disable=too-many-locals
    """Show main menu screen"""

    font_title = pygame.font.Font(None, 80)
    font_menu = pygame.font.Font(None, 50)

    # Texts
    title_text = font_title.render("PYC-MAN", True, YELLOW)
    play_text = font_menu.render("PLAY", True, WHITE)
    scores_text = font_menu.render("HIGH SCORES", True, WHITE)

    # Collider rectangles
    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    scores_rect = scores_text.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)
    )
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    # Dummy map to draw characters
    dummy_map = GameMap()

    # Pac-Man positioning
    pacman = PacMan(dummy_map, SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 60)
    pacman.direction = Direction.RIGHT

    # Ghost creation
    ghosts = ghost_creation(dummy_map)

    while True:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if play_rect.collidepoint(mouse_pos):
                    return "PLAY"
                if scores_rect.collidepoint(mouse_pos):
                    return "HIGH_SCORE"

        pacman.animate()

        # Text draw
        screen.blit(title_text, title_rect)

        # Mouse hover effect
        mouse_pos = pygame.mouse.get_pos()
        play_color = YELLOW if play_rect.collidepoint(mouse_pos) else WHITE
        scores_color = YELLOW if scores_rect.collidepoint(mouse_pos) else WHITE

        screen.blit(font_menu.render("PLAY", True, play_color), play_rect)
        screen.blit(font_menu.render("HIGH SCORES", True, scores_color), scores_rect)

        # Characters draw
        pacman.draw(screen)
        for i, ghost in enumerate(ghosts):
            ghost.draw_on_menu(screen, pacman.y, i)

        pygame.display.flip()
        clock.tick(FPS)
