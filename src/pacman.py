"""Pac-Man character module.

This module defines the PacMan class, handling movement, input, and interaction.
"""

import math
from typing import List

import pygame

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost
from src.position import Position
from src.settings import FPS, SCREEN_WIDTH, TILE_SIZE, YELLOW


class PacMan:
    """Class representing the player (Pac-Man)."""

    # Game entities inherently need many attributes for state management
    # pylint: disable=too-many-instance-attributes

    def __init__(self, game_map: GameMap, start_x: float, start_y: float):
        """Initialize Pac-Man."""
        self.game_map = game_map
        self.position = Position(start_x, start_y)
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE  # Input buffering

        self.speed = 2  # Pixels per frame
        self.score = 0
        self.lives = 3

        # Animation state
        self.mouth_open_angle = 0
        self.animation_speed = 0.2
        self.animation_counter = 0.0  # Fixed: float initialization
        self.mouth_closing = True

        # Power up state
        self.powered_up = False
        self.power_up_timer = 0
        self.power_up_duration = 10 * FPS

    @property
    def x(self) -> float:
        """Get X position."""
        return self.position.x

    @property
    def y(self) -> float:
        """Get Y position."""
        return self.position.y

    def handle_input(self) -> None:
        """Handles keyboard input to set the next direction."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = Direction.UP
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = Direction.DOWN
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = Direction.LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = Direction.RIGHT

    def update(self, ghosts: List[Ghost]) -> None:
        """Updates Pac-Man's state (movement, animation, collisions)."""
        self._try_change_direction()
        self._move()
        self._animate()
        self._check_pellet_collision()
        self._update_power_up()
        self._check_ghost_collisions(ghosts)

    def _try_change_direction(self) -> None:
        """Attempts to change direction if not blocked by walls."""
        if self.next_direction == Direction.NONE:
            return

        # If stopped or reversing, change immediately
        if self.direction == Direction.NONE or self._is_opposite_direction(
            self.next_direction
        ):
            self.direction = self.next_direction
            self.next_direction = Direction.NONE
            return

        # Otherwise, must be centered on tile to turn
        if self._is_centered_on_tile():
            grid_x, grid_y = self.position.to_grid()
            dx, dy = self.next_direction.value

            # Check if the target tile is free
            if self.game_map.is_walkable(grid_x + dx, grid_y + dy):
                # Center perfectly before turning to avoid misalignment
                pixel_x, pixel_y = self.game_map.grid_to_pixel(grid_x, grid_y)
                self.position.x = pixel_x
                self.position.y = pixel_y

                self.direction = self.next_direction
                self.next_direction = Direction.NONE

    def _move(self) -> None:
        """Performs physical movement and handles wall collisions."""
        if self.direction == Direction.NONE:
            return

        dx, dy = self.direction.value
        new_x = self.position.x + dx * self.speed
        new_y = self.position.y + dy * self.speed

        check_pos = Position(new_x, new_y)
        grid_x, grid_y = check_pos.to_grid()

        # Tunnel handling
        if grid_x < 0:
            self.position.x = SCREEN_WIDTH - TILE_SIZE
            return
        if grid_x >= self.game_map.width:
            self.position.x = 0
            return

        # Wall collision check
        next_grid_x = grid_x + dx
        next_grid_y = grid_y + dy

        can_move = True
        center_x, center_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        dist_from_center = 0

        if self.direction in [Direction.LEFT, Direction.RIGHT]:
            dist_from_center = abs(new_x - center_x)
        else:
            dist_from_center = abs(new_y - center_y)

        # If crossing tile center into a wall, stop at center
        if dist_from_center >= 0 and not self.game_map.is_walkable(
            next_grid_x, next_grid_y
        ):
            blocked = False
            if self.direction == Direction.RIGHT and new_x > center_x:
                blocked = True
            if self.direction == Direction.LEFT and new_x < center_x:
                blocked = True
            if self.direction == Direction.DOWN and new_y > center_y:
                blocked = True
            if self.direction == Direction.UP and new_y < center_y:
                blocked = True

            if blocked:
                self.position.x = center_x
                self.position.y = center_y
                can_move = False

        if can_move:
            self.position.x = new_x
            self.position.y = new_y

    def _check_pellet_collision(self) -> None:
        """Eats pellet or power pellet if at tile center."""
        grid_x, grid_y = self.position.to_grid()
        cell_value = self.game_map.get_cell(grid_x, grid_y)

        # Check proximity to center
        pixel_x, pixel_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        if abs(self.position.x - pixel_x) < 5 and abs(self.position.y - pixel_y) < 5:
            if cell_value == 2:  # Normal Pellet
                self.game_map.set_cell(grid_x, grid_y, 0)
                self.score += 10
            elif cell_value == 3:  # Power Pellet
                self.game_map.set_cell(grid_x, grid_y, 0)
                self.score += 50
                self._activate_power_up()

    def _activate_power_up(self) -> None:
        """Activates power-up mode."""
        self.powered_up = True
        self.power_up_timer = self.power_up_duration

    def _update_power_up(self) -> None:
        """Updates the power-up timer."""
        if self.powered_up:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.powered_up = False

    def _check_ghost_collisions(self, ghosts: List[Ghost]) -> None:
        """Handles collisions with ghosts."""
        hitbox_radius = TILE_SIZE / 2 * 0.8

        for ghost in ghosts:
            dist = math.sqrt((self.x - ghost.x) ** 2 + (self.y - ghost.y) ** 2)

            if dist < hitbox_radius * 2:
                if self.powered_up and not ghost.in_ghost_house:
                    self.score += 200
                    ghost.get_eaten()
                elif not self.powered_up and not ghost.in_ghost_house:
                    self._die()

    def _die(self) -> None:
        """Handles Pac-Man death."""
        print("Pac-Man Died!")
        self.lives -= 1

    def _animate(self) -> None:
        """Handles mouth animation."""
        if self.direction == Direction.NONE:
            return

        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0.0
            if self.mouth_closing:
                self.mouth_open_angle += 5
                if self.mouth_open_angle >= 45:
                    self.mouth_closing = False
            else:
                self.mouth_open_angle -= 5
                if self.mouth_open_angle <= 0:
                    self.mouth_closing = True

    def draw(self, screen: pygame.Surface) -> None:
        """Draws Pac-Man on the screen."""
        color = YELLOW

        center = (int(self.x), int(self.y))
        radius = TILE_SIZE // 2 - 2

        if self.mouth_open_angle == 0:
            pygame.draw.circle(screen, color, center, radius)
        else:
            # Draw Pac-Man with open mouth using a polygon
            rotation = 0
            if self.direction == Direction.UP:
                rotation = 90
            elif self.direction == Direction.LEFT:
                rotation = 180
            elif self.direction == Direction.DOWN:
                rotation = 270

            start_angle = math.radians(rotation + self.mouth_open_angle)
            end_angle = math.radians(rotation + 360 - self.mouth_open_angle)

            points = [center]
            steps = 20
            step_angle = (end_angle - start_angle) / steps

            for i in range(steps + 1):
                angle = start_angle + i * step_angle
                px = center[0] + radius * math.cos(angle)
                py = center[1] - radius * math.sin(angle)
                # Fixed: Cast to int to match points type List[Tuple[int, int]]
                points.append((int(px), int(py)))

            pygame.draw.polygon(screen, color, points)

    def _is_centered_on_tile(self) -> bool:
        grid_x, grid_y = self.position.to_grid()
        center_x, center_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        return (
            abs(self.position.x - center_x) < 2 and abs(self.position.y - center_y) < 2
        )

    def _is_opposite_direction(self, direction: Direction) -> bool:
        if self.direction == Direction.NONE:
            return False
        return (
            self.direction.value[0] * -1 == direction.value[0]
            and self.direction.value[1] * -1 == direction.value[1]
        )
