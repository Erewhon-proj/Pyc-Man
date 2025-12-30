"""
Test suite for PacMan class.
Uses pytest-mock for patching.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pygame
import pytest
from pytest_mock import MockerFixture

from src.direction import Direction
from src.ghost import Ghost
from src.pacman import PacMan
from src.settings import SCREEN_WIDTH, TILE_SIZE


@pytest.fixture
def pacman(mock_game_map):
    """Creates a PacMan instance centered at tile (1, 1)."""
    start_x = 1 * TILE_SIZE + TILE_SIZE / 2
    start_y = 1 * TILE_SIZE + TILE_SIZE / 2
    return PacMan(mock_game_map, start_x, start_y)


def test_initialization(pacman):
    """Tests the initial state of the PacMan object."""
    assert pacman.lives == 3
    assert pacman.score == 0
    assert pacman.direction == Direction.NONE
    assert pacman.powered_up is False
    assert pacman.speed == 2


def test_handle_input(pacman, mocker: MockerFixture):
    """Tests if keyboard input correctly sets next_direction."""
    mock_keys = mocker.Mock()

    # Simulate pressing UP key
    def get_key(k):
        return k == pygame.K_UP

    mock_keys.__getitem__.side_effect = get_key

    mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

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


def test_ghost_collision_death(pacman, mocker: MockerFixture):
    """Tests dying when touching a normal ghost."""
    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    # Suppress print output
    mocker.patch("builtins.print")

    pacman.update([ghost])

    assert pacman.lives == 2
    assert pacman.powered_up is False


def test_ghost_collision_eat_ghost(pacman, mocker: MockerFixture):
    """Tests eating a ghost when powered up."""
    pacman.powered_up = True
    # Ensure timer is > 0
    pacman.power_up_timer = 600

    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    pacman.update([ghost])

    # Should not die
    assert pacman.lives == 3
    # Eating score
    assert pacman.score == 200
    ghost.get_eaten.assert_called_once()
