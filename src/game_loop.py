"""Module that contains main functions to reset scene for gameplay loop"""

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostHouseState, GhostState
from src.pacman import PacMan
from src.settings import NUM_PELLETS


def reset_positions(pacman: PacMan, ghosts: list[Ghost]) -> None:
    """Resets Pac-Man and the ghosts to their initial positions and states."""

    # Reset Pac-Man's position and movement directions
    pacman.position.x = pacman.spawn_position.x
    pacman.position.y = pacman.spawn_position.y
    pacman.direction = Direction.NONE
    pacman.next_direction = Direction.NONE

    # Reset Ghosts' positions and states
    reset_ghosts_position(ghosts)


def reset_ghosts_position(ghosts: list[Ghost]) -> None:
    """Reset Ghosts' positions and states"""
    for ghost in ghosts:
        ghost.set_position(ghost.spawn_position.x, ghost.spawn_position.y)
        ghost.set_state(GhostState.SCATTER)
        ghost.reset_frightened_timer()

        if ghost.name == "Blinky":
            ghost.set_house_state(GhostHouseState.ACTIVE)
        else:
            ghost.set_house_state(GhostHouseState.IN_HOUSE)


def level_finished(
    pacman: PacMan, ghosts: list[Ghost], game_map: GameMap, timer: int, level: int
) -> tuple[int, int]:
    """Function to reset level upon completion to continue playing."""
    if pacman.pellets_eaten >= NUM_PELLETS:
        reset_positions(pacman, ghosts)
        game_map.reset()
        pacman.pellets_eaten = 0
        timer = 0
        level += 1  # Increment level counter
    return timer, level


def pacman_eaten(pacman: PacMan, ghosts: list[Ghost]) -> None:
    """Function to reset entities position when pacman is eaten and it still has extra lives"""
    if pacman.is_dead:
        # Reset Ghosts' positions and states
        reset_ghosts_position(ghosts)
    pacman.is_dead = False
