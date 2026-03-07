"""Functions to handle certain key input events"""

import pygame


def wants_to_run(events: list[pygame.event.Event]) -> bool:
    """Function to see if player is quitting game"""
    run = True
    for event in events:
        if event.type == pygame.QUIT:
            run = False
    return run


def wants_to_pause(events: list[pygame.event.Event], pause: bool) -> bool:
    """Function to see if player is pausing game"""
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pause = not pause
    return pause
