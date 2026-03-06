"""
Test suite for Ghost classes.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

from dataclasses import dataclass
from typing import Tuple
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from src.difficulty import DifficultyManager
from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostConfig, GhostHouseState, GhostState
from src.position import Position
from src.settings import (
    GHOST_HOUSE_EXIT_X,
    GHOST_HOUSE_EXIT_Y,
    GHOST_SPEED,
    RED,
    TILE_SIZE,
)


@dataclass
class FrightenedTestCase:
    """Test case configuration for frightened behavior tests."""

    initial_state: GhostState
    initial_timer: int
    expected_timer: int
    should_refresh: bool


@pytest.fixture
def mock_game_map(mocker: MockerFixture) -> MagicMock:
    """Create a mocked GameMap for testing."""
    mock_map = mocker.Mock(spec=GameMap)
    mock_map.pixel_to_grid.return_value = (5, 5)
    mock_map.grid_to_pixel.return_value = (150.0, 150.0)
    mock_map.is_walkable.return_value = True
    mock_map.height = 22
    mock_map.width = 19
    return mock_map


@pytest.fixture
def ghost_config() -> GhostConfig:
    """Create a basic GhostConfig for testing."""
    return GhostConfig(
        start_position=Position(100.0, 100.0),
        color=RED,
        name="TestGhost",
        starts_in_house=False,
    )


@pytest.fixture
def concrete_ghost(mock_game_map: MagicMock, ghost_config: GhostConfig) -> Ghost:
    """Create a concrete Ghost implementation for testing"""

    class ConcreteGhost(Ghost):
        """Concrete implementation of Ghost for testing."""

        def calculate_target(
            self,
            pacman_x: float,
            pacman_y: float,
            _pacman_direction: Tuple[int, int],
        ) -> Tuple[float, float]:
            """Simple target calculation for testing."""
            return pacman_x, pacman_y

        def get_scatter_target(self) -> Tuple[float, float]:
            """Simple scatter target for testing."""
            return 0.0, 0.0

    return ConcreteGhost(mock_game_map, ghost_config)


# --- GhostHouseState Tests ---


def test_enum_has_correct_values():
    """Test that GhostHouseState has all required states."""
    states = list(GhostHouseState)
    assert len(states) == 3
    assert GhostHouseState.IN_HOUSE in states
    assert GhostHouseState.EXITING in states
    assert GhostHouseState.ACTIVE in states


# --- GhostConfig Tests ---


def test_config_initialization_with_all_fields():
    """Test GhostConfig initialization with all fields."""
    position = Position(50.0, 75.0)
    color = (255, 0, 0)
    name = "Blinky"

    config = GhostConfig(
        start_position=position,
        color=color,
        name=name,
        starts_in_house=True,
    )

    assert config.start_position == position
    assert config.color == color
    assert config.name == name
    assert config.starts_in_house is True


def test_config_default_starts_in_house():
    """Test that starts_in_house defaults to False."""
    position = Position(100.0, 100.0)
    config = GhostConfig(start_position=position, color=RED, name="Ghost")
    assert config.starts_in_house is False


# --- Ghost Initialization Tests ---


def test_ghost_initializes_with_config(mock_game_map, ghost_config):
    """Test Ghost initialization with GhostConfig."""

    class TestGhost(Ghost):
        """Minimal Ghost implementation for testing."""

        def calculate_target(self, _pacman_x, _pacman_y, _pacman_direction):
            """Calculate target position for testing."""
            return 0, 0

        def get_scatter_target(self):
            """Get scatter target for testing."""
            return 0.0, 0.0

    ghost = TestGhost(mock_game_map, ghost_config)

    assert ghost._game_map == mock_game_map
    assert ghost._position.x == ghost_config.start_position.x
    assert ghost._position.y == ghost_config.start_position.y
    assert ghost._color == ghost_config.color
    assert ghost._name == ghost_config.name


def test_ghost_initializes_with_default_speed(concrete_ghost):
    """Test that ghost speed is set from settings."""
    assert concrete_ghost._speed == GHOST_SPEED


def test_ghost_initializes_with_right_direction(concrete_ghost):
    """Test that ghost starts facing right."""
    assert concrete_ghost._direction == Direction.RIGHT


@pytest.mark.parametrize(
    "starts_in_house, expected_state",
    [
        (True, GhostHouseState.IN_HOUSE),
        (False, GhostHouseState.ACTIVE),
    ],
)
def test_ghost_house_state_initialization(
    mock_game_map,
    starts_in_house,
    expected_state,
):
    """Test ghost house state is set correctly based on config."""
    config = GhostConfig(
        start_position=Position(100, 100),
        color=RED,
        name="StateTest",
        starts_in_house=starts_in_house,
    )

    class TestGhost(Ghost):
        """Minimal Ghost implementation for testing."""

        def calculate_target(self, _pacman_x, _pacman_y, _pacman_direction):
            """Calculate target position for testing."""
            return 0, 0

        def get_scatter_target(self):
            """Get scatter target for testing."""
            return 0.0, 0.0

    ghost = TestGhost(mock_game_map, config)
    assert ghost._house_state == expected_state


def test_ghost_house_exit_position_calculated_correctly(concrete_ghost):
    """Test that house exit position is calculated from settings."""
    expected_x = GHOST_HOUSE_EXIT_X * TILE_SIZE
    expected_y = GHOST_HOUSE_EXIT_Y * TILE_SIZE

    assert concrete_ghost._house_exit.x == expected_x
    assert concrete_ghost._house_exit.y == expected_y


# --- Ghost Properties Tests ---


def test_x_property_returns_position_x(concrete_ghost):
    """Test that x property returns correct value."""
    concrete_ghost._position.x = 123.45
    assert concrete_ghost.x == 123.45


def test_y_property_returns_position_y(concrete_ghost):
    """Test that y property returns correct value."""
    concrete_ghost._position.y = 678.90
    assert concrete_ghost.y == 678.90


@pytest.mark.parametrize(
    "house_state, expected",
    [
        (GhostHouseState.IN_HOUSE, True),
        (GhostHouseState.EXITING, False),
        (GhostHouseState.ACTIVE, False),
    ],
)
def test_in_ghost_house_property(concrete_ghost, house_state, expected):
    """Test in_ghost_house property for different states."""
    concrete_ghost._house_state = house_state
    assert concrete_ghost.in_ghost_house == expected


def test_color_property_returns_color(concrete_ghost):
    """Test that color property returns correct value."""
    assert concrete_ghost.color == RED


def test_name_property_returns_name(concrete_ghost):
    """Test that name property returns correct value."""
    assert concrete_ghost.name == "TestGhost"


# --- Ghost Abstract Method Tests ---


def test_cannot_instantiate_ghost_directly(mock_game_map, ghost_config):
    """Test Ghost cannot be instantiated without abstract method."""
    with pytest.raises(TypeError) as exc_info:
        # pylint: disable=abstract-class-instantiated
        Ghost(mock_game_map, ghost_config)  # type: ignore[abstract]

    assert "abstract" in str(exc_info.value).lower()


def test_concrete_implementation_calculates_target(concrete_ghost):
    """Test that concrete implementation can calculate target."""
    target = concrete_ghost.calculate_target(100.0, 200.0, (1, 0))

    assert isinstance(target, tuple)
    assert len(target) == 2
    assert target == (100.0, 200.0)


# --- Ghost Update Tests ---


def test_update_does_nothing_when_in_house(concrete_ghost, mocker: MockerFixture):
    """Test that ghost doesn't move when IN_HOUSE."""
    concrete_ghost._house_state = GhostHouseState.IN_HOUSE
    initial_position = Position(concrete_ghost._position.x, concrete_ghost._position.y)
    spy_choose = mocker.spy(concrete_ghost, "_choose_direction")
    spy_move = mocker.spy(concrete_ghost, "_move")

    concrete_ghost.update(200.0, 200.0, (1, 0))

    assert concrete_ghost._position.x == initial_position.x
    assert concrete_ghost._position.y == initial_position.y
    spy_choose.assert_not_called()
    spy_move.assert_not_called()


