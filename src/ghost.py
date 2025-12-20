"""Ghost entities and their behaviors.

This module defines the abstract Ghost base class that implements the ghost behavior.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from src import settings
from src.direction import Direction
from src.game_map import GameMap
from src.position import Position


class GhostHouseState(Enum):
    """State machine for ghost house behavior."""

    IN_HOUSE = auto()  # Waiting in house
    EXITING = auto()  # Moving to exit
    ACTIVE = auto()  # Free to roam


@dataclass
class GhostConfig:
    """Configuration for initializing a ghost."""

    start_position: Position
    color: Tuple[int, int, int]
    name: str
    starts_in_house: bool = False


class Ghost(ABC):
    """Abstract base class for all ghost entities.

    This class defines the common behavior and state for all ghosts in the game.
    Each ghost subclass must implement its own targeting strategy.

    """

    def __init__(self, game_map: GameMap, config: GhostConfig) -> None:
        """
        Initialize a ghost.

        Args:
            game_map: The game map for navigation (dependency injection)
            config: Ghost configuration containing position, color, name, etc.
        """
        self._game_map: GameMap = game_map
        self._position = Position(config.start_position.x, config.start_position.y)
        self._spawn_position = Position(
            config.start_position.x, config.start_position.y
        )
        self._color: Tuple[int, int, int] = config.color
        self._name: str = config.name
        self._direction: Tuple[int, int] = Direction.RIGHT.value
        self._speed: int = settings.GHOST_SPEED
        self._target: Optional[Position] = None

        # Ghost house state machine
        self._house_state: GhostHouseState = (
            GhostHouseState.IN_HOUSE
            if config.starts_in_house
            else GhostHouseState.ACTIVE
        )
        self._house_exit = Position(
            settings.GHOST_HOUSE_EXIT_X * settings.TILE_SIZE,
            settings.GHOST_HOUSE_EXIT_Y * settings.TILE_SIZE,
        )

    @property
    def x(self) -> float:
        """Get the ghost's X position."""
        return self._position.x

    @property
    def y(self) -> float:
        """Get the ghost's Y position."""
        return self._position.y

    @property
    def color(self) -> Tuple[int, int, int]:
        """Get the ghost's color."""
        return self._color

    @property
    def name(self) -> str:
        """Get the ghost's name."""
        return self._name

    @property
    def in_ghost_house(self) -> bool:
        """Check if ghost is in the ghost house."""
        return self._house_state == GhostHouseState.IN_HOUSE

    @abstractmethod
    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Calculate the target position.
        Each ghost subclass implements its own targeting strategy.

        Args:
            pacman_x: Pac-Man's X position in pixels
            pacman_y: Pac-Man's Y position in pixels
            pacman_direction: Pac-Man's current direction (dx, dy)

        Returns:
            Tuple of (target_x, target_y) in pixels
        """
        pass
