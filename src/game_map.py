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
        """Render the map"""
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                px, py = x * TILE_SIZE, y * TILE_SIZE

                if cell == 1:
                    # Wall
                    pygame.draw.rect(screen, BLUE, (px, py, TILE_SIZE, TILE_SIZE))

                elif cell == 2:
                    # Pellet with glow
                    center = (px + TILE_SIZE // 2, py + TILE_SIZE // 2)
                    pygame.draw.circle(screen, (255, 255, 200, 50), center, 5)
                    pygame.draw.circle(screen, WHITE, center, 3)

                elif cell == 3:
                    # Power pellet with animation
                    center = (px + TILE_SIZE // 2, py + TILE_SIZE // 2)
                    pulse = abs(math.sin(pygame.time.get_ticks() / 200)) * 3
                    pygame.draw.circle(screen, (255, 255, 150), center, int(8 + pulse))
                    pygame.draw.circle(screen, WHITE, center, 6)