def test_update_calls_exit_house_when_exiting(concrete_ghost, mocker: MockerFixture):
    """Test that ghost calls _exit_house when EXITING."""
    concrete_ghost._house_state = GhostHouseState.EXITING
    spy_exit = mocker.spy(concrete_ghost, "_exit_house")
    spy_choose = mocker.spy(concrete_ghost, "_choose_direction")

    concrete_ghost.update(200.0, 200.0, (1, 0))

    spy_exit.assert_called_once()
    spy_choose.assert_not_called()


def test_update_normal_behavior_when_active(concrete_ghost, mocker: MockerFixture):
    """Test that ghost performs AI when ACTIVE."""
    concrete_ghost._house_state = GhostHouseState.ACTIVE
    concrete_ghost._state = GhostState.CHASE  # Set to CHASE so calculate_target is used
    spy_choose = mocker.spy(concrete_ghost, "_choose_direction")
    spy_move = mocker.spy(concrete_ghost, "_move")

    concrete_ghost.update(200.0, 200.0, (1, 0))

    spy_choose.assert_called_once()
    spy_move.assert_called_once()
    assert concrete_ghost._target is not None
    assert concrete_ghost._target.x == 200.0
    assert concrete_ghost._target.y == 200.0


# --- Ghost Choose Direction Tests ---


