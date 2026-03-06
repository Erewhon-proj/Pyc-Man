"""
Tests for ghost_init.py
"""

from dataclasses import dataclass

import pytest
from pytest_mock import MockerFixture

from src.ghost import GhostState
from src.ghost_init import (
    get_ghost_mode,
    ghost_creation,
    handle_ghost_release,
    set_ghost_modes,
)


@dataclass
class GhostReleaseTestCase:
    """Test case for ghost release timing."""

    pellets: int
    timer: int
    pinky_should_release: bool
    inky_should_release: bool
    clyde_should_release: bool


@pytest.mark.parametrize(
    "test_case",
    [
        GhostReleaseTestCase(0, 59, False, False, False),  # No exits yet
        GhostReleaseTestCase(0, 60, True, False, False),  # Pinky exits
        GhostReleaseTestCase(29, 100, True, False, False),  # No Inky yet
        GhostReleaseTestCase(30, 100, True, True, False),  # Inky exits
        GhostReleaseTestCase(59, 100, True, True, False),  # No Clyde yet
        GhostReleaseTestCase(60, 100, True, True, True),  # Clyde exits
    ],
)
def test_ghost_release_logic(
    mocker: MockerFixture, test_case: GhostReleaseTestCase
) -> None:
    """Tests that ghosts are released at the correct time."""
    # Create Mocks for ghosts
    blinky = mocker.Mock()
    pinky = mocker.Mock()
    inky = mocker.Mock()
    clyde = mocker.Mock()
    ghosts = [blinky, pinky, inky, clyde]

    handle_ghost_release(test_case.pellets, test_case.timer, ghosts)

    if test_case.pinky_should_release:
        pinky.release_from_house.assert_called_once()
    else:
        pinky.release_from_house.assert_not_called()

    if test_case.inky_should_release:
        inky.release_from_house.assert_called_once()
    else:
        inky.release_from_house.assert_not_called()

    if test_case.clyde_should_release:
        clyde.release_from_house.assert_called_once()
    else:
        clyde.release_from_house.assert_not_called()


def test_get_ghost_mode(mocker):
    """Verify the switch between SCATTER and CHASE based on cycles defined in settings."""
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
    restricted_ghost.is_frightened = True

    ghosts = [active_ghost, restricted_ghost]

    # Change from SCATTER to CHASE
    set_ghost_modes(ghosts, mode="CHASE", previous_mode="SCATTER")
    active_ghost.set_state.assert_called_with(GhostState.CHASE, reverse_direction=True)
    restricted_ghost.set_state.assert_not_called()


def test_ghost_creation(mocker: MockerFixture):
    """Verify that all 4 ghosts are created with the correct configuration."""
    mock_map = mocker.Mock()
    mocker.patch("src.ghost_init.TILE_SIZE", 16)
    mock_blinky = mocker.patch("src.ghost_init.Blinky")
    mock_inky = mocker.patch("src.ghost_init.Inky")
    mocker.patch("src.ghost_init.Pinky")
    mocker.patch("src.ghost_init.Clyde")

    ghosts = ghost_creation(mock_map)

    assert len(ghosts) == 4
    mock_blinky_instance = mock_blinky.return_value

    args, _ = mock_inky.call_args
    assert args[3] == mock_blinky_instance
