"""Unit tests to test game_loop module"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pytest

from src.direction import Direction
from src.game_loop import (
    level_finished,
    pacman_eaten,
    reset_ghosts_position,
    reset_positions,
)
from src.ghost import GhostHouseState, GhostState
from src.settings import NUM_PELLETS


@pytest.fixture
def mock_pacman(mocker):
    """Provides a mocked PacMan instance with predefined attributes."""
    pacman = mocker.Mock()
    pacman.spawn_position.x = 10
    pacman.spawn_position.y = 15
    pacman.position.x = 5
    pacman.position.y = 5
    pacman.direction = Direction.UP
    pacman.next_direction = Direction.DOWN
    pacman.pellets_eaten = 0
    return pacman


@pytest.fixture
def mock_ghost_blinky(mocker):
    """Provides a mocked Blinky ghost instance to test the 'Blinky' specific branch."""
    ghost = mocker.Mock()
    ghost.name = "Blinky"
    ghost.spawn_position.x = 20
    ghost.spawn_position.y = 20
    return ghost


@pytest.fixture
def mock_ghost_inky(mocker):
    """Provides a mocked Inky ghost instance to test the non-Blinky branch."""
    ghost = mocker.Mock()
    ghost.name = "Inky"
    ghost.spawn_position.x = 30
    ghost.spawn_position.y = 30
    return ghost


@pytest.fixture
def mock_game_map(mocker):
    """Provides a mocked GameMap instance."""

    class MockGameMap:
        """Mocked GameMap instance"""

        def reset(self):
            """Mocked reset function"""
            pass

    game_map = MockGameMap()
    # Spy on the reset method to verify it gets called
    mocker.spy(game_map, "reset")
    return game_map


def test_reset_positions(mock_pacman, mock_ghost_blinky, mock_ghost_inky):
    """Test that resetting positions correctly updates Pac-Man and all ghosts."""
    ghosts = [mock_ghost_blinky, mock_ghost_inky]

    # Execute
    reset_positions(mock_pacman, ghosts)

    # Assert Pac-Man is reset to spawn position and directions are cleared
    assert mock_pacman.position.x == mock_pacman.spawn_position.x
    assert mock_pacman.position.y == mock_pacman.spawn_position.y
    assert mock_pacman.direction == Direction.NONE
    assert mock_pacman.next_direction == Direction.NONE


def test_reset_ghosts_position(mock_ghost_blinky, mock_ghost_inky):
    """Test that resetting positions and states correctly updates all ghosts."""
    ghosts = [mock_ghost_blinky, mock_ghost_inky]

    # Execute
    reset_ghosts_position(ghosts)

    # Assert Blinky is reset and gets the ACTIVE house state
    mock_ghost_blinky.set_position.assert_called_once_with(20, 20)
    mock_ghost_blinky.set_state.assert_called_once_with(GhostState.SCATTER)
    mock_ghost_blinky.set_house_state.assert_called_once_with(GhostHouseState.ACTIVE)
    mock_ghost_blinky.reset_frightened_timer.assert_called_once()

    # Assert Inky is reset and gets the IN_HOUSE house state
    mock_ghost_inky.set_position.assert_called_once_with(30, 30)
    mock_ghost_inky.set_state.assert_called_once_with(GhostState.SCATTER)
    mock_ghost_inky.set_house_state.assert_called_once_with(GhostHouseState.IN_HOUSE)
    mock_ghost_inky.reset_frightened_timer.assert_called_once()


@pytest.mark.parametrize(
    "pellets_eaten, expected_timer, expected_level, should_reset",
    [
        (NUM_PELLETS - 1, 50, 1, False),  # Level not complete
        (NUM_PELLETS, 0, 2, True),  # Level complete
    ],
)
# pylint: disable=too-many-positional-arguments
def test_level_finished(
    mocker,
    mock_pacman,
    mock_ghost_blinky,
    mock_game_map,
    pellets_eaten,
    expected_timer,
    expected_level,
    should_reset,
):
    """Test level_finished behavior based on pellets eaten."""
    # Setup
    mock_pacman.pellets_eaten = pellets_eaten
    timer = 50
    level = 1
    ghosts = [mock_ghost_blinky]

    # Patch reset_positions using pytest-mock
    mock_reset_positions = mocker.patch("src.game_loop.reset_positions")

    # Execute
    result_timer, result_level = level_finished(
        mock_pacman, ghosts, mock_game_map, timer, level
    )

    # Assert
    assert result_timer == expected_timer
    assert result_level == expected_level
    if should_reset:
        assert mock_pacman.pellets_eaten == 0
        mock_reset_positions.assert_called_once_with(mock_pacman, ghosts)
        mock_game_map.reset.assert_called_once()
    else:
        assert mock_pacman.pellets_eaten == pellets_eaten
        mock_reset_positions.assert_not_called()
        mock_game_map.reset.assert_not_called()


def test_pacman_eaten_when_dead(mock_pacman, mock_ghost_blinky, mock_ghost_inky):
    """Test behavior when Pac-Man is marked as dead."""
    # Setup: Pac-Man is dead
    mock_pacman.is_dead = True
    ghosts = [mock_ghost_blinky, mock_ghost_inky]

    # Execute
    pacman_eaten(mock_pacman, ghosts)

    # Assert Blinky is reset and gets the ACTIVE house state
    mock_ghost_blinky.set_position.assert_called_once_with(20, 20)
    mock_ghost_blinky.set_state.assert_called_once_with(GhostState.SCATTER)
    mock_ghost_blinky.set_house_state.assert_called_once_with(GhostHouseState.ACTIVE)
    mock_ghost_blinky.reset_frightened_timer.assert_called_once()

    # Assert Inky is reset and gets the IN_HOUSE house state
    mock_ghost_inky.set_position.assert_called_once_with(30, 30)
    mock_ghost_inky.set_state.assert_called_once_with(GhostState.SCATTER)
    mock_ghost_inky.set_house_state.assert_called_once_with(GhostHouseState.IN_HOUSE)
    mock_ghost_inky.reset_frightened_timer.assert_called_once()

    # Assert Pac-Man is revived (is_dead set to False)
    assert mock_pacman.is_dead is False


def test_pacman_eaten_when_alive(mock_pacman, mock_ghost_blinky, mock_ghost_inky):
    """Test behavior when Pac-Man is not dead (should do nothing to ghosts)."""
    # Setup: Pac-Man is alive
    mock_pacman.is_dead = False
    ghosts = [mock_ghost_blinky, mock_ghost_inky]

    # Execute
    pacman_eaten(mock_pacman, ghosts)

    # Assert ghosts are NOT reset
    mock_ghost_blinky.set_position.assert_not_called()
    mock_ghost_inky.set_position.assert_not_called()

    # Assert Pac-Man remains alive
    assert mock_pacman.is_dead is False
