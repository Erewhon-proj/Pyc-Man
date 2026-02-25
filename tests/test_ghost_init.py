"""
Tests for ghost_init.py
"""

from pytest_mock import MockerFixture

from src.ghost import GhostState
from src.ghost_init import (
    get_ghost_mode,
    ghost_creation,
    handle_ghost_release,
    set_ghost_modes,
)


def test_ghost_release_logic(mocker: MockerFixture):
    """Tests that ghosts are released at the correct time using pytest-mock.

    New behavior:
    - Blinky: starts free (not in this function anymore)
    - Pinky: exits after 60 frames (1 second)
    - Inky: exits after 30 pellets eaten
    - Clyde: exits after 60 pellets eaten
    """
    # Create Mocks for ghosts (no blinky anymore)
    pinky = mocker.Mock()
    inky = mocker.Mock()
    clyde = mocker.Mock()

    # Test Frame 59, 0 pellets (No exits yet)
    handle_ghost_release(0, 59, pinky, inky, clyde)
    pinky.release_from_house.assert_not_called()

    # Test Frame 60, 0 pellets (Pinky exits)
    handle_ghost_release(0, 60, pinky, inky, clyde)
    pinky.release_from_house.assert_called_once()

    # Test Frame 100, 29 pellets (No Inky yet)
    handle_ghost_release(29, 100, pinky, inky, clyde)
    inky.release_from_house.assert_not_called()

    # Test Frame 100, 30 pellets (Inky exits)
    handle_ghost_release(30, 100, pinky, inky, clyde)
    inky.release_from_house.assert_called_once()

    # Test Frame 100, 59 pellets (No Clyde yet)
    handle_ghost_release(59, 100, pinky, inky, clyde)
    clyde.release_from_house.assert_not_called()

    # Test Frame 100, 60 pellets (Clyde exits)
    handle_ghost_release(60, 100, pinky, inky, clyde)
    clyde.release_from_house.assert_called_once()


def test_get_ghost_mode(mocker):
    """Verify the switch between SCATTER and CHASE based on cycles defined in settings."""
    # Mocking cycles constant in the ghost_init module
    mock_cycles = [("SCATTER", 7), ("CHASE", 20), ("SCATTER", 5), ("CHASE", -1)]
    mocker.patch("src.ghost_init.GHOST_MODE_CYCLES", mock_cycles)

    # At the beginning (timer < 7)
    assert get_ghost_mode(5) == "SCATTER"
    # After the first scatter (7 < timer < 27)
    assert get_ghost_mode(10) == "CHASE"
    # During the second scatter (timer > 27)
    assert get_ghost_mode(30) == "SCATTER"
    # Permanent mode (-1)
    assert get_ghost_mode(1000) == "CHASE"


def test_set_ghost_modes(mocker: MockerFixture):
    """Verify that the state is only changed for eligible ghosts."""
    # Create mocks for ghosts with different conditions
    active_ghost = mocker.Mock()
    active_ghost.is_frightened = False
    active_ghost.is_eaten = False
    active_ghost.in_ghost_house = False

    restricted_ghost = mocker.Mock()
    restricted_ghost.is_frightened = True  # This one should not change state

    ghosts = [active_ghost, restricted_ghost]

    # Change from SCATTER to CHASE (mode_changed will be True)
    set_ghost_modes(ghosts, mode="CHASE", previous_mode="SCATTER")

    # The active ghost should change state and reverse direction
    active_ghost.set_state.assert_called_with(GhostState.CHASE, reverse_direction=True)
    # The frightened ghost should be skipped
    restricted_ghost.set_state.assert_not_called()


def test_ghost_creation(mocker: MockerFixture):
    """Verify that all 4 ghosts are created with the correct configuration."""
    mock_map = mocker.Mock()
    # Mock TILE_SIZE to simplify calculations and avoid dependency on settings.py
    mocker.patch("src.ghost_init.TILE_SIZE", 16)

    # Mocking ghosts
    mock_blinky = mocker.patch("src.ghost_init.Blinky")
    mock_inky = mocker.patch("src.ghost_init.Inky")
    mocker.patch("src.ghost_init.Pinky")
    mocker.patch("src.ghost_init.Clyde")

    ghosts = ghost_creation(mock_map)

    assert len(ghosts) == 4
    mock_blinky_instance = mock_blinky.return_value

    args, _ = mock_inky.call_args
    assert args[3] == mock_blinky_instance
