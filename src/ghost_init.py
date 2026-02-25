"""File to manage ghost initialization for game start / loop"""

from typing import List

from src.game_map import GameMap
from src.ghost import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from src.settings import GHOST_MODE_CYCLES, TILE_SIZE


def handle_ghost_release(pellets_eaten: int, timer: int, pinky, inky, clyde) -> None:
    """Handles the progressive release of ghosts based on pellets eaten and timer.

    In the original Pac-Man:
    - Blinky: starts free (already active, no release needed)
    - Pinky: exits after a short delay (60 frames / 1 second)
    - Inky: exits after 30 pellets eaten
    - Clyde: exits after 60 pellets eaten
    """
    if timer == 60:
        pinky.release_from_house()
    if pellets_eaten >= 30:
        inky.release_from_house()
    if pellets_eaten >= 60:
        clyde.release_from_house()


def get_ghost_mode(timer: int) -> str:
    """Determines the current ghost mode (SCATTER or CHASE) based on the game timer.

    Returns:
        str: "SCATTER" or "CHASE"
    """
    elapsed = timer
    for mode, duration in GHOST_MODE_CYCLES:
        if duration == -1:  # Permanent mode
            return mode
        if elapsed < duration:
            return mode
        elapsed -= duration
    return "CHASE"  # Fallback


def set_ghost_modes(ghosts: List[Ghost], mode: str, previous_mode: str) -> None:
    """Sets the mode for all ghosts and reverses their direction on mode change.

    Args:
        ghosts: List of ghost entities
        mode: New mode ("SCATTER" or "CHASE")
        previous_mode: Previous mode to detect changes
    """
    mode_changed = mode != previous_mode

    for ghost in ghosts:
        # Don't change mode if ghost is frightened or eaten
        if ghost.is_frightened or ghost.is_eaten or ghost.in_ghost_house:
            continue

        if mode == "SCATTER":
            ghost.set_state(GhostState.SCATTER, reverse_direction=mode_changed)
        elif mode == "CHASE":
            ghost.set_state(GhostState.CHASE, reverse_direction=mode_changed)


def ghost_creation(game_map: GameMap) -> List[Ghost]:
    """Initializes and returns a list containing all four ghost entities."""

    blinky = Blinky(game_map, 9.5 * TILE_SIZE, 8.5 * TILE_SIZE)
    pinky = Pinky(game_map, 8.5 * TILE_SIZE, 10.5 * TILE_SIZE)
    inky = Inky(game_map, 9.5 * TILE_SIZE, 10.5 * TILE_SIZE, blinky)
    clyde = Clyde(game_map, 10.5 * TILE_SIZE, 10.5 * TILE_SIZE)

    ghosts: List[Ghost] = [blinky, pinky, inky, clyde]
    return ghosts
