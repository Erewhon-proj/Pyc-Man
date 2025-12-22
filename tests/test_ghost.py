"""
Test suite for Ghost classes.
"""

# pylint: disable=redefined-outer-name  # pytest fixtures pattern
# pylint: disable=protected-access  # white-box testing

from typing import Tuple

import pytest
from pytest_mock import MockerFixture  # type: ignore[import-not-found]

from src.direction import Direction
from src.game_map import GameMap
from src.ghost import Ghost, GhostConfig, GhostHouseState
from src.position import Position
from src.settings import (
    GHOST_HOUSE_EXIT_X,
    GHOST_HOUSE_EXIT_Y,
    GHOST_SPEED,
    RED,
    TILE_SIZE,
)


@pytest.fixture
def mock_game_map(mocker: MockerFixture) -> GameMap:
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
def concrete_ghost(mock_game_map: GameMap, ghost_config: GhostConfig) -> Ghost:
    """Create a concrete Ghost implementation for testing"""

    class ConcreteGhost(Ghost):
        """Concrete implementation of Ghost for testing."""

        def calculate_target(
            self,
            pacman_x: float,
            pacman_y: float,
            pacman_direction: Tuple[int, int],
        ) -> Tuple[float, float]:
            """Simple target calculation for testing."""
            return pacman_x, pacman_y

    return ConcreteGhost(mock_game_map, ghost_config)


class TestGhostHouseState:
    """Test suite for GhostHouseState enum."""

    def test_enum_has_correct_values(self) -> None:
        """Test that GhostHouseState has all required states."""
        states = list(GhostHouseState)

        assert len(states) == 3
        assert GhostHouseState.IN_HOUSE in states
        assert GhostHouseState.EXITING in states
        assert GhostHouseState.ACTIVE in states


class TestGhostConfig:
    """Test suite for GhostConfig dataclass."""

    def test_config_initialization_with_all_fields(self) -> None:
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

    def test_config_default_starts_in_house(self) -> None:
        """Test that starts_in_house defaults to False."""
        position = Position(100.0, 100.0)

        config = GhostConfig(start_position=position, color=RED, name="Ghost")

        assert config.starts_in_house is False


class TestGhostInitialization:
    """Test suite for Ghost initialization."""

    def test_ghost_initializes_with_config(
        self, mock_game_map: GameMap, ghost_config: GhostConfig
    ) -> None:
        """Test Ghost initialization with GhostConfig."""

        class TestGhost(Ghost):
            """Minimal Ghost implementation for testing."""

            def calculate_target(self, pacman_x, pacman_y, pacman_direction):
                return 0, 0

        ghost = TestGhost(mock_game_map, ghost_config)

        assert ghost._game_map == mock_game_map
        assert ghost._position.x == ghost_config.start_position.x
        assert ghost._position.y == ghost_config.start_position.y
        assert ghost._color == ghost_config.color
        assert ghost._name == ghost_config.name

    def test_ghost_initializes_with_default_speed(self, concrete_ghost: Ghost) -> None:
        """Test that ghost speed is set from settings."""
        assert concrete_ghost._speed == GHOST_SPEED

    def test_ghost_initializes_with_right_direction(
        self, concrete_ghost: Ghost
    ) -> None:
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
        self,
        mock_game_map: GameMap,
        starts_in_house: bool,
        expected_state: GhostHouseState,
    ) -> None:
        """Test ghost house state is set correctly based on config."""
        config = GhostConfig(
            start_position=Position(100, 100),
            color=RED,
            name="StateTest",
            starts_in_house=starts_in_house,
        )

        class TestGhost(Ghost):
            """Minimal Ghost implementation for testing."""

            def calculate_target(self, pacman_x, pacman_y, pacman_direction):
                return 0, 0

        ghost = TestGhost(mock_game_map, config)

        assert ghost._house_state == expected_state

    def test_ghost_house_exit_position_calculated_correctly(
        self, concrete_ghost: Ghost
    ) -> None:
        """Test that house exit position is calculated from settings."""
        expected_x = GHOST_HOUSE_EXIT_X * TILE_SIZE
        expected_y = GHOST_HOUSE_EXIT_Y * TILE_SIZE

        assert concrete_ghost._house_exit.x == expected_x
        assert concrete_ghost._house_exit.y == expected_y


class TestGhostProperties:
    """Test suite for Ghost properties."""

    def test_x_property_returns_position_x(self, concrete_ghost: Ghost) -> None:
        """Test that x property returns correct value."""
        concrete_ghost._position.x = 123.45

        x = concrete_ghost.x

        assert x == 123.45

    def test_y_property_returns_position_y(self, concrete_ghost: Ghost) -> None:
        """Test that y property returns correct value."""
        concrete_ghost._position.y = 678.90

        y = concrete_ghost.y

        assert y == 678.90

    @pytest.mark.parametrize(
        "house_state, expected",
        [
            (GhostHouseState.IN_HOUSE, True),
            (GhostHouseState.EXITING, False),
            (GhostHouseState.ACTIVE, False),
        ],
    )
    def test_in_ghost_house_property(
        self,
        concrete_ghost: Ghost,
        house_state: GhostHouseState,
        expected: bool,
    ) -> None:
        """Test in_ghost_house property for different states."""
        concrete_ghost._house_state = house_state

        result = concrete_ghost.in_ghost_house

        assert result == expected


