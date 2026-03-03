"""Module that contains main functions to reset scene for gameplay loop"""

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostHouseState, GhostState
from src.pacman import PacMan
from src.settings import GHOST_SPEED, NUM_PELLETS

# pylint: disable=protected-access
# pylint: disable=unnecessary-dunder-call
# type: ignore[misc]


def reset_positions(pacman, ghosts):
    """Resets Pac-Man and the ghosts to their initial positions and states."""

    # Reset Pac-Man's position and movement directions
    pacman.position.x = pacman.spawn_position.x
    pacman.position.y = pacman.spawn_position.y
    pacman.direction = Direction.NONE
    pacman.next_direction = Direction.NONE

    # Reset Ghosts' positions and states
    for ghost in ghosts:
        ghost.set_position(ghost.spawn_position.x, ghost.spawn_position.y)
        ghost._state = GhostState.SCATTER
        ghost._speed = GHOST_SPEED

        if ghost.name == "Blinky":
            ghost._house_state = GhostHouseState.ACTIVE
        else:
            ghost._house_state = GhostHouseState.IN_HOUSE


def level_finished(
    pacman: PacMan, ghosts: list[Ghost], game_map: GameMap, timer: int
) -> int:
    """Function to reset level upon completion to continue playing"""
    if pacman.pellets_eaten >= NUM_PELLETS:
        reset_positions(pacman, ghosts)
        game_map.__init__()  # type: ignore[misc]
        pacman.pellets_eaten = 0
        timer = 0
    return timer


def pacman_eaten(pacman: PacMan, ghosts: list[Ghost]) -> None:
    """Function to reset entities postion when pacman is eaten and it still has extra lives"""
    if pacman.is_dead:
        # Reset Ghosts' positions and states
        for ghost in ghosts:
            ghost.set_position(ghost.spawn_position.x, ghost.spawn_position.y)
            ghost._state = GhostState.SCATTER
            ghost._speed = GHOST_SPEED

            if ghost.name == "Blinky":
                ghost._house_state = GhostHouseState.ACTIVE
            else:
                ghost._house_state = GhostHouseState.IN_HOUSE
    pacman.is_dead = False
