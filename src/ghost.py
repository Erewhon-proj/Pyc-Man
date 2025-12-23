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
        self._direction: Direction = Direction.RIGHT
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

    def update(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> None:
        """
        Update ghost position.

        Args:
            pacman_x: Pac-Man's X position in pixels
            pacman_y: Pac-Man's Y position in pixels
            pacman_direction: Pac-Man's current direction (dx, dy)
        """
        # State machine: handle behavior based on current state
        if self._house_state == GhostHouseState.IN_HOUSE:
            # Waiting in house, do nothing
            return

        if self._house_state == GhostHouseState.EXITING:
            # Moving towards exit
            self._exit_house()
            return

        target_x, target_y = self.calculate_target(pacman_x, pacman_y, pacman_direction)
        self._target = Position(target_x, target_y)

        self._choose_direction()

        self._move()

    def _is_centered_on_tile(self) -> bool:
        """Check if ghost is centered on current tile."""
        grid_x, grid_y = self._position.to_grid()
        center_x, center_y = self._game_map.grid_to_pixel(grid_x, grid_y)
        tolerance = 2.0
        return (
            abs(self._position.x - center_x) < tolerance
            and abs(self._position.y - center_y) < tolerance
        )

    def _is_opposite_direction(self, direction: Direction) -> bool:
        """Check if given direction is opposite to current direction."""
        dx, dy = direction.value
        opposite_dx = -self._direction.value[0]
        opposite_dy = -self._direction.value[1]
        return dx == opposite_dx and dy == opposite_dy

    def _get_distance_for_direction(self, direction: Direction) -> Optional[float]:
        """Calculate distance to target if moving in given direction."""
        assert self._target is not None
        grid_x, grid_y = self._position.to_grid()
        dx, dy = direction.value
        next_grid_x = grid_x + dx
        next_grid_y = grid_y + dy

        if not self._game_map.is_walkable(next_grid_x, next_grid_y):
            return None

        next_pixel_x, next_pixel_y = self._game_map.grid_to_pixel(
            next_grid_x, next_grid_y
        )
        next_position = Position(next_pixel_x, next_pixel_y)
        return next_position.distance_to(self._target)

    def _choose_direction(self) -> None:
        """Choose the direction that minimizes distance to target."""
        if self._target is None or not self._is_centered_on_tile():
            return

        best_direction = self._direction
        best_distance = float("inf")

        for direction in [
            Direction.UP,
            Direction.DOWN,
            Direction.LEFT,
            Direction.RIGHT,
        ]:
            if self._is_opposite_direction(direction):
                continue

            distance = self._get_distance_for_direction(direction)
            if distance is not None and distance < best_distance:
                best_distance = distance
                best_direction = direction

        self._direction = best_direction

    def _move(self) -> None:
        """Move the ghost in the current direction."""
        dx, dy = self._direction.value
        new_x: float = self._position.x + dx * self._speed
        new_y: float = self._position.y + dy * self._speed

        # Check if new position is walkable
        new_position = Position(new_x, new_y)
        new_grid_x, new_grid_y = new_position.to_grid()

        if self._game_map.is_walkable(new_grid_x, new_grid_y):
            self._position.x = new_x
            self._position.y = new_y
        else:
            # If blocked, snap to center of current tile to allow direction change
            grid_x, grid_y = self._position.to_grid()
            center_x, center_y = self._game_map.grid_to_pixel(grid_x, grid_y)
            self._position.x = center_x
            self._position.y = center_y

    def _exit_house(self) -> None:
        """Move ghost towards the house exit point."""
        tolerance: float = 2.0

        if abs(self._position.x - self._house_exit.x) > tolerance:
            if self._position.x < self._house_exit.x:
                self._position.x += self._speed
            else:
                self._position.x -= self._speed

        elif abs(self._position.y - self._house_exit.y) > tolerance:
            self._position.y -= self._speed
        else:
            self._house_state = GhostHouseState.ACTIVE

    def release_from_house(self) -> None:
        """Signal the ghost to start exiting from the ghost house."""
        if self._house_state == GhostHouseState.IN_HOUSE:
            self._house_state = GhostHouseState.EXITING

    def return_to_house(self) -> None:
        """Return ghost to spawn position in ghost house (when eaten)."""
        self._position.x = self._spawn_position.x
        self._position.y = self._spawn_position.y
        self._house_state = GhostHouseState.IN_HOUSE
        self._direction = Direction.RIGHT


class Blinky(Ghost):
    """
    Blinky (Red Ghost) - The Chaser.
    Directly targets Pac-Man's current position.
    Starts in the ghost house but exits immediately (first to exit).
    """

    def __init__(self, game_map: GameMap, start_x: float, start_y: float) -> None:
        """Initialize Blinky."""
        config = GhostConfig(
            start_position=Position(start_x, start_y),
            color=settings.RED,
            name="Blinky",
            starts_in_house=True,
        )
        super().__init__(game_map, config)

    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """Blinky targets Pac-Man's exact position."""
        return pacman_x, pacman_y


class Pinky(Ghost):
    """
    Pinky (Pink Ghost) - The Ambusher.
    Targets 4 tiles ahead of Pac-Man in his current direction.
    Starts in the ghost house.
    """

    def __init__(self, game_map: GameMap, start_x: float, start_y: float) -> None:
        """Initialize Pinky."""
        config = GhostConfig(
            start_position=Position(start_x, start_y),
            color=settings.PINK,
            name="Pinky",
            starts_in_house=True,
        )
        super().__init__(game_map, config)
        self._tiles_ahead: int = settings.PINKY_TILES_AHEAD

    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """Pinky anticipates Pac-Man's position by targeting 4 tiles ahead."""
        offset_pixels: float = self._tiles_ahead * settings.TILE_SIZE
        target_x: float = pacman_x + pacman_direction[0] * offset_pixels
        target_y: float = pacman_y + pacman_direction[1] * offset_pixels
        return target_x, target_y


class Inky(Ghost):
    """
    Inky (Cyan Ghost) - The Bashful One.
    Uses a more complex targeting pattern involving Pac-Man and Blinky's positions.
    Starts in the ghost house.
    """

    def __init__(
        self,
        game_map: GameMap,
        start_x: float,
        start_y: float,
        blinky: Optional[Blinky] = None,
    ) -> None:
        """Initialize Inky."""
        config = GhostConfig(
            start_position=Position(start_x, start_y),
            color=settings.CYAN,
            name="Inky",
            starts_in_house=True,
        )
        super().__init__(game_map, config)
        self._blinky: Optional[Blinky] = blinky
        self._offset_tiles: int = settings.INKY_OFFSET_TILES

    def set_blinky(self, blinky: Blinky) -> None:
        """Set the reference to Blinky."""
        self._blinky = blinky

    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        1. Takes point 2 tiles ahead of Pac-Man in his direction
        2. Draws vector from Blinky to that point
        3. Doubles that vector - the end is Inky's target
        """
        if self._blinky is None:
            return pacman_x, pacman_y

        # Step 1: Calculate point 2 tiles ahead of Pac-Man in his direction
        offset_pixels: float = self._offset_tiles * settings.TILE_SIZE
        intermediate_x: float = pacman_x + pacman_direction[0] * offset_pixels
        intermediate_y: float = pacman_y + pacman_direction[1] * offset_pixels

        # Step 2: Calculate vector from Blinky to intermediate point
        vector_x: float = intermediate_x - self._blinky.x
        vector_y: float = intermediate_y - self._blinky.y

        # Step 3: Double the vector starting from Blinky
        target_x: float = self._blinky.x + vector_x * 2
        target_y: float = self._blinky.y + vector_y * 2

        return target_x, target_y


class Clyde(Ghost):
    """
    Clyde (Orange Ghost) - The Stupid One.
    Chases Pac-Man when far away, but runs to scatter corner when close.
    Starts in the ghost house.
    """

    def __init__(self, game_map: GameMap, start_x: float, start_y: float) -> None:
        """Initialize Clyde."""
        config = GhostConfig(
            start_position=Position(start_x, start_y),
            color=settings.ORANGE,
            name="Clyde",
            starts_in_house=True,
        )
        super().__init__(game_map, config)
        self._scatter_distance: float = (
            settings.CLYDE_SCATTER_DISTANCE_TILES * settings.TILE_SIZE
        )
        self._scatter_x: float = 1.0 * settings.TILE_SIZE
        self._scatter_y: float = (game_map.height - 2) * settings.TILE_SIZE

    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Clyde targets Pac-Man when far, scatter corner when close.
        Classic "timid" behavior.
        """
        pacman_position = Position(pacman_x, pacman_y)
        distance: float = self._position.distance_to(pacman_position)

        if distance > self._scatter_distance:
            # Far from Pac-Man: chase
            return pacman_x, pacman_y
        # Close to Pac-Man: scatter to corner
        return self._scatter_x, self._scatter_y