class TestGhostAbstractMethod:
    """Test suite for Ghost abstract method."""

    def test_cannot_instantiate_ghost_directly(
        self, mock_game_map: GameMap, ghost_config: GhostConfig
    ) -> None:
        """Test Ghost cannot be instantiated without abstract method."""
        with pytest.raises(TypeError) as exc_info:
            # pylint: disable=abstract-class-instantiated
            Ghost(mock_game_map, ghost_config)  # type: ignore[abstract]

        assert "abstract" in str(exc_info.value).lower()

    def test_concrete_implementation_calculates_target(
        self, concrete_ghost: Ghost
    ) -> None:
        """Test that concrete implementation can calculate target."""
        target = concrete_ghost.calculate_target(100.0, 200.0, (1, 0))

        assert isinstance(target, tuple)
        assert len(target) == 2
        assert target == (100.0, 200.0)


class TestGhostUpdate:
    """Test suite for Ghost update() method."""

    def test_update_does_nothing_when_in_house(
        self, concrete_ghost: Ghost, mocker: MockerFixture
    ) -> None:
        """Test that ghost doesn't move when IN_HOUSE."""
        concrete_ghost._house_state = GhostHouseState.IN_HOUSE
        initial_position = Position(
            concrete_ghost._position.x, concrete_ghost._position.y
        )
        spy_choose = mocker.spy(concrete_ghost, "_choose_direction")
        spy_move = mocker.spy(concrete_ghost, "_move")

        concrete_ghost.update(200.0, 200.0, (1, 0))

        assert concrete_ghost._position.x == initial_position.x
        assert concrete_ghost._position.y == initial_position.y
        spy_choose.assert_not_called()
        spy_move.assert_not_called()

    def test_update_calls_exit_house_when_exiting(
        self, concrete_ghost: Ghost, mocker: MockerFixture
    ) -> None:
        """Test that ghost calls _exit_house when EXITING."""
        concrete_ghost._house_state = GhostHouseState.EXITING
        spy_exit = mocker.spy(concrete_ghost, "_exit_house")
        spy_choose = mocker.spy(concrete_ghost, "_choose_direction")

        concrete_ghost.update(200.0, 200.0, (1, 0))

        spy_exit.assert_called_once()
        spy_choose.assert_not_called()

    def test_update_normal_behavior_when_active(
        self, concrete_ghost: Ghost, mocker: MockerFixture
    ) -> None:
        """Test that ghost performs AI when ACTIVE."""
        concrete_ghost._house_state = GhostHouseState.ACTIVE
        spy_choose = mocker.spy(concrete_ghost, "_choose_direction")
        spy_move = mocker.spy(concrete_ghost, "_move")

        concrete_ghost.update(200.0, 200.0, (1, 0))

        spy_choose.assert_called_once()
        spy_move.assert_called_once()
        assert concrete_ghost._target is not None
        assert concrete_ghost._target.x == 200.0
        assert concrete_ghost._target.y == 200.0


class TestGhostChooseDirection:
    """Test suite for Ghost _choose_direction() method."""

    def test_choose_direction_does_nothing_when_no_target(
        self, concrete_ghost: Ghost
    ) -> None:
        """Test that direction isn't changed when target is None."""
        concrete_ghost._target = None
        initial_direction = concrete_ghost._direction

        concrete_ghost._choose_direction()

        assert concrete_ghost._direction == initial_direction

    def test_choose_direction_picks_direction_towards_target(
        self, concrete_ghost: Ghost, mock_game_map: GameMap
    ) -> None:
        """Test that ghost picks direction that moves towards target."""

        def grid_to_pixel_mock(x: int, y: int) -> Tuple[float, float]:
            return x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2

        concrete_ghost._position = Position(150.0, 150.0)
        concrete_ghost._target = Position(250.0, 150.0)
        mock_game_map.grid_to_pixel.side_effect = grid_to_pixel_mock  # type: ignore[attr-defined]
        mock_game_map.is_walkable.return_value = True  # type: ignore[attr-defined]

        concrete_ghost._choose_direction()

        assert concrete_ghost._direction == Direction.RIGHT

    def test_choose_direction_avoids_going_backwards(
        self, concrete_ghost: Ghost, mock_game_map: GameMap
    ) -> None:
        """Test that ghost never reverses direction."""
        concrete_ghost._position = Position(150.0, 150.0)
        concrete_ghost._direction = Direction.RIGHT
        concrete_ghost._target = Position(50.0, 150.0)
        mock_game_map.pixel_to_grid.return_value = (5, 5)  # type: ignore[attr-defined]
        mock_game_map.grid_to_pixel.return_value = (150.0, 150.0)  # type: ignore[attr-defined]

        def is_walkable_mock(x: int, y: int) -> bool:
            return (x, y) in [(5, 4), (5, 6)]

        mock_game_map.is_walkable.side_effect = is_walkable_mock  # type: ignore[attr-defined]

        concrete_ghost._choose_direction()

        assert concrete_ghost._direction != Direction.LEFT


