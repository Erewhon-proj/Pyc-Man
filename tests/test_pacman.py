from unittest.mock import MagicMock, patch

import pygame
import pytest

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost
from src.pacman import PacMan
from src.settings import SCREEN_WIDTH, TILE_SIZE

# --- Fixtures ---


@pytest.fixture
def mock_game_map():
    """Creates a mock game map for testing."""
    m = MagicMock(spec=GameMap)
    m.width = 20
    m.height = 20
    # Default: everything is walkable
    m.is_walkable.return_value = True
    # Mock grid_to_pixel to return the exact center of the tile
    m.grid_to_pixel.side_effect = lambda gx, gy: (
        gx * TILE_SIZE + TILE_SIZE / 2,
        gy * TILE_SIZE + TILE_SIZE / 2,
    )
    # Default: empty cell
    m.get_cell.return_value = 0
    return m


@pytest.fixture
def pacman(mock_game_map):
    """Creates a PacMan instance centered at tile (1, 1)."""
    start_x = 1 * TILE_SIZE + TILE_SIZE / 2
    start_y = 1 * TILE_SIZE + TILE_SIZE / 2
    return PacMan(mock_game_map, start_x, start_y)


# --- Tests ---


def test_initialization(pacman):
    """Tests the initial state of the PacMan object."""
    assert pacman.lives == 3
    assert pacman.score == 0
    assert pacman.direction == Direction.NONE
    assert pacman.powered_up is False
    assert pacman.speed == 2


def test_handle_input(pacman):
    """Tests if keyboard input correctly sets next_direction."""
    mock_keys = MagicMock()

    # Simulate pressing UP key
    def get_key(k):
        return k == pygame.K_UP

    mock_keys.__getitem__.side_effect = get_key

    with patch("pygame.key.get_pressed", return_value=mock_keys):
        pacman.handle_input()
        assert pacman.next_direction == Direction.UP


def test_change_direction_valid(pacman):
    """Tests changing direction when the path is clear."""
    pacman.next_direction = Direction.RIGHT

    # Update triggers _try_change_direction
    pacman.update([])

    assert pacman.direction == Direction.RIGHT
    assert pacman.next_direction == Direction.NONE


def test_movement_free(pacman):
    """Tests movement in open space."""
    pacman.direction = Direction.RIGHT
    start_x = pacman.x

    pacman.update([])

    # Should move exactly by 'speed' pixels
    assert pacman.x == start_x + pacman.speed


def test_movement_wall_collision(pacman, mock_game_map):
    """Tests collision with a wall stops movement."""
    pacman.direction = Direction.RIGHT

    # Simulate wall at (2, 1)
    def side_effect_is_walkable(gx, gy):
        if gx == 2 and gy == 1:
            return False
        return True

    mock_game_map.is_walkable.side_effect = side_effect_is_walkable

    # Move towards the wall
    for _ in range(20):
        pacman.update([])

    # Should stop at the center of the current tile (1, 1)
    center_current_tile_x = 1 * TILE_SIZE + TILE_SIZE / 2

    # Allow small float tolerance
    assert abs(pacman.x - center_current_tile_x) < 0.1


def test_tunnel_wrapping(pacman):
    """Tests wrapping around the screen edges."""
    pacman.direction = Direction.LEFT
    pacman.position.x = 0

    # Moving left at x=0 should wrap to screen width
    pacman.update([])

    assert pacman.x == SCREEN_WIDTH - TILE_SIZE


def test_eat_pellet(pacman, mock_game_map):
    """Tests score increment and pellet removal."""
    # Simulate pellet at current location
    mock_game_map.get_cell.return_value = 2

    pacman.update([])

    assert pacman.score == 10
    mock_game_map.set_cell.assert_called_with(1, 1, 0)


def test_eat_power_pellet(pacman, mock_game_map):
    """Tests power pellet activation."""
    # Simulate power pellet
    mock_game_map.get_cell.return_value = 3

    pacman.update([])

    assert pacman.score == 50
    assert pacman.powered_up is True
    assert pacman.power_up_timer > 0


def test_ghost_collision_death(pacman):
    """Tests dying when touching a normal ghost."""
    ghost = MagicMock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    # Suppress print output
    with patch("builtins.print"):
        pacman.update([ghost])

    assert pacman.lives == 2
    assert pacman.powered_up is False


def test_ghost_collision_eat_ghost(pacman):
    """Tests eating a ghost when powered up."""
    pacman.powered_up = True

    ghost = MagicMock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    pacman.update([ghost])

    assert pacman.lives == 3  # Should not die
    assert pacman.score == 200  # Eating score
    ghost.return_to_house.assert_called_once()
