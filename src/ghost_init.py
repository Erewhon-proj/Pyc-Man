"""File to manage ghost initialization for game start / loop"""

from typing import List, Optional

from src.difficulty import DifficultyManager
from src.game_map import GameMap
from src.ghost import Blinky, Clyde, Ghost, GhostState, Inky, Pinky
from src.settings import GHOST_MODE_CYCLES, TILE_SIZE


def handle_ghost_release(
    pellets_eaten: int,
    timer: int,
    ghosts: list[Ghost],
    difficulty_manager: Optional[DifficultyManager] = None,
) -> None:
    """Handles the progressive release of ghosts based on pellets eaten and timer.

    In the original Pac-Man:
    - Blinky: starts free (already active, no release needed)
    - Pinky: exits after a short delay (60 frames / 1 second)
    - Inky: exits after 30 pellets eaten
    - Clyde: exits after 60 pellets eaten
    """
    # Get level-based release thresholds
    if difficulty_manager:
        pinky_threshold = difficulty_manager.get_pinky_release_frames()
        inky_threshold = difficulty_manager.get_inky_release_pellets()
        clyde_threshold = difficulty_manager.get_clyde_release_pellets()
    else:
        # Default values
        pinky_threshold = 60
        inky_threshold = 30
        clyde_threshold = 60

    if timer >= pinky_threshold:
        ghosts[1].release_from_house()
    if pellets_eaten >= inky_threshold:
        ghosts[2].release_from_house()
    if pellets_eaten >= clyde_threshold:
        ghosts[3].release_from_house()


def get_ghost_mode(
    timer: int, difficulty_manager: Optional[DifficultyManager] = None
) -> str:
    """Determines the current ghost mode (SCATTER or CHASE) based on the game timer."""

    # Get level-based mode cycles or use default
    if difficulty_manager:
        mode_cycles = difficulty_manager.get_ghost_mode_cycles()
    else:
        mode_cycles = GHOST_MODE_CYCLES

    elapsed = timer
    for mode, duration in mode_cycles:
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


def ghost_creation(
    game_map: GameMap, difficulty_manager: Optional[DifficultyManager] = None
) -> List[Ghost]:
    """Initializes and returns a list containing all four ghost entities."""
    blinky = Blinky(game_map, 9.5 * TILE_SIZE, 8.5 * TILE_SIZE, difficulty_manager)
    pinky = Pinky(game_map, 8.5 * TILE_SIZE, 10.5 * TILE_SIZE, difficulty_manager)
    inky = Inky(game_map, 9.5 * TILE_SIZE, 10.5 * TILE_SIZE, blinky, difficulty_manager)
    clyde = Clyde(game_map, 10.5 * TILE_SIZE, 10.5 * TILE_SIZE, difficulty_manager)

    ghosts: List[Ghost] = [blinky, pinky, inky, clyde]
    return ghosts
