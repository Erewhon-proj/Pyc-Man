"""Pac-Man character module.

This module defines the PacMan class, handling movement, input, and interaction.
"""

import math
from typing import List

import pygame

from src import settings
from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost
from src.position import Position


class PacMan:
    """Class representing the player (Pac-Man)."""

    # Game entities inherently need many attributes for state management
    # pylint: disable=too-many-instance-attributes

    def __init__(self, game_map: GameMap, start_x: float, start_y: float):
        """Initialize Pac-Man."""
        self.game_map = game_map
        self.spawn_position = Position(start_x, start_y)
        self.position = Position(start_x, start_y)
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE  # Input buffering

        self.base_speed = settings.PACMAN_SPEED
        self.speed = settings.PACMAN_SPEED  # Current effective speed
        self.eating_timer = 0  # Frames of slowdown when eating
        self.score = 0
        self.lives = settings.STARTING_LIVES
        self.extra_lives_earned = 0  # Track how many extra lives have been earned
        self.pellets_eaten = 0  # Counter for ghost release logic

        # Animation state
        self.mouth_open_angle = 0
        self.animation_speed = 0.2
        self.animation_counter = 0.0
        self.mouth_closing = True

        # Power up state
        self.powered_up = False
        self.power_up_timer = 0
        self.power_up_duration = 10 * settings.FPS

        # Ghost scoring multiplier (resets when power pellet ends or new one starts)
        self.ghost_multiplier = 1

        # Respawn state
        self.death_timer = 0  # Invulnerability timer after respawn
        self.is_dead = False  # Flag to prevent multiple deaths

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
        # Update death timer (invincibility after respawn)
        if self.death_timer > 0:
            self.death_timer -= 1

        self._try_change_direction()
        self._move()
        self._animate()
        self._check_pellet_collision(ghosts)
        self._update_power_up()
        self._update_eating_timer()
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

        # Pac-Man can pre-turn before reaching exact center (cornering)
        if self._can_turn():
            grid_x, grid_y = self.position.to_grid()
            dx, dy = self.next_direction.value

            # Check if the target tile is free
            if self.game_map.is_walkable(grid_x + dx, grid_y + dy):
                # Center only the axis we're LEAVING (old direction)
                pixel_x, pixel_y = self.game_map.grid_to_pixel(grid_x, grid_y)

                if self.direction in [Direction.LEFT, Direction.RIGHT]:
                    # Was moving horizontally → snap X only
                    self.position.x = pixel_x
                elif self.direction in [Direction.UP, Direction.DOWN]:
                    # Was moving vertically → snap Y only
                    self.position.y = pixel_y

                self.direction = self.next_direction
                self.next_direction = Direction.NONE

    def _should_block_movement(
        self, new_x: float, new_y: float, center_x: float, center_y: float
    ) -> bool:
        """Check if movement should be blocked when approaching a wall."""
        if self.direction == Direction.RIGHT and new_x > center_x:
            return True
        if self.direction == Direction.LEFT and new_x < center_x:
            return True
        if self.direction == Direction.DOWN and new_y > center_y:
            return True
        if self.direction == Direction.UP and new_y < center_y:
            return True
        return False

    def _move(self) -> None:
        """Performs physical movement and handles wall collisions."""
        if self.direction == Direction.NONE:
            return

        dx, dy = self.direction.value
        effective_speed = self.speed
        new_x = self.position.x + dx * effective_speed
        new_y = self.position.y + dy * effective_speed

        # Handle tunnel wrapping BEFORE checking walkability
        map_width_pixels = self.game_map.width * settings.TILE_SIZE
        if new_x < 0:
            new_x += map_width_pixels
        elif new_x >= map_width_pixels:
            new_x -= map_width_pixels

        # Get current grid position
        grid_x, grid_y = self.game_map.pixel_to_grid(self.position.x, self.position.y)
        center_x, center_y = self.game_map.grid_to_pixel(grid_x, grid_y)

        # Check the next tile in the direction of movement
        next_grid_x = grid_x + dx
        next_grid_y = grid_y + dy

        # Wrap next_grid_x for tunnel
        if next_grid_x < 0:
            next_grid_x = self.game_map.width - 1
        elif next_grid_x >= self.game_map.width:
            next_grid_x = 0

        # Check if moving past center toward a wall
        if not self.game_map.is_walkable(
            next_grid_x, next_grid_y
        ) and self._should_block_movement(new_x, new_y, center_x, center_y):
            self.position.x = center_x
            self.position.y = center_y
        else:
            self.position.x = new_x
            self.position.y = new_y

    def _check_pellet_collision(self, ghosts: List[Ghost]) -> None:
        """Eats pellet or power pellet if at tile center."""
        grid_x, grid_y = self.position.to_grid()
        cell_value = self.game_map.get_cell(grid_x, grid_y)

        # Check proximity to center
        pixel_x, pixel_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        if abs(self.position.x - pixel_x) < 5 and abs(self.position.y - pixel_y) < 5:
            if cell_value == 2:  # Normal Pellet
                self.game_map.set_cell(grid_x, grid_y, 0)
                self.score += 10
                self.pellets_eaten += 1
                self._check_extra_life()
                # Trigger eating slowdown (71% of normal speed)
                self.eating_timer = 1
                self._update_speed()
            elif cell_value == 3:  # Power Pellet
                self.game_map.set_cell(grid_x, grid_y, 0)
                self.score += 50
                self.pellets_eaten += 1  # Increment pellet counter
                self._check_extra_life()
                self._activate_power_up()
                for ghost in ghosts:
                    ghost.start_frightened()
                # Trigger eating slowdown
                self.eating_timer = 1
                self._update_speed()

    def _activate_power_up(self) -> None:
        """Activates power-up mode and resets ghost multiplier."""
        self.powered_up = True
        self.power_up_timer = self.power_up_duration
        self.ghost_multiplier = 1  # Reset multiplier for new power pellet
        self._update_speed()

    def _update_power_up(self) -> None:
        """Updates the power-up timer."""
        if self.powered_up:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.powered_up = False
                self.ghost_multiplier = 1  # Reset multiplier when power-up ends
                self._update_speed()

    def _update_eating_timer(self) -> None:
        """Updates the eating slowdown timer."""
        if self.eating_timer > 0:
            self.eating_timer -= 1
            if self.eating_timer == 0:
                self._update_speed()

    def _update_speed(self) -> None:
        """Updates Pac-Man's speed based on current state."""
        if self.eating_timer > 0:
            # Eating: slow down to 71%
            self.speed = self.base_speed * settings.PACMAN_EATING_SPEED_MULTIPLIER
        elif self.powered_up:
            # Powered-up: go faster (110%)
            self.speed = settings.PACMAN_POWERED_SPEED
        else:
            # Normal speed
            self.speed = self.base_speed

    def _check_ghost_collisions(self, ghosts: List[Ghost]) -> None:
        """Handles collisions with ghosts.

        In the original Pac-Man, collision happens when entities are very close
        (approximately within 1-2 pixels of each other's centers).
        """
        # Don't check collisions if currently invincible (just respawned)
        if self.death_timer > 0:
            return

        # Collision threshold: ~8 pixels (more precise than before)
        collision_threshold = (
            settings.TILE_SIZE * 0.27
        )  # Approximately 8 pixels for 30px tiles

        for ghost in ghosts:
            dist = math.sqrt((self.x - ghost.x) ** 2 + (self.y - ghost.y) ** 2)

            if dist < collision_threshold:
                if ghost.is_frightened:
                    points = settings.GHOST_BASE_SCORE * self.ghost_multiplier
                    self.score += points
                    self.ghost_multiplier *= 2  # Double multiplier for next ghost
                    self._check_extra_life()
                    ghost.get_eaten()
                elif not ghost.is_eaten and not ghost.in_ghost_house:
                    self._die()

    def _die(self) -> None:
        """Handles Pac-Man death and respawn."""
        print("Pac-Man Died!")
        self.lives -= 1

        # Respawn at spawn position
        self._respawn()

    def _respawn(self) -> None:
        """Respawn Pac-Man at spawn position with temporary invincibility."""
        self.position.x = self.spawn_position.x
        self.position.y = self.spawn_position.y
        self.direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.death_timer = settings.RESPAWN_INVINCIBILITY_FRAMES

        # Reset power-up state
        self.powered_up = False
        self.power_up_timer = 0
        self.ghost_multiplier = 1  # Reset ghost multiplier on death
        self._update_speed()

    def _check_extra_life(self) -> None:
        """Check if player has earned an extra life based on score."""
        lives_earned = self.score // settings.EXTRA_LIFE_SCORE
        if lives_earned > self.extra_lives_earned:
            # Award extra lives (up to settings.MAX_LIVES)
            new_lives = min(
                lives_earned - self.extra_lives_earned, settings.MAX_LIVES - self.lives
            )
            if new_lives > 0:
                self.lives += new_lives
                self.extra_lives_earned += new_lives
                print(f"Extra life earned! Lives: {self.lives}")

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
        color = settings.YELLOW

        center = (int(self.x), int(self.y))
        radius = settings.TILE_SIZE // 2 - 2

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

    def draw_lives(self, screen: pygame.Surface) -> None:
        """Draw remaining lives as small Pac-Man icons in bottom-left corner."""
        for i in range(self.lives):
            x = settings.LIVES_DISPLAY_X + (i * settings.LIVES_SPACING)
            y = settings.LIVES_DISPLAY_Y
            radius = settings.LIVES_ICON_SIZE // 2

            # Draw a simple Pac-Man icon (yellow circle with mouth)
            center = (x + radius, y)
            pygame.draw.circle(screen, settings.YELLOW, center, radius)

            # Draw mouth (black triangle)
            mouth_points = [
                center,
                (x + radius + radius, y - radius // 2),
                (x + radius + radius, y + radius // 2),
            ]
            pygame.draw.polygon(screen, (0, 0, 0), mouth_points)

    def draw_score(self, screen: pygame.Surface) -> None:
        """Draw the score in the top-left corner."""
        font = pygame.font.Font(None, settings.SCORE_FONT_SIZE)
        score_text = f"SCORE: {self.score}"
        text_surface = font.render(score_text, True, settings.WHITE)
        screen.blit(text_surface, (settings.SCORE_DISPLAY_X, settings.SCORE_DISPLAY_Y))

    def _is_centered_on_tile(self) -> bool:
        grid_x, grid_y = self.position.to_grid()
        center_x, center_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        return (
            abs(self.position.x - center_x) < 2 and abs(self.position.y - center_y) < 2
        )

    def _can_turn(self) -> bool:
        """Check if Pac-Man can turn"""
        grid_x, grid_y = self.position.to_grid()
        center_x, center_y = self.game_map.grid_to_pixel(grid_x, grid_y)
        turn_tolerance = 8  # Pac-Man can pre-turn ~8 pixels before center
        return (
            abs(self.position.x - center_x) < turn_tolerance
            and abs(self.position.y - center_y) < turn_tolerance
        )

    def _is_opposite_direction(self, direction: Direction) -> bool:
        if self.direction == Direction.NONE:
            return False
        return (
            self.direction.value[0] * -1 == direction.value[0]
            and self.direction.value[1] * -1 == direction.value[1]
        )
