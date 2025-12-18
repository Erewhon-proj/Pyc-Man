"""
Test suite for GameMap class
"""

# pylint: disable=redefined-outer-name

import pytest

from src.game_map import GameMap


@pytest.fixture
def game_map():
    """Provide a fresh GameMap instance for each test"""
    return GameMap()


class TestGameMap:
    """Test suite for GameMap class"""

    def test_layout_is_not_empty(self, game_map):
        """Game map layout should not be empty"""
        assert len(game_map.layout) > 0
        assert len(game_map.layout[0]) > 0

    def test_initial_pellet_count(self, game_map):
        """Initial pellet count should match layout"""
        pellet_count = sum(cell in (2, 3) for row in game_map.layout for cell in row)

        assert game_map.initial_pellets == pellet_count

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (0, 0, True),  # Wall
            (1, 1, False),  # Power pellet
            (2, 1, False),  # Pellet
            (9, 1, True),  # Wall
        ],
    )
    def test_is_wall(self, game_map, x, y, expected):
        """Test wall detection"""
        assert game_map.is_wall(x, y) == expected

    def test_is_wall_out_of_bounds(self, game_map):
        """Out-of-bounds positions should be walls"""
        assert game_map.is_wall(-1, 0)
        assert game_map.is_wall(0, -1)
        assert game_map.is_wall(999, 999)

    def test_get_cell(self, game_map):
        """Test retrieving a cell value"""
        value = game_map.get_cell(1, 1)
        assert value in (0, 1, 2, 3)

    def test_get_cell_out_of_bounds_returns_wall(self, game_map):
        """Out-of-bounds get_cell should return wall"""
        assert game_map.get_cell(-1, 0) == 1
        assert game_map.get_cell(0, 999) == 1

    def test_set_cell_changes_value(self, game_map):
        """Setting a cell should update the layout"""
        game_map.set_cell(1, 1, 0)
        assert game_map.get_cell(1, 1) == 0

    def test_set_cell_out_of_bounds_does_nothing(self, game_map):
        """Setting out-of-bounds should not crash"""
        game_map.set_cell(-1, -1, 0)
