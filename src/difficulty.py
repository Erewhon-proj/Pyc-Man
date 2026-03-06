"""Difficulty progression system for Pyc-Man.

This module manages all difficulty parameters that scale with game levels,
including ghost speeds, frightened duration, release timing, and mode cycles.
"""

from src import settings


class DifficultyManager:
    """Manages difficulty progression based on current game level.

    This class provides methods to calculate various game parameters that
    increase difficulty as the player progresses through levels. The progression
    is designed to create a challenging but fair experience.

    Attributes:
        level: Current game level (1-based).
    """

    def __init__(self, level: int = 1) -> None:
        """Initialize difficulty manager with a specific level.

        Args:
            level: Current game level, defaults to 1.
        """
        self._level = level

    @property
    def level(self) -> int:
        """Get current level."""
        return self._level

    def get_ghost_speed(self) -> float:
        """Calculate base ghost speed for current level.

        Ghost speed increases by 5% per level for the first 2 levels,
        then plateaus at the maximum speed to prevent impossible gameplay.

        Returns:
            Base ghost speed in pixels per frame.
        """
        base = settings.GHOST_SPEED
        # Only increase for first 2 levels, then plateau
        increase = min(self.level - 1, 2) * settings.GHOST_SPEED_INCREMENT_PER_LEVEL
        return min(base + increase, settings.MAX_GHOST_SPEED)

    def get_chase_speed_multiplier(self) -> float:
        """Calculate speed multiplier for CHASE mode.

        CHASE mode becomes progressively more aggressive, with ghosts
        moving faster in this mode compared to SCATTER mode.

        Returns:
            Speed multiplier (1.0 = normal, up to 1.4 = 40% faster).
        """
        # Increase by 10% per level for first 4 levels
        multiplier = (
            1.0 + min(self.level - 1, 4) * settings.CHASE_SPEED_INCREMENT_PER_LEVEL
        )
        return min(multiplier, settings.MAX_CHASE_SPEED_MULTIPLIER)

    def get_frightened_duration_frames(self) -> int:
        """Calculate frightened mode duration in frames.

        Frightened duration decreases by 2 seconds per level for the first
        3 levels, then by 0.5 seconds per additional level, with a minimum
        of 2 seconds to maintain gameplay viability.

        Returns:
            Frightened duration in frames (at 60 FPS).
        """
        if self.level <= 3:
            # First 3 levels: aggressive reduction
            decrement = (
                self.level - 1
            ) * settings.FRIGHTENED_DURATION_DECREMENT_PER_LEVEL
            duration = 10.0 - decrement
        else:
            # Level 4+: gradual reduction
            base_duration = 4.0  # Duration after first 3 levels
            extra_levels = self.level - 3
            decrement = extra_levels * settings.FRIGHTENED_DURATION_DECREMENT_LATE
            duration = base_duration - decrement

        duration = max(duration, settings.MIN_FRIGHTENED_DURATION)
        return int(duration * 60)  # Convert seconds to frames at 60 FPS

    def get_pinky_release_frames(self) -> int:
        """Calculate frame count for Pinky's release from ghost house.

        Pinky is released progressively earlier in higher levels to
        increase early-game pressure.

        Returns:
            Number of frames before Pinky exits the ghost house.
        """
        reduction = (self.level - 1) * settings.GHOST_RELEASE_REDUCTION_PER_LEVEL
        frames = settings.PINKY_BASE_RELEASE_FRAMES - reduction
        return max(frames, settings.MIN_PINKY_RELEASE_FRAMES)

    def get_inky_release_pellets(self) -> int:
        """Calculate pellet count for Inky's release from ghost house.

        Inky is released after fewer pellets are eaten in higher levels.

        Returns:
            Number of pellets that must be eaten before Inky exits.
        """
        reduction = (self.level - 1) * settings.GHOST_RELEASE_PELLET_REDUCTION_PER_LEVEL
        pellets = settings.INKY_BASE_RELEASE_PELLETS - reduction
        return max(pellets, settings.MIN_GHOST_RELEASE_PELLETS)

    def get_clyde_release_pellets(self) -> int:
        """Calculate pellet count for Clyde's release from ghost house.

        Clyde is released after fewer pellets are eaten in higher levels.

        Returns:
            Number of pellets that must be eaten before Clyde exits.
        """
        reduction = (self.level - 1) * settings.GHOST_RELEASE_PELLET_REDUCTION_PER_LEVEL
        pellets = settings.CLYDE_BASE_RELEASE_PELLETS - reduction
        return max(
            pellets, settings.MIN_GHOST_RELEASE_PELLETS * 2
        )  # Clyde needs 2x minimum

    def get_scatter_reduction(self) -> int:
        """Calculate SCATTER mode duration reduction in frames.

        SCATTER mode (when ghosts retreat to corners) becomes shorter
        in higher levels, reducing the player's "safe" periods.

        Returns:
            Number of frames to subtract from SCATTER durations.
        """
        reduction_seconds = (
            min(self.level - 1, settings.MAX_SCATTER_REDUCTION)
            * settings.SCATTER_REDUCTION_PER_LEVEL
        )
        return int(reduction_seconds * 60)  # Convert to frames at 60 FPS

    def get_ghost_mode_cycles(self) -> list[tuple[str, int]]:
        """Get modified ghost mode cycles for current level.

        Applies SCATTER duration reduction while preserving CHASE phases
        and permanent mode markers.

        Returns:
            List of (mode, duration) tuples for the current level.
        """
        scatter_reduction = self.get_scatter_reduction()

        cycles = []
        for mode, duration in settings.GHOST_MODE_CYCLES:
            if mode == "SCATTER" and duration > 0:
                # Reduce SCATTER duration but enforce minimum
                new_duration = max(
                    duration - scatter_reduction, settings.MIN_SCATTER_DURATION
                )
                cycles.append((mode, new_duration))
            else:
                # Keep CHASE and permanent modes unchanged
                cycles.append((mode, duration))

        return cycles
