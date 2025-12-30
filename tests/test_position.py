"""
Test suite for Position class.
"""

import pytest

from src.position import Position
from src.settings import TILE_SIZE


class TestPosition:
    """Test suite for Position class."""

    def test_initialization(self):
        """Test Position initialization with coordinates."""
        x, y = 10.5, 20.0

        pos = Position(x, y)

        assert pos.x == x
        assert pos.y == y

    def test_copy_creates_new_instance(self):
        """Test that copy creates a new independent instance."""
        original = Position(5, 5)

        copy = original.copy()

        assert copy is not original
        assert copy.x == original.x
        assert copy.y == original.y

    @pytest.mark.parametrize(
        "x, y, expected_grid",
        [
            (0, 0, (0, 0)),  # Origin
            (TILE_SIZE, TILE_SIZE * 2, (1, 2)),  # Exact boundaryi
            (TILE_SIZE * 1.5, TILE_SIZE * 2.7, (1, 2)),  # Internal offset
            (TILE_SIZE * 5, TILE_SIZE * 10, (5, 10)),  # Large numbersmi sm
        ],
    )
    def test_to_grid_conversion(self, x, y, expected_grid):
        """Test pixel to grid coordinate conversion."""
        pos = Position(x, y)

        grid_coords = pos.to_grid()

        assert grid_coords == expected_grid

    @pytest.mark.parametrize(
        "x, y, expected_center",
        [
            (0, 0, (TILE_SIZE / 2, TILE_SIZE / 2)),
            (100, 100, (100 + TILE_SIZE / 2, 100 + TILE_SIZE / 2)),
            (
                TILE_SIZE,
                TILE_SIZE * 2,
                (TILE_SIZE + TILE_SIZE / 2, TILE_SIZE * 2 + TILE_SIZE / 2),
            ),
        ],
    )
    def test_get_center(self, x, y, expected_center):
        """Test calculation of tile center point."""
        pos = Position(x, y)

        center = pos.get_center()

        assert center == expected_center

    @pytest.mark.parametrize(
        "pos1, pos2, expected_distance",
        [
            # Same position
            (Position(10, 10), Position(10, 10), 0.0),
            # Horizontal (1 tile distance)
            (Position(0, 0), Position(TILE_SIZE, 0), float(TILE_SIZE)),
            # Vertical
            (Position(0, 0), Position(0, TILE_SIZE), float(TILE_SIZE)),
            # Diagonal (3-4-5 triangle) - Distance: 50
            (Position(0, 0), Position(30, 40), 50.0),
        ],
    )
    def test_distance_to(self, pos1, pos2, expected_distance):
        """Test distance calculation between two positions."""
        dist = pos1.distance_to(pos2)

        assert dist == pytest.approx(expected_distance)

    def test_distance_symmetry(self):
        """Test that distance calculation is symmetric."""
        p1 = Position(10, 20)
        p2 = Position(50, 80)

        dist_1_to_2 = p1.distance_to(p2)
        dist_2_to_1 = p2.distance_to(p1)

        assert dist_1_to_2 == pytest.approx(dist_2_to_1)