def test_choose_direction_does_nothing_when_no_target(concrete_ghost):
    """Test that direction isn't changed when target is None."""
    concrete_ghost._target = None
    initial_direction = concrete_ghost._direction

    concrete_ghost._choose_direction()

    assert concrete_ghost._direction == initial_direction


def test_choose_direction_picks_direction_towards_target(concrete_ghost, mock_game_map):
    """Test that ghost picks direction that moves towards target."""

    def grid_to_pixel_mock(x: int, y: int) -> Tuple[float, float]:
        return x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2

    concrete_ghost._position = Position(150.0, 150.0)
    concrete_ghost._target = Position(250.0, 150.0)
    mock_game_map.grid_to_pixel.side_effect = grid_to_pixel_mock
    mock_game_map.is_walkable.return_value = True

    concrete_ghost._choose_direction()
    assert concrete_ghost._direction == Direction.RIGHT


def test_choose_direction_avoids_going_backwards(concrete_ghost, mock_game_map):
    """Test that ghost never reverses direction."""
    concrete_ghost._position = Position(150.0, 150.0)
    concrete_ghost._direction = Direction.RIGHT
    concrete_ghost._target = Position(50.0, 150.0)
    mock_game_map.pixel_to_grid.return_value = (5, 5)
    mock_game_map.grid_to_pixel.return_value = (150.0, 150.0)

    def is_walkable_mock(x: int, y: int) -> bool:
        return (x, y) in [(5, 4), (5, 6)]  # UP and DOWN are valid

    mock_game_map.is_walkable.side_effect = is_walkable_mock

    concrete_ghost._choose_direction()
    assert concrete_ghost._direction != Direction.LEFT


# --- Ghost Move Tests ---


def test_move_updates_position_when_walkable(concrete_ghost, mock_game_map):
    """Test that ghost moves when path is clear."""
    concrete_ghost._position = Position(150.0, 150.0)
    concrete_ghost._direction = Direction.RIGHT
    concrete_ghost._speed = 2
    mock_game_map.is_walkable.return_value = True

    concrete_ghost._move()
    assert concrete_ghost._position.x == 152.0
    assert concrete_ghost._position.y == 150.0


def test_move_snaps_to_center_when_blocked(concrete_ghost, mock_game_map):
    """Test that ghost snaps to tile center only when trying to move PAST center toward wall.

    This matches Pac-Man's behavior to prevent bouncing.
    """
    # Setup: Ghost is past center, trying to move further right into wall
    concrete_ghost._position = Position(151.0, 150.0)  # Past center
    concrete_ghost._direction = Direction.RIGHT
    concrete_ghost._speed = 2.0
    mock_game_map.is_walkable.return_value = False  # Wall ahead
    mock_game_map.grid_to_pixel.return_value = (150.0, 150.0)  # Center of current tile

    concrete_ghost._move()

    assert concrete_ghost._position.x == 150.0
    assert concrete_ghost._position.y == 150.0


# --- Ghost Exit House Tests ---


def test_exit_house_moves_horizontally_first(concrete_ghost):
    """Test that ghost moves horizontally towards exit first."""
    exit_x = concrete_ghost._house_exit.x
    concrete_ghost._position = Position(exit_x - 20.0, 200.0)
    concrete_ghost._speed = 2.0
    concrete_ghost._house_state = GhostHouseState.EXITING

    concrete_ghost._exit_house()

    assert concrete_ghost._position.x > (exit_x - 20.0)


