"""
Shared fixtures for pytest.
This file must be named conftest.py for pytest to discover fixtures automatically.
"""

import pytest
from pytest_mock import MockerFixture

from src.game_map import GameMap
from src.settings import TILE_SIZE


@pytest.fixture
def mock_game_map(mocker: MockerFixture):
    """Creates a mock game map for testing using pytest-mock."""
    m = mocker.Mock(spec=GameMap)

    # Configura attributi base
    m.width = 20
    m.height = 20

    # Default: tutto è camminabile
    m.is_walkable.return_value = True

    # Mock grid_to_pixel per restituire il centro esatto della tile
    m.grid_to_pixel.side_effect = lambda gx, gy: (
        gx * TILE_SIZE + TILE_SIZE / 2,
        gy * TILE_SIZE + TILE_SIZE / 2,
    )

    # Mock pixel_to_grid
    m.pixel_to_grid.side_effect = lambda px, py: (
        int(px // TILE_SIZE),
        int(py // TILE_SIZE),
    )

    # Default: cella vuota
    m.get_cell.return_value = 0

    return m
