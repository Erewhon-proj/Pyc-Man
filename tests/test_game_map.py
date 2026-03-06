"""
Test suite for GameMap class
"""

# pylint: disable=redefined-outer-name
# pylint: disable=too-many-positional-arguments
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-public-methods

import pygame
import pytest

from src.game_map import GameMap


@pytest.fixture
def game_map():
    """Provide a fresh GameMap instance for each test"""
    return GameMap()


@pytest.fixture
def mock_screen(mocker):
    """Provide a mocked Pygame surface"""
    return mocker.Mock(spec=pygame.Surface)


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

    @pytest.mark.parametrize(
        "pixel_x, pixel_y, expected_grid_x, expected_grid_y",
        [
            (0, 0, 0, 0),
            (30, 30, 1, 1),
            (45, 60, 1, 2),
            (150, 150, 5, 5),
        ],
    )
    def test_pixel_to_grid(
        self, game_map, pixel_x, pixel_y, expected_grid_x, expected_grid_y
    ):
        """Test conversion from pixel to grid coordinates"""
        grid_x, grid_y = game_map.pixel_to_grid(pixel_x, pixel_y)
        assert grid_x == expected_grid_x
        assert grid_y == expected_grid_y

    @pytest.mark.parametrize(
        "grid_x, grid_y, expected_pixel_x, expected_pixel_y",
        [
            (0, 0, 15.0, 15.0),
            (1, 1, 45.0, 45.0),
            (5, 5, 165.0, 165.0),
        ],
    )
    def test_grid_to_pixel(
        self, game_map, grid_x, grid_y, expected_pixel_x, expected_pixel_y
    ):
        """Test conversion from grid to pixel coordinates (center)"""
        pixel_x, pixel_y = game_map.grid_to_pixel(grid_x, grid_y)
        assert pixel_x == expected_pixel_x
        assert pixel_y == expected_pixel_y

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (0, 0, False),  # Wall - not walkable
            (1, 1, True),  # Power pellet - walkable
            (2, 1, True),  # Pellet - walkable
            (9, 1, False),  # Wall - not walkable
        ],
    )
    def test_is_walkable(self, game_map, x, y, expected):
        """Test walkability detection"""
        assert game_map.is_walkable(x, y) == expected

    def test_height_property(self, game_map):
        """Test height property returns number of rows"""
        assert game_map.height == len(game_map.layout)
        assert game_map.height == 22

    def test_width_property(self, game_map):
        """Test width property returns number of columns"""
        assert game_map.width == len(game_map.layout[0])
        assert game_map.width == 19

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (0, 0, True),  # Normal wall -> visual wall
            (1, 1, False),  # Empty space or pellet -> not a visual wall
            (-1, 10, False),  # Left tunnel out of bounds-> open path (False)
            (19, 10, False),  # Right Tunnel out of bounds -> open path (False)
        ],
    )
    def test_is_visual_wall(self, game_map, x, y, expected):
        """Test the special logic for wall rendering in tunnels"""
        # Using _ to access a protected method for testing internal logic
        # pylint: disable=protected-access
        assert game_map._is_visual_wall(x, y) == expected

    def test_initial_pellet_count_logic(self, game_map):
        """Verify that the counting logic used by _draw_pellets is consistent"""
        # Count how many cells in the layout are 2 (pellet) or 3 (power pellet)
        cells_with_pellets = sum(
            1 for row in game_map.layout for cell in row if cell in (2, 3)
        )
        assert game_map.initial_pellets == cells_with_pellets

    def test_draw(self, game_map, mocker, mock_screen):
        """Test that draw coordinates the main rendering methods."""
        mock_draw_walls = mocker.patch.object(game_map, "_draw_walls")
        mock_draw_pellets = mocker.patch.object(game_map, "_draw_pellets")

        game_map.draw(mock_screen)

        mock_draw_walls.assert_called_once_with(mock_screen)
        mock_draw_pellets.assert_called_once_with(mock_screen)

    def test_draw_clipped_corner(self, game_map, mocker, mock_screen):
        """Test the clipped corner rendering bounds and logic."""
        mock_circle = mocker.patch("pygame.draw.circle")

        clip_rect = (0, 0, 10, 10)
        center = (5, 5)

        game_map._draw_clipped_corner(
            mock_screen, clip_rect, center, radius=8, thickness=2
        )

        assert mock_screen.set_clip.call_count == 2
        mock_screen.set_clip.assert_called_with(None)
        mock_circle.assert_called_once()

    def test_draw_walls_coverage(self, game_map, mocker, mock_screen):
        """Test _draw_walls executes completely over the map and calls rendering internals."""
        mocker.patch("pygame.draw.line")
        mocker.patch("pygame.draw.circle")

        # Traverse the entire default layout map layout and trigger all _draw_cell_walls branches
        game_map._draw_walls(mock_screen)

    @pytest.mark.parametrize(
        "boundary, expected_line_calls, expected_clipped_calls",
        [
            ((True, True, False, False), 1, 0),  # b_n, b_s
            ((False, False, True, True), 1, 0),  # b_e, b_w
            ((True, False, True, False), 0, 1),  # b_n, b_e
            ((True, False, False, True), 0, 1),  # b_n, b_w
            ((False, True, True, False), 0, 1),  # b_s, b_e
            ((False, True, False, True), 0, 1),  # b_s, b_w
            ((False, False, False, False), 0, 0),  # No boundary fallback
        ],
    )
    def test_draw_corner(
        self,
        game_map,
        mocker,
        mock_screen,
        boundary,
        expected_line_calls,
        expected_clipped_calls,
    ):
        """Test explicit branching combinations mapped inside _draw_corner."""
        mock_line = mocker.patch("pygame.draw.line")
        mock_clipped = mocker.patch.object(game_map, "_draw_clipped_corner")

        game_map._draw_corner(mock_screen, (10, 10), boundary, r=8, thickness=2)

        assert mock_line.call_count == expected_line_calls
        assert mock_clipped.call_count == expected_clipped_calls

    @pytest.mark.parametrize(
        "boundary, expected_line_calls",
        [
            ((True, False, False, False), 1),
            ((False, True, False, False), 1),
            ((False, False, True, False), 1),
            ((False, False, False, True), 1),
            ((True, True, True, True), 4),
            ((False, False, False, False), 0),
        ],
    )
    def test_draw_dead_end(
        self, game_map, mocker, mock_screen, boundary, expected_line_calls
    ):
        """Test explicit branching connections mapped inside _draw_dead_end."""
        mock_line = mocker.patch("pygame.draw.line")
        game_map._draw_dead_end(mock_screen, (10, 10), boundary, r=8, thickness=2)
        assert mock_line.call_count == expected_line_calls

    def test_draw_pellets(self, game_map, mocker, mock_screen):
        """Test pellet rendering and pulse math calculations."""
        mock_circle = mocker.patch("pygame.draw.circle")
        mocker.patch("pygame.time.get_ticks", return_value=1000)

        # Manually calculate number of standard and power pellets in the test matrix
        pellets = sum(1 for row in game_map.layout for cell in row if cell == 2)
        power_pellets = sum(1 for row in game_map.layout for cell in row if cell == 3)

        game_map._draw_pellets(mock_screen)

        # Standard pellets draw exactly 1 circle while Power Pellets draw 2
        expected_calls = pellets + (power_pellets * 2)
        assert mock_circle.call_count == expected_calls