# --- Difficulty System Tests ---


@pytest.fixture
def difficulty_manager_level_1():
    """Provide DifficultyManager for level 1."""
    return DifficultyManager(level=1)


@pytest.fixture
def difficulty_manager_level_3():
    """Provide DifficultyManager for level 3."""
    return DifficultyManager(level=3)


@pytest.fixture
def concrete_ghost_with_difficulty(
    mock_game_map: MagicMock,
    ghost_config: GhostConfig,
    difficulty_manager_level_1: DifficultyManager,
) -> Ghost:
    """Create a concrete Ghost implementation with difficulty manager for testing."""

    class ConcreteGhost(Ghost):
        """Concrete implementation of Ghost for testing."""

        def calculate_target(
            self,
            pacman_x: float,
            pacman_y: float,
            _pacman_direction: Tuple[int, int],
        ) -> Tuple[float, float]:
            """Simple target calculation for testing."""
            return pacman_x, pacman_y

        def get_scatter_target(self) -> Tuple[float, float]:
            """Simple scatter target for testing."""
            return 0.0, 0.0

    return ConcreteGhost(mock_game_map, ghost_config, difficulty_manager_level_1)


def test_ghost_with_difficulty_manager_uses_level_based_speed(
    concrete_ghost_with_difficulty: Ghost,
):
    """Test that ghost uses difficulty manager for base speed calculation."""
    # At level 1, speed should be base speed
    assert concrete_ghost_with_difficulty._speed == GHOST_SPEED


def test_ghost_without_difficulty_manager_uses_default_speed(concrete_ghost: Ghost):
    """Test that ghost without difficulty manager uses default speed."""
    assert concrete_ghost._speed == GHOST_SPEED


@pytest.mark.parametrize(
    "test_case",
    [
        FrightenedTestCase(GhostState.SCATTER, 0, 600, True),  # First activation
        FrightenedTestCase(GhostState.CHASE, 0, 600, True),  # From CHASE
        FrightenedTestCase(GhostState.FRIGHTENED, 100, 600, True),  # Refresh existing
        FrightenedTestCase(GhostState.EATEN, 0, 0, False),  # EATEN not affected
    ],
)
def test_start_frightened_with_difficulty_manager(
    concrete_ghost_with_difficulty: Ghost, test_case: FrightenedTestCase
) -> None:
    """Test start_frightened behavior with difficulty manager across different states."""
    concrete_ghost_with_difficulty._state = test_case.initial_state
    concrete_ghost_with_difficulty._frightened_timer = test_case.initial_timer

    concrete_ghost_with_difficulty.start_frightened()

    if test_case.should_refresh:
        assert concrete_ghost_with_difficulty._state == GhostState.FRIGHTENED
        assert (
            concrete_ghost_with_difficulty._frightened_timer == test_case.expected_timer
        )
        assert concrete_ghost_with_difficulty._speed == 1.0
    else:
        # EATEN state should not be affected
        assert concrete_ghost_with_difficulty._state == GhostState.EATEN
        assert (
            concrete_ghost_with_difficulty._frightened_timer == test_case.initial_timer
        )


def test_start_frightened_without_difficulty_manager(concrete_ghost: Ghost):
    """Test that frightened without difficulty manager uses default duration."""
    concrete_ghost._state = GhostState.SCATTER
    concrete_ghost.start_frightened()

    # Should use default 600 frames
    assert concrete_ghost._frightened_timer == 600


def test_chase_speed_multiplier_applied_in_move(
    concrete_ghost_with_difficulty: Ghost, mock_game_map: MagicMock
):
    """Test that CHASE mode speed multiplier is applied during movement."""
    concrete_ghost_with_difficulty._state = GhostState.CHASE
    concrete_ghost_with_difficulty._position = Position(150.0, 150.0)
    concrete_ghost_with_difficulty._direction = Direction.RIGHT
    concrete_ghost_with_difficulty._speed = 2.0
    mock_game_map.is_walkable.return_value = True
    mock_game_map.pixel_to_grid.return_value = (5, 5)
    mock_game_map.grid_to_pixel.return_value = (150.0, 150.0)

    initial_x = concrete_ghost_with_difficulty._position.x
    concrete_ghost_with_difficulty._move()

    # With CHASE multiplier of 1.0 at level 1, should move at normal speed
    # Speed: 2.0 * 1.0 (CHASE) * 1.0 (no tunnel) = 2.0
    assert concrete_ghost_with_difficulty._position.x == initial_x + 2.0


