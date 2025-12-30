"""Ghost entities and their behaviors.

This module defines the abstract Ghost base class that implements the ghost behavior.
"""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Tuple

import pygame

from src import settings
from src.direction import Direction
from src.game_map import GameMap
from src.position import Position


class GhostHouseState(Enum):
    """State machine for ghost house behavior."""

    IN_HOUSE = auto()  # Waiting in house
    EXITING = auto()  # Moving to exit
    ACTIVE = auto()  # Free to roam


class GhostState(Enum):
    """General state of the ghost in the game."""

    SCATTER = auto()
    CHASE = auto()
    FRIGHTENED = auto()
    EATEN = auto()


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
        self._original_color: Tuple[int, int, int] = config.color
        self._color: Tuple[int, int, int] = config.color
        self._name: str = config.name
        self._direction: Direction = Direction.RIGHT
        self._speed: int = settings.GHOST_SPEED
        self._target: Optional[Position] = None

        # States
        self._state: GhostState = GhostState.SCATTER
        self._house_state: GhostHouseState = (
            GhostHouseState.IN_HOUSE
            if config.starts_in_house
            else GhostHouseState.ACTIVE
        )
        self._house_exit = Position(
            settings.GHOST_HOUSE_EXIT_X * settings.TILE_SIZE,
            settings.GHOST_HOUSE_EXIT_Y * settings.TILE_SIZE,
        )

        # Animation & Frightened timers
        self._frightened_timer = 0
        self._animation_frame = 0.0
        self._animation_speed = 0.2

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

    @property
    def is_frightened(self) -> bool:
        return self._state == GhostState.FRIGHTENED

    @property
    def is_eaten(self) -> bool:
        return self._state == GhostState.EATEN

    @abstractmethod
    def calculate_target(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> Tuple[float, float]:
        """
        Calculate the target position.
        Each ghost subclass implements its own targeting strategy.
        """
        pass

    def start_frightened(self) -> None:
        """Activate frightened state."""
        if self._state not in [GhostState.EATEN, GhostState.FRIGHTENED]:
            self._state = GhostState.FRIGHTENED
            self._frightened_timer = 600  # Frames (e.g., 10 seconds at 60 FPS)
            self._speed = 1  # Slower speed
            self._reverse_direction()

    def get_eaten(self) -> None:
        """Handle being eaten by Pac-Man."""
        self._state = GhostState.EATEN
        self._speed = 4  # Fast return speed
        # Target becomes the house exit

    def _reverse_direction(self) -> None:
        """Reverses the current direction immediately."""
        if self._direction == Direction.UP:
            self._direction = Direction.DOWN
        elif self._direction == Direction.DOWN:
            self._direction = Direction.UP
        elif self._direction == Direction.LEFT:
            self._direction = Direction.RIGHT
        elif self._direction == Direction.RIGHT:
            self._direction = Direction.LEFT

    def update(
        self, pacman_x: float, pacman_y: float, pacman_direction: Tuple[int, int]
    ) -> None:
        """
        Update ghost position and state.
        """
        # 1. Update Animation
        self._animation_frame = (self._animation_frame + self._animation_speed) % 2

        # 2. Handle Frightened Timer
        if self._state == GhostState.FRIGHTENED:
            self._frightened_timer -= 1
            if self._frightened_timer <= 0:
                self._state = GhostState.SCATTER
                self._speed = settings.GHOST_SPEED

        # 3. Handle Eaten State (Return to House)
        if self._state == GhostState.EATEN:
            # Check if reached the house exit area
            if self._position.distance_to(self._house_exit) < settings.TILE_SIZE:
                self._respawn_in_house()
                return

        # 4. State Machine: handle behavior based on House State
        if self._house_state == GhostHouseState.IN_HOUSE:
            return  # Waiting in house

        if self._house_state == GhostHouseState.EXITING:
            self._exit_house()
            return

        # 5. Determine Target based on State
        if self._state == GhostState.EATEN:
            # Target is the house entrance
            target_x, target_y = self._house_exit.x, self._house_exit.y
        elif self._state == GhostState.FRIGHTENED:
            # Target is irrelevant, random movement handled in _choose_direction
            target_x, target_y = 0, 0
        else:
            # Standard targeting (Chase/Scatter)
            target_x, target_y = self.calculate_target(
                pacman_x, pacman_y, pacman_direction
            )

        self._target = Position(target_x, target_y)

        self._choose_direction()
        self._move()

    def _respawn_in_house(self) -> None:
        """Reset ghost after returning home as eyes."""
        self._state = GhostState.SCATTER  # Or Chase/Scatter logic
        self._speed = settings.GHOST_SPEED
        self._position.x = self._spawn_position.x
        self._position.y = self._spawn_position.y
        self._house_state = GhostHouseState.EXITING  # Immediately exit again
        self._direction = Direction.UP

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
        # If target is None (shouldn't happen in logic path) return inf
        if self._target is None:
            return float("inf")

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
        """Choose the direction."""
        if not self._is_centered_on_tile():
            return

        # Special Case: Frightened Mode = Random Direction at intersections
        if self._state == GhostState.FRIGHTENED:
            valid_directions = []
            for direction in [
                Direction.UP,
                Direction.DOWN,
                Direction.LEFT,
                Direction.RIGHT,
            ]:
                if self._is_opposite_direction(direction):
                    continue

                grid_x, grid_y = self._position.to_grid()
                dx, dy = direction.value
                if self._game_map.is_walkable(grid_x + dx, grid_y + dy):
                    valid_directions.append(direction)

            if valid_directions:
                self._direction = random.choice(valid_directions)
            return

        # Standard AI: Minimize distance to target
        if self._target is None:
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

        # Tunnel Handling (wrap around screen)
        if new_grid_x < 0:
            self._position.x = settings.SCREEN_WIDTH - settings.TILE_SIZE
            return
        elif new_grid_x >= self._game_map.width:
            self._position.x = 0
            return

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
            self._direction = Direction.LEFT  # Standard exit direction

    def release_from_house(self) -> None:
        """Signal the ghost to start exiting from the ghost house."""
        if self._house_state == GhostHouseState.IN_HOUSE:
            self._house_state = GhostHouseState.EXITING

    def return_to_house(self) -> None:
        """Return ghost to spawn position in ghost house (forced reset)."""
        self._position.x = self._spawn_position.x
        self._position.y = self._spawn_position.y
        self._house_state = GhostHouseState.IN_HOUSE
        self._direction = Direction.RIGHT
        self._state = GhostState.SCATTER
        self._speed = settings.GHOST_SPEED

    # --- RENDERING ---

    def draw(self, screen: pygame.Surface):
        """Draw the ghost based on its state."""
        x, y = int(self._position.x), int(self._position.y)

        # 1. Draw Body (if not Eaten/Eyes)
        if self._state != GhostState.EATEN:
            current_color = self._original_color

            # Handle Frightened Color
            if self._state == GhostState.FRIGHTENED:
                # Flash white near end of timer
                if (
                    self._frightened_timer < 120
                    and (self._frightened_timer // 10) % 2 == 0
                ):
                    current_color = settings.FRIGHTENED_WHITE
                else:
                    current_color = settings.FRIGHTENED_BLUE

            self._draw_body(screen, x, y, current_color)

        # 2. Draw Eyes
        self._draw_eyes(screen, x, y)

    def _draw_body(self, screen, x, y, color):
        tile_size = settings.TILE_SIZE
        radius = int(tile_size * 0.4)

        # Head (Top Semicircle)
        pygame.draw.circle(screen, color, (x, y - 2), radius)

        # Body (Rect)
        rect_top = y - 2
        rect_height = radius
        rect = pygame.Rect(x - radius, rect_top, radius * 2, rect_height)
        pygame.draw.rect(screen, color, rect)

        # Feet (Animated)
        feet_y = rect_top + rect_height
        feet_count = 3
        foot_radius = radius // feet_count
        anim_offset = 0 if int(self._animation_frame) == 0 else 2

        for i in range(feet_count):
            foot_x = (x - radius) + (i * 2 * foot_radius) + foot_radius
            pygame.draw.circle(
                screen, color, (int(foot_x), int(feet_y - anim_offset)), foot_radius
            )

    def _draw_eyes(self, screen, x, y):
        # Eyes configuration
        eye_radius = 4
        pupil_radius = 2
        eye_offset_x = 4
        eye_offset_y = -4

        # Look direction offset
        look_x, look_y = 0, 0
        if self._direction == Direction.LEFT:
            look_x = -2
        elif self._direction == Direction.RIGHT:
            look_x = 2
        elif self._direction == Direction.UP:
            look_y = -2
        elif self._direction == Direction.DOWN:
            look_y = 2

        if self._state == GhostState.FRIGHTENED:
            # Frightened eyes (simple dots)
            pygame.draw.circle(screen, (255, 200, 200), (x - 4, y - 2), 2)
            pygame.draw.circle(screen, (255, 200, 200), (x + 4, y - 2), 2)
        else:
            # Normal Eyes (Sclera + Pupil)
            # Left Eye
            pygame.draw.circle(
                screen, settings.WHITE, (x - eye_offset_x, y + eye_offset_y), eye_radius
            )
            pygame.draw.circle(
                screen,
                settings.BLUE,
                (x - eye_offset_x + look_x, y + eye_offset_y + look_y),
                pupil_radius,
            )
            # Right Eye
            pygame.draw.circle(
                screen, settings.WHITE, (x + eye_offset_x, y + eye_offset_y), eye_radius
            )
            pygame.draw.circle(
                screen,
                settings.BLUE,
                (x + eye_offset_x + look_x, y + eye_offset_y + look_y),
                pupil_radius,
            )


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
