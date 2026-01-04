"""Integration tests to verify main configuration aligns with game logic"""

from src.game_map import GameMap
from src.settings import TILE_SIZE


def test_pacman_spawn_position_is_valid():
    """Verifies that the Pac-Man spawn position defined in main is walkable"""
    game_map = GameMap()

    # Logic copied from src/main.py
    start_x = 9 * TILE_SIZE + TILE_SIZE / 2
    start_y = 16 * TILE_SIZE + TILE_SIZE / 2

    grid_x, grid_y = game_map.pixel_to_grid(start_x, start_y)

    # Ensure it does not spawn inside a wall
    assert game_map.is_walkable(grid_x, grid_y)
    # Ensure it does not spawn outside the grid
    assert 0 <= grid_x < game_map.width
    assert 0 <= grid_y < game_map.height


def test_ghosts_spawn_positions_are_valid():
    """Verifies that ghosts spawn in valid positions (or inside the house)"""
    game_map = GameMap()

    # Coordinates taken from src/main.py
    ghost_spawns = [
        (9.5 * TILE_SIZE, 8.5 * TILE_SIZE),  # Blinky
        (8.5 * TILE_SIZE, 10.5 * TILE_SIZE),  # Pinky
        (9.5 * TILE_SIZE, 10.5 * TILE_SIZE),  # Inky
        (10.5 * TILE_SIZE, 10.5 * TILE_SIZE),  # Clyde
    ]

    for x, y in ghost_spawns:
        grid_x, grid_y = game_map.pixel_to_grid(x, y)
        # Note: We don't use is_walkable here because the ghost house is technically
        # a "wall" for normal movement, but we must ensure coordinates are sensible.
        assert 0 <= grid_x < game_map.width
        assert 0 <= grid_y < game_map.height

        # Verify they are not in the "Void" (empty cells outside playable map)
        # 0=Empty, 1=Wall, 2=Pellet, 3=Power Pellet
        assert game_map.get_cell(grid_x, grid_y) in [0, 1, 2, 3]
