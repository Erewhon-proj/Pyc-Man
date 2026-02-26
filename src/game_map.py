"""Module for managing the Pac-Man game map"""

import math

import pygame

from src.settings import BLUE, TILE_SIZE, WHITE


class GameMap:
    """Represents the Pac-Man game map with walls, pellets, and power pellets"""

    tunnel_left_position = (0, 10)
    tunnel_right_position = (18, 10)

    def __init__(self):
        # 1 = wall, 0 = path, 2 = pellet, 3 = power pellet
        self.layout = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 3, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 3, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 0, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 1, 1, 1],
            [1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
            [1, 3, 2, 1, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 1, 2, 3, 1],
            [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
            [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
            [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
            [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        self.initial_pellets = self._count_pellets()

    def _count_pellets(self) -> int:
        """Count total pellets in the map"""
        return sum(cell in [2, 3] for row in self.layout for cell in row)

    def is_wall(self, grid_x: int, grid_y: int) -> bool:
        """Check if position is a wall"""
        if 0 <= grid_y < len(self.layout) and 0 <= grid_x < len(self.layout[0]):
            return self.layout[grid_y][grid_x] == 1
        return True

    def get_cell(self, grid_x: int, grid_y: int) -> int:
        """Get cell value at position"""
        if 0 <= grid_y < len(self.layout) and 0 <= grid_x < len(self.layout[0]):
            return self.layout[grid_y][grid_x]
        return 1

    def set_cell(self, grid_x: int, grid_y: int, value: int):
        """Set cell value at position"""
        if 0 <= grid_y < len(self.layout) and 0 <= grid_x < len(self.layout[0]):
            self.layout[grid_y][grid_x] = value

    def pixel_to_grid(self, pixel_x: float, pixel_y: float) -> tuple[int, int]:
        """Convert pixel coordinates to grid coordinates"""
        grid_x = int(pixel_x / TILE_SIZE)
        grid_y = int(pixel_y / TILE_SIZE)
        return grid_x, grid_y

    def grid_to_pixel(self, grid_x: int, grid_y: int) -> tuple[float, float]:
        """Convert grid coordinates to pixel coordinates (center of tile)"""
        pixel_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        pixel_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        return float(pixel_x), float(pixel_y)

    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        """Check if a grid position is walkable (not a wall)"""
        return not self.is_wall(grid_x, grid_y)

    @property
    def height(self) -> int:
        """Get the height of the map in grid cells"""
        return len(self.layout)

    @property
    def width(self) -> int:
        """Get the width of the map in grid cells"""
        return len(self.layout[0]) if self.layout else 0

    def draw(self, screen: pygame.Surface):
        """Render all map elements."""
        self._draw_walls(screen)
        self._draw_pellets(screen)

    def _is_visual_wall(self, grid_x: int, grid_y: int) -> bool:
        """Check if a cell is a wall, treating out-of-bounds tunnel areas as open paths."""
        tunnel_row = 10
        if grid_y == tunnel_row and (grid_x < 0 or grid_x >= self.width):
            return False
        return self.is_wall(grid_x, grid_y)

    def _draw_clipped_corner(
        self,
        screen: pygame.Surface,
        clip_rect: tuple,
        center: tuple,
        radius: int,
        thickness: int,
    ):
        """Draw a perfect quadrant by using a clipping mask to bypass Pygame rendering bugs."""
        screen.set_clip(pygame.Rect(*clip_rect))
        pygame.draw.circle(screen, BLUE, center, radius, thickness)
        screen.set_clip(None)

    def _draw_walls(self, screen: pygame.Surface):
        """Calculate boundaries and render the labyrinth walls with rounded corners."""
        thickness = 2
        r = 8  # Corner radius

        for y in range(self.height + 1):
            for x in range(self.width + 1):
                px, py = x * TILE_SIZE, y * TILE_SIZE

                # Boundary detection
                bE = x < self.width and self._is_visual_wall(
                    x, y - 1
                ) != self._is_visual_wall(x, y)
                bS = y < self.height and self._is_visual_wall(
                    x - 1, y
                ) != self._is_visual_wall(x, y)
                bW = x > 0 and self._is_visual_wall(
                    x - 1, y - 1
                ) != self._is_visual_wall(x - 1, y)
                bN = y > 0 and self._is_visual_wall(
                    x - 1, y - 1
                ) != self._is_visual_wall(x, y - 1)

                # Draw straight segments
                if bE:
                    pygame.draw.line(
                        screen, BLUE, (px + r, py), (px + TILE_SIZE - r, py), thickness
                    )
                if bS:
                    pygame.draw.line(
                        screen, BLUE, (px, py + r), (px, py + TILE_SIZE - r), thickness
                    )

                # Handle intersections and corners
                b_count = bN + bS + bE + bW

                if b_count == 2:
                    if bN and bS:
                        pygame.draw.line(
                            screen, BLUE, (px, py - r), (px, py + r), thickness
                        )
                    elif bE and bW:
                        pygame.draw.line(
                            screen, BLUE, (px - r, py), (px + r, py), thickness
                        )
                    elif bN and bE:
                        self._draw_clipped_corner(
                            screen, (px, py - r, r, r), (px + r, py - r), r, thickness
                        )
                    elif bN and bW:
                        self._draw_clipped_corner(
                            screen,
                            (px - r, py - r, r, r),
                            (px - r, py - r),
                            r,
                            thickness,
                        )
                    elif bS and bE:
                        self._draw_clipped_corner(
                            screen, (px, py, r, r), (px + r, py + r), r, thickness
                        )
                    elif bS and bW:
                        self._draw_clipped_corner(
                            screen, (px - r, py, r, r), (px - r, py + r), r, thickness
                        )
                elif b_count != 0:
                    # Anchor lines to the grid edge for tunnel exits and dead ends
                    if bN:
                        pygame.draw.line(
                            screen, BLUE, (px, py - r), (px, py), thickness
                        )
                    if bS:
                        pygame.draw.line(
                            screen, BLUE, (px, py + r), (px, py), thickness
                        )
                    if bE:
                        pygame.draw.line(
                            screen, BLUE, (px + r, py), (px, py), thickness
                        )
                    if bW:
                        pygame.draw.line(
                            screen, BLUE, (px - r, py), (px, py), thickness
                        )

    def _draw_pellets(self, screen: pygame.Surface):
        """Render normal and power pellets across the map."""
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                # Skip empty paths or walls
                if cell not in (2, 3):
                    continue

                center_x = (x * TILE_SIZE) + (TILE_SIZE // 2)
                center_y = (y * TILE_SIZE) + (TILE_SIZE // 2)
                center = (center_x, center_y)

                if cell == 2:
                    # Regular pellet
                    pygame.draw.circle(screen, (255, 255, 220), center, 3)

                elif cell == 3:
                    # Power pellet with pulsing effect
                    pulse = abs(math.sin(pygame.time.get_ticks() / 200.0)) * 3
                    radius = int(7 + pulse)

                    pygame.draw.circle(screen, (255, 255, 150), center, radius)  # Glow
                    pygame.draw.circle(screen, (255, 255, 255), center, 5)  # Core
