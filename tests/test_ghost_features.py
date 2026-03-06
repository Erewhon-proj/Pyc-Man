"""
Test suite for Ghost features (state, animation, drawing).
Uses pytest-mock for patching.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=too-many-statements

from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostConfig, GhostHouseState, GhostState
from src.position import Position
from src.settings import GHOST_SPEED, TILE_SIZE


@dataclass
class FrightenedStateTestCase:
    """Test case for frightened state transitions."""

    initial_state: GhostState
    expected_state: GhostState
    expected_timer: int


@pytest.fixture
def ghost_config() -> GhostConfig:
    """Basic ghost configuration."""
    return GhostConfig(
        start_position=Position(100, 100),
        color=(255, 0, 0),
        name="TestGhost",
        starts_in_house=False,
    )


@pytest.fixture
def concrete_ghost(mock_game_map: GameMap, ghost_config: GhostConfig) -> Ghost:
    """Concrete Ghost instance (since Ghost is abstract)."""

    class TestGhost(Ghost):
        """Concrete implementation for testing."""

        def calculate_target(
            self,
            pacman_x: float,
            pacman_y: float,
            _pacman_direction: tuple[int, int],
        ) -> tuple[float, float]:
            """Calculate target position for testing."""
            return pacman_x, pacman_y

        def get_scatter_target(self) -> tuple[float, float]:
            """Get scatter target for testing."""
            return 0.0, 0.0

    return TestGhost(mock_game_map, ghost_config)


def test_start_frightened(concrete_ghost: Ghost) -> None:
    """Tests transition to FRIGHTENED state."""
    concrete_ghost._state = GhostState.SCATTER
    concrete_ghost._direction = Direction.LEFT

    concrete_ghost.start_frightened()

    assert concrete_ghost._state == GhostState.FRIGHTENED
    assert concrete_ghost._frightened_timer == 600
    assert concrete_ghost._speed == 1
    assert concrete_ghost._direction == Direction.RIGHT


def test_frightened_timer_update(concrete_ghost: Ghost) -> None:
    """Tests that frightened timer decrements and resets state."""
    concrete_ghost.start_frightened()
    concrete_ghost._frightened_timer = 1

    concrete_ghost.update(0, 0, (0, 0))

    assert concrete_ghost._state == GhostState.SCATTER
    assert concrete_ghost._speed == GHOST_SPEED


@pytest.mark.parametrize(
    "test_case",
    [
        FrightenedStateTestCase(
            GhostState.SCATTER, GhostState.FRIGHTENED, 600
        ),  # Normal activation
        FrightenedStateTestCase(
            GhostState.CHASE, GhostState.FRIGHTENED, 600
        ),  # From CHASE mode
        FrightenedStateTestCase(
            GhostState.FRIGHTENED, GhostState.FRIGHTENED, 600
        ),  # Refresh timer
        FrightenedStateTestCase(
            GhostState.EATEN, GhostState.EATEN, 0
        ),  # EATEN not affected
    ],
)
def test_start_frightened_behavior(
    concrete_ghost: Ghost, test_case: FrightenedStateTestCase
) -> None:
    """Tests start_frightened behavior across different initial states."""
    concrete_ghost._state = test_case.initial_state
    if test_case.initial_state == GhostState.FRIGHTENED:
        concrete_ghost._frightened_timer = 100  # Low timer to test refresh
    elif test_case.initial_state == GhostState.EATEN:
        concrete_ghost._speed = 4  # EATEN speed

    concrete_ghost.start_frightened()

    assert concrete_ghost._state == test_case.expected_state
    if test_case.expected_state == GhostState.FRIGHTENED:
        assert concrete_ghost._frightened_timer == test_case.expected_timer
        assert concrete_ghost._speed == 1
    else:
        # EATEN state should not be affected
        assert concrete_ghost._frightened_timer == 0
        assert concrete_ghost._speed == 4


def test_get_eaten(concrete_ghost: Ghost) -> None:
    """Tests transition to EATEN state."""
    concrete_ghost.get_eaten()

    assert concrete_ghost._state == GhostState.EATEN
    assert concrete_ghost._speed == 4


def test_eaten_return_to_house(concrete_ghost: Ghost) -> None:
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


def test_animation_update(concrete_ghost: Ghost) -> None:
    """Tests that animation frame advances."""
    initial_frame = concrete_ghost._animation_frame
    concrete_ghost.update(0, 0, (0, 0))
    assert concrete_ghost._animation_frame != initial_frame


def test_draw_normal(concrete_ghost: Ghost, mocker: MockerFixture) -> None:
    """Tests drawing calls in normal state."""
    screen_mock = mocker.Mock()
    mock_circle = mocker.patch("pygame.draw.circle")
    mock_rect = mocker.patch("pygame.draw.rect")

    concrete_ghost.draw(screen_mock)

    # Should draw body (circle + rect) and feet (circles) + eyes
    assert mock_circle.call_count >= 1
    assert mock_rect.call_count >= 1

    # Check color used (Red)
    args, _ = mock_circle.call_args_list[0]
    assert args[1] == (255, 0, 0)


def test_draw_frightened(concrete_ghost: Ghost, mocker: MockerFixture) -> None:
    """Tests drawing calls in frightened state."""
    concrete_ghost.start_frightened()
    screen_mock = mocker.Mock()
    mock_circle = mocker.patch("pygame.draw.circle")
    mocker.patch("pygame.draw.rect")

    concrete_ghost.draw(screen_mock)

    args, _ = mock_circle.call_args_list[0]
    # Verify it's NOT red (it is blue or white)
    assert args[1] != (255, 0, 0)


def test_draw_eaten(concrete_ghost: Ghost, mocker: MockerFixture) -> None:
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
    concrete_ghost: Ghost, mock_game_map, mocker: MockerFixture
) -> None:
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


def test_draw_on_menu(concrete_ghost, mocker: MockerFixture):
    """Tests that draw_on_menu correctly updates state and calls draw."""
    # ---Setup mock screen and parameters---
    screen_mock = mocker.Mock()
    pacman_y = 300.0
    index = 2
    mock_screen_width = 800

    # Patch the SCREEN_WIDTH constant in the module where it is used (src.ghost)
    mocker.patch("src.ghost.settings.SCREEN_WIDTH", mock_screen_width)

    # Mock the draw method on the instance itself (to verify it's called without rendering)
    mock_draw = mocker.patch.object(concrete_ghost, "draw")

    # Capture the initial state to verify the update
    initial_animation_frame = concrete_ghost._animation_frame
    expected_animation_frame = (
        initial_animation_frame + concrete_ghost._animation_speed
    ) % 2

    # Calculate the expected result for the X coordinate
    expected_x = (mock_screen_width // 2) - 20 + (index * 40)

    # ---Execute the method under test---
    concrete_ghost.draw_on_menu(screen_mock, pacman_y, index)

    # ---Assertions---
    # Verify the X position
    assert concrete_ghost._position.x == expected_x

    # Verify the Y position
    assert concrete_ghost._position.y == pacman_y

    # Verify the direction is forced to the left
    assert concrete_ghost._direction == Direction.LEFT

    # Verify the animation frame update
    assert concrete_ghost._animation_frame == expected_animation_frame

    # Verify that the draw method was called exactly once with the mocked screen
    mock_draw.assert_called_once_with(screen_mock)
