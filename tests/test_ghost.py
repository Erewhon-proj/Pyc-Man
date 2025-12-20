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
        assert concrete_ghost._direction == Direction.RIGHT.value

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