def test_respawn_in_house_uses_difficulty_manager_speed(
    concrete_ghost_with_difficulty: Ghost,
):
    """Test that respawn uses difficulty manager for speed calculation."""
    concrete_ghost_with_difficulty._state = GhostState.EATEN
    concrete_ghost_with_difficulty._position = Position(
        concrete_ghost_with_difficulty._house_exit.x,
        concrete_ghost_with_difficulty._house_exit.y,
    )

    concrete_ghost_with_difficulty.update(0, 0, (0, 0))

    # Should use difficulty manager's base speed after respawn
    assert concrete_ghost_with_difficulty._speed == GHOST_SPEED
    assert concrete_ghost_with_difficulty._state == GhostState.SCATTER


def test_frightened_timer_expires_uses_difficulty_manager_speed(
    concrete_ghost_with_difficulty: Ghost,
):
    """Test that speed resets to difficulty manager's speed when frightened expires."""
    concrete_ghost_with_difficulty._state = GhostState.FRIGHTENED
    concrete_ghost_with_difficulty._frightened_timer = 1
    concrete_ghost_with_difficulty._speed = 1.0

    concrete_ghost_with_difficulty.update(0, 0, (0, 0))

    # Should revert to difficulty manager's base speed
    assert concrete_ghost_with_difficulty._state == GhostState.SCATTER
    assert concrete_ghost_with_difficulty._speed == GHOST_SPEED


def test_return_to_house_uses_difficulty_manager_speed(
    concrete_ghost_with_difficulty: Ghost,
):
    """Test that return_to_house uses difficulty manager for speed calculation."""
    concrete_ghost_with_difficulty.return_to_house()

    # Should use difficulty manager's base speed
    assert concrete_ghost_with_difficulty._speed == GHOST_SPEED
    assert concrete_ghost_with_difficulty._state == GhostState.SCATTER
    assert concrete_ghost_with_difficulty._house_state == GhostHouseState.IN_HOUSE


def test_high_level_ghost_has_correct_speed(
    mock_game_map: MagicMock, ghost_config: GhostConfig
):
    """Test that high level ghost has correct speed calculation."""
    high_level_difficulty = DifficultyManager(level=5)

    class ConcreteGhost(Ghost):
        """Concrete implementation of Ghost for testing."""

        def calculate_target(
            self,
            _pacman_x: float,
            _pacman_y: float,
            _pacman_direction: Tuple[int, int],
        ) -> Tuple[float, float]:
            """Calculate target position for testing."""
            return _pacman_x, _pacman_y

        def get_scatter_target(self) -> Tuple[float, float]:
            """Get scatter target for testing."""
            return 0.0, 0.0

    ghost = ConcreteGhost(mock_game_map, ghost_config, high_level_difficulty)

    # At level 5, speed should be at maximum (plateau)
    assert ghost._speed == 2.0


def test_high_level_ghost_has_correct_frightened_duration(
    mock_game_map: MagicMock, ghost_config: GhostConfig
):
    """Test that high level ghost has reduced frightened duration."""
    high_level_difficulty = DifficultyManager(level=5)

    class ConcreteGhost(Ghost):
        """Concrete implementation of Ghost for testing."""

        def calculate_target(
            self,
            _pacman_x: float,
            _pacman_y: float,
            _pacman_direction: Tuple[int, int],
        ) -> Tuple[float, float]:
            """Calculate target position for testing."""
            return _pacman_x, _pacman_y

        def get_scatter_target(self) -> Tuple[float, float]:
            """Get scatter target for testing."""
            return 0.0, 0.0

    ghost = ConcreteGhost(mock_game_map, ghost_config, high_level_difficulty)
    ghost._state = GhostState.SCATTER
    ghost.start_frightened()

    # At level 5, frightened duration should be 3 seconds (180 frames)
    assert ghost._frightened_timer == 180