class TestGhostMove:
    """Test suite for Ghost _move() method."""

    def test_move_updates_position_when_walkable(
        self, concrete_ghost: Ghost, mock_game_map: GameMap
    ) -> None:
        """Test that ghost moves when path is clear."""
        concrete_ghost._position = Position(150.0, 150.0)
        concrete_ghost._direction = Direction.RIGHT
        concrete_ghost._speed = 2
        mock_game_map.is_walkable.return_value = True  # type: ignore[attr-defined]

        concrete_ghost._move()

        assert concrete_ghost._position.x == 152.0
        assert concrete_ghost._position.y == 150.0

    def test_move_snaps_to_center_when_blocked(
        self, concrete_ghost: Ghost, mock_game_map: GameMap
    ) -> None:
        """Test that ghost snaps to tile center when hitting wall."""
        concrete_ghost._position = Position(148.0, 148.0)
        concrete_ghost._direction = Direction.RIGHT
        mock_game_map.is_walkable.return_value = False  # type: ignore[attr-defined]
        mock_game_map.grid_to_pixel.return_value = (150.0, 150.0)  # type: ignore[attr-defined]

        concrete_ghost._move()

        assert concrete_ghost._position.x == 150.0
        assert concrete_ghost._position.y == 150.0


class TestGhostExitHouse:
    """Test suite for Ghost _exit_house() method."""

    def test_exit_house_moves_horizontally_first(self, concrete_ghost: Ghost) -> None:
        """Test that ghost moves horizontally towards exit first."""
        exit_x = concrete_ghost._house_exit.x
        concrete_ghost._position = Position(exit_x - 20.0, 200.0)
        concrete_ghost._speed = 2

        concrete_ghost._exit_house()

        assert concrete_ghost._position.x == exit_x - 18.0
        assert concrete_ghost._position.y == 200.0

    def test_exit_house_moves_vertically_after_centered(
        self, concrete_ghost: Ghost
    ) -> None:
        """Test that ghost moves up after horizontal alignment."""
        exit_x = concrete_ghost._house_exit.x
        exit_y = concrete_ghost._house_exit.y
        concrete_ghost._position = Position(exit_x, exit_y + 20.0)
        concrete_ghost._speed = 2

        concrete_ghost._exit_house()

        assert concrete_ghost._position.x == exit_x
        assert concrete_ghost._position.y == exit_y + 18.0

    def test_exit_house_transitions_to_active_when_reached(
        self, concrete_ghost: Ghost
    ) -> None:
        """Test that ghost becomes ACTIVE when reaching exit."""
        concrete_ghost._position = Position(
            concrete_ghost._house_exit.x, concrete_ghost._house_exit.y
        )
        concrete_ghost._house_state = GhostHouseState.EXITING

        concrete_ghost._exit_house()

        assert concrete_ghost._house_state == GhostHouseState.ACTIVE


class TestGhostReleaseFromHouse:
    """Test suite for Ghost release_from_house() method."""

    @pytest.mark.parametrize(
        "initial_state, expected_state",
        [
            (GhostHouseState.IN_HOUSE, GhostHouseState.EXITING),
            (GhostHouseState.EXITING, GhostHouseState.EXITING),
            (GhostHouseState.ACTIVE, GhostHouseState.ACTIVE),
        ],
    )
    def test_release_state_transitions(
        self,
        concrete_ghost: Ghost,
        initial_state: GhostHouseState,
        expected_state: GhostHouseState,
    ) -> None:
        """Test release transitions correctly based on current state."""
        concrete_ghost._house_state = initial_state

        concrete_ghost.release_from_house()

        assert concrete_ghost._house_state == expected_state


class TestGhostReturnToHouse:
    """Test suite for Ghost return_to_house() method."""

    def test_return_resets_all_ghost_state(self, concrete_ghost: Ghost) -> None:
        """Test that return_to_house performs complete reset."""
        spawn_x = concrete_ghost._spawn_position.x
        spawn_y = concrete_ghost._spawn_position.y
        concrete_ghost._position = Position(999.0, 999.0)
        concrete_ghost._house_state = GhostHouseState.ACTIVE
        concrete_ghost._direction = Direction.LEFT

        concrete_ghost.return_to_house()

        assert concrete_ghost._position.x == spawn_x
        assert concrete_ghost._position.y == spawn_y
        assert concrete_ghost._house_state == GhostHouseState.IN_HOUSE
        assert concrete_ghost._direction == Direction.RIGHT
