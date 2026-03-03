import pytest

from src.game_loop import reset_positions, level_finished, pacman_eaten
from src.direction import Direction
from src.ghost import GhostState, GhostHouseState
from src.settings import GHOST_SPEED, NUM_PELLETS


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
        def __init__(self):
            pass

    game_map = MockGameMap()
    # Spy on the __init__ method to verify it gets called
    mocker.spy(game_map, '__init__')
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

    # Assert Blinky is reset and gets the ACTIVE house state
    mock_ghost_blinky.set_position.assert_called_once_with(20, 20)
    assert mock_ghost_blinky._state == GhostState.SCATTER
    assert mock_ghost_blinky._speed == GHOST_SPEED
    assert mock_ghost_blinky._house_state == GhostHouseState.ACTIVE

    # Assert Inky is reset and gets the IN_HOUSE house state
    mock_ghost_inky.set_position.assert_called_once_with(30, 30)
    assert mock_ghost_inky._state == GhostState.SCATTER
    assert mock_ghost_inky._speed == GHOST_SPEED
    assert mock_ghost_inky._house_state == GhostHouseState.IN_HOUSE


def test_level_finished_not_complete(mocker, mock_pacman, mock_ghost_blinky, mock_game_map):
    """Test behavior when the level is not finished yet (pellets missing)."""
    # Setup: Pac-Man has eaten 1 pellet less than required
    mock_pacman.pellets_eaten = NUM_PELLETS - 1
    timer = 50
    ghosts = [mock_ghost_blinky]

    # Patch reset_positions using pytest-mock
    mock_reset_positions = mocker.patch('src.game_loop.reset_positions')

    # Execute
    result = level_finished(mock_pacman, ghosts, mock_game_map, timer)

    # Assert nothing was reset and the timer remains unchanged
    assert result == 50
    assert mock_pacman.pellets_eaten == NUM_PELLETS - 1
    mock_reset_positions.assert_not_called()
    mock_game_map.__init__.assert_not_called()


def test_level_finished_complete(mocker, mock_pacman, mock_ghost_blinky, mock_game_map):
    """Test behavior when the level is completed (all pellets eaten)."""
    # Setup: Pac-Man has eaten all required pellets
    mock_pacman.pellets_eaten = NUM_PELLETS
    timer = 50
    ghosts = [mock_ghost_blinky]

    # Patch reset_positions using pytest-mock
    mock_reset_positions = mocker.patch('src.game_loop.reset_positions')

    # Execute
    result = level_finished(mock_pacman, ghosts, mock_game_map, timer)

    # Assert everything is reset
    assert result == 0  # Timer is reset to 0
    assert mock_pacman.pellets_eaten == 0  # Pellets are reset
    mock_reset_positions.assert_called_once_with(mock_pacman, ghosts)
    mock_game_map.__init__.assert_called_once()


def test_pacman_eaten_when_dead(mock_pacman, mock_ghost_blinky, mock_ghost_inky):
    """Test behavior when Pac-Man is marked as dead."""
    # Setup: Pac-Man is dead
    mock_pacman.is_dead = True
    ghosts = [mock_ghost_blinky, mock_ghost_inky]

    # Execute
    pacman_eaten(mock_pacman, ghosts)

    # Assert Blinky is reset and gets the ACTIVE house state
    mock_ghost_blinky.set_position.assert_called_once_with(20, 20)
    assert mock_ghost_blinky._state == GhostState.SCATTER
    assert mock_ghost_blinky._speed == GHOST_SPEED
    assert mock_ghost_blinky._house_state == GhostHouseState.ACTIVE

    # Assert Inky is reset and gets the IN_HOUSE house state
    mock_ghost_inky.set_position.assert_called_once_with(30, 30)
    assert mock_ghost_inky._state == GhostState.SCATTER
    assert mock_ghost_inky._speed == GHOST_SPEED
    assert mock_ghost_inky._house_state == GhostHouseState.IN_HOUSE

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