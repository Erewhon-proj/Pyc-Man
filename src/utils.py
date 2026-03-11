"""Utility functions for the game."""

import sys

import pygame


def handle_quit_event(event: pygame.event.Event) -> bool:
    """Handle QUIT event - exits the application. """
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    return False
