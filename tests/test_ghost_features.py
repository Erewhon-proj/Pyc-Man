from unittest.mock import ANY, MagicMock, patch

import pygame
import pytest

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostConfig, GhostHouseState, GhostState
from src.position import Position
from src.settings import GHOST_SPEED, TILE_SIZE

# --- Fixtures ---


@pytest.fixture
def mock_game_map():
    """Creates a mock game map."""
    m = MagicMock(spec=GameMap)
    m.width = 20
    m.height = 20
    m.is_walkable.return_value = True
    m.grid_to_pixel.side_effect = lambda gx, gy: (
        gx * TILE_SIZE + TILE_SIZE / 2,
        gy * TILE_SIZE + TILE_SIZE / 2,
    )
    return m


@pytest.fixture
def ghost_config():
    """Basic ghost configuration."""
    return GhostConfig(
        start_position=Position(100, 100),
        color=(255, 0, 0),
        name="TestGhost",
        starts_in_house=False,
    )


@pytest.fixture
def concrete_ghost(mock_game_map, ghost_config):
    """Concrete Ghost instance (since Ghost is abstract)."""

    class TestGhost(Ghost):
        def calculate_target(self, px, py, pdir):
            return px, py

    return TestGhost(mock_game_map, ghost_config)


# --- Tests ---


def test_start_frightened(concrete_ghost):
    """Tests transition to FRIGHTENED state."""
    # Ensure ghost is in a state that allows becoming frightened
    concrete_ghost._state = GhostState.SCATTER
    concrete_ghost._direction = Direction.LEFT

    concrete_ghost.start_frightened()

    assert concrete_ghost._state == GhostState.FRIGHTENED
    assert concrete_ghost._frightened_timer == 600
    assert concrete_ghost._speed == 1  # Reduced speed
    # Verify direction reversal
    assert concrete_ghost._direction == Direction.RIGHT


def test_frightened_timer_update(concrete_ghost):
    """Tests that frightened timer decrements and resets state."""
    concrete_ghost.start_frightened()
    concrete_ghost._frightened_timer = 1  # Nearly finished

    # Update call (pacman position irrelevant for this test)
    concrete_ghost.update(0, 0, (0, 0))

    assert concrete_ghost._state == GhostState.SCATTER
    assert concrete_ghost._speed == GHOST_SPEED


def test_get_eaten(concrete_ghost):
    """Tests transition to EATEN state."""
    concrete_ghost.get_eaten()

    assert concrete_ghost._state == GhostState.EATEN
    assert concrete_ghost._speed == 4  # Fast return speed


def test_eaten_return_to_house(concrete_ghost, mock_game_map):
    """Tests respawning when EATEN ghost reaches house."""
    concrete_ghost.get_eaten()

    # Place ghost exactly at house exit
    exit_pos = concrete_ghost._house_exit
    concrete_ghost._position.x = exit_pos.x
    concrete_ghost._position.y = exit_pos.y

    # Mocking distance check effectively
    # logic: if distance < TILE_SIZE -> respawn

    concrete_ghost.update(0, 0, (0, 0))

    # Should have reset
    assert concrete_ghost._state != GhostState.EATEN
    assert concrete_ghost._house_state == GhostHouseState.EXITING
    assert concrete_ghost._speed == GHOST_SPEED


def test_animation_update(concrete_ghost):
    """Tests that animation frame advances."""
    initial_frame = concrete_ghost._animation_frame
    concrete_ghost.update(0, 0, (0, 0))
    assert concrete_ghost._animation_frame != initial_frame


def test_draw_normal(concrete_ghost):
    """Tests drawing calls in normal state."""
    screen_mock = MagicMock()

    with patch("pygame.draw.circle") as mock_circle, patch(
        "pygame.draw.rect"
    ) as mock_rect:
        concrete_ghost.draw(screen_mock)

        # Should draw body (circle + rect) and feet (circles) + eyes
        assert mock_circle.call_count >= 1  # Head + feet + eyes
        assert mock_rect.call_count >= 1  # Body

        # Check color used (Red)
        args, _ = mock_circle.call_args_list[0]
        assert args[1] == (255, 0, 0)  # Color arg


def test_draw_frightened(concrete_ghost):
    """Tests drawing calls in frightened state (Blue)."""
    concrete_ghost.start_frightened()
    screen_mock = MagicMock()

    with patch("pygame.draw.circle") as mock_circle, patch(
        "pygame.draw.rect"
    ) as mock_rect:
        concrete_ghost.draw(screen_mock)

        # Check color used (Frightened Blue from settings, usually dark blue)
        # Using ANY because exact color tuple depends on settings import
        args, _ = mock_circle.call_args_list[0]
        # Verify it's NOT red
        assert args[1] != (255, 0, 0)


def test_draw_eaten(concrete_ghost):
    """Tests drawing calls in eaten state (Only eyes)."""
    concrete_ghost.get_eaten()
    screen_mock = MagicMock()

    with patch("pygame.draw.circle") as mock_circle, patch(
        "pygame.draw.rect"
    ) as mock_rect:
        concrete_ghost.draw(screen_mock)

        # Should NOT draw body rect
        mock_rect.assert_not_called()

        # Should draw eyes (circles)
        assert mock_circle.call_count > 0


def test_random_direction_when_frightened(concrete_ghost, mock_game_map):
    """Tests that ghost picks random direction when frightened."""
    concrete_ghost.start_frightened()
    concrete_ghost._position = Position(150, 150)  # Center of tile

    # Mock multiple available directions
    # Using side_effect to allow movement in all directions
    mock_game_map.is_walkable.return_value = True

    with patch("random.choice") as mock_random:
        mock_random.return_value = Direction.UP
        concrete_ghost._choose_direction()

        assert concrete_ghost._direction == Direction.UP
        # Verify random.choice was called with a list of directions
        mock_random.assert_called()
