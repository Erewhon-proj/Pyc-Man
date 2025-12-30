"""
Test suite for Ghost features (state, animation, drawing).
Uses pytest-mock for patching.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=too-many-statements

import pytest
from pytest_mock import MockerFixture

from src.direction import Direction
from src.ghost import Ghost, GhostConfig, GhostHouseState, GhostState
from src.position import Position
from src.settings import GHOST_SPEED, TILE_SIZE


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
        """Concrete implementation for testing."""

        def calculate_target(
            self,
            pacman_x: float,
            pacman_y: float,
            pacman_direction: tuple[int, int],
        ) -> tuple[float, float]:
            return pacman_x, pacman_y

    return TestGhost(mock_game_map, ghost_config)


def test_start_frightened(concrete_ghost):
    """Tests transition to FRIGHTENED state."""
    # Ensure ghost is in a state that allows becoming frightened
    concrete_ghost._state = GhostState.SCATTER
    concrete_ghost._direction = Direction.LEFT

    concrete_ghost.start_frightened()

    assert concrete_ghost._state == GhostState.FRIGHTENED
    assert concrete_ghost._frightened_timer == 600
    assert concrete_ghost._speed == 1
    # Verify direction reversal
    assert concrete_ghost._direction == Direction.RIGHT


def test_frightened_timer_update(concrete_ghost):
    """Tests that frightened timer decrements and resets state."""
    concrete_ghost.start_frightened()
    concrete_ghost._frightened_timer = 1

    # Update call (pacman position irrelevant for this test)
    concrete_ghost.update(0, 0, (0, 0))

    assert concrete_ghost._state == GhostState.SCATTER
    assert concrete_ghost._speed == GHOST_SPEED


def test_get_eaten(concrete_ghost):
    """Tests transition to EATEN state."""
    concrete_ghost.get_eaten()

    assert concrete_ghost._state == GhostState.EATEN
    assert concrete_ghost._speed == 4


def test_eaten_return_to_house(concrete_ghost):
    """Tests respawning when EATEN ghost reaches house."""
    concrete_ghost.get_eaten()

    # Place ghost exactly at house exit
    exit_pos = concrete_ghost._house_exit
    concrete_ghost._position.x = exit_pos.x
    concrete_ghost._position.y = exit_pos.y

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


def test_draw_normal(concrete_ghost, mocker: MockerFixture):
    """Tests drawing calls in normal state."""
    screen_mock = mocker.Mock()
    mock_circle = mocker.patch("pygame.draw.circle")
    mock_rect = mocker.patch("pygame.draw.rect")

    concrete_ghost.draw(screen_mock)

    # Should draw body (circle + rect) and feet (circles) + eyes
    assert mock_circle.call_count >= 1
    assert mock_rect.call_count >= 1

    # Check color used (Red)
    # call_args_list[0] is the first call, args[1] is the color
    args, _ = mock_circle.call_args_list[0]
    assert args[1] == (255, 0, 0)


def test_draw_frightened(concrete_ghost, mocker: MockerFixture):
    """Tests drawing calls in frightened state."""
    concrete_ghost.start_frightened()
    screen_mock = mocker.Mock()
    mock_circle = mocker.patch("pygame.draw.circle")
    # We patch rect just to ensure it's called/not errored, though primarily checking color
    mocker.patch("pygame.draw.rect")

    concrete_ghost.draw(screen_mock)

    args, _ = mock_circle.call_args_list[0]
    # Verify it's NOT red (it is blue or white)
    assert args[1] != (255, 0, 0)


def test_draw_eaten(concrete_ghost, mocker: MockerFixture):
    """Tests drawing calls in eaten state (Only eyes)."""
    concrete_ghost.get_eaten()
    screen_mock = mocker.Mock()
    mock_circle = mocker.patch("pygame.draw.circle")
    mock_rect = mocker.patch("pygame.draw.rect")

    concrete_ghost.draw(screen_mock)

    # Should NOT draw body rect
    mock_rect.assert_not_called()
    # Should draw eyes (circles)
    assert mock_circle.call_count > 0


def test_random_direction_when_frightened(
    concrete_ghost, mock_game_map, mocker: MockerFixture
):
    """Tests that ghost picks random direction when frightened."""
    concrete_ghost.start_frightened()

    # Position must be centered on a tile for _choose_direction to work
    center_pos_x = 1 * TILE_SIZE + TILE_SIZE / 2
    center_pos_y = 1 * TILE_SIZE + TILE_SIZE / 2
    concrete_ghost._position = Position(center_pos_x, center_pos_y)

    # Mock multiple available directions
    mock_game_map.is_walkable.return_value = True

    # Use mocker to patch random.choice
    mock_choice = mocker.patch("random.choice", return_value=Direction.UP)

    concrete_ghost._choose_direction()

    assert concrete_ghost._direction == Direction.UP
    mock_choice.assert_called()
