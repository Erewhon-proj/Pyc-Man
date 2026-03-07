"""Function to implement the pause function"""

import pygame

from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WHITE


def pause(is_paused: bool, screen: pygame.Surface) -> None:
    """Function to implement the pause function"""
    if is_paused:
        font = pygame.font.SysFont(None, 72)
        pause_text = font.render("PAUSE", True, WHITE)
        rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(pause_text, rect)
