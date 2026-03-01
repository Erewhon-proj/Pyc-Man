"""
Test suite for PacMan class.
Uses pytest-mock for patching.
"""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pygame
import pytest
from pytest_mock import MockerFixture

from src import settings
from src.direction import Direction
from src.ghost import Ghost
from src.pacman import PacMan


@pytest.fixture
def pacman(mock_game_map):
    """Creates a PacMan instance centered at tile (1, 1)."""
    start_x = 1 * settings.TILE_SIZE + settings.TILE_SIZE / 2
    start_y = 1 * settings.TILE_SIZE + settings.TILE_SIZE / 2
    return PacMan(mock_game_map, start_x, start_y)


def test_initialization(pacman):
    """Tests the initial state of the PacMan object."""
    assert pacman.lives == 3
    assert pacman.score == 0
    assert pacman.direction == Direction.NONE
    assert pacman.powered_up is False
    assert pacman.speed == 2


def test_handle_input(pacman, mocker: MockerFixture):
    """Tests if keyboard input correctly sets next_direction."""
    # Use MagicMock because we need to support __getitem__ (indexing)
    mock_keys = mocker.MagicMock()

    # Simulate pressing UP key
    def get_key(k):
        return k == pygame.K_UP

    mock_keys.__getitem__.side_effect = get_key

    mocker.patch("pygame.key.get_pressed", return_value=mock_keys)

    pacman.handle_input()
    assert pacman.next_direction == Direction.UP


def test_change_direction_valid(pacman):
    """Tests changing direction when the path is clear."""
    pacman.next_direction = Direction.RIGHT

    # Update triggers _try_change_direction
    pacman.update([])

    assert pacman.direction == Direction.RIGHT
    assert pacman.next_direction == Direction.NONE


def test_movement_free(pacman):
    """Tests movement in open space."""
    pacman.direction = Direction.RIGHT
    start_x = pacman.x

    pacman.update([])

    # Should move exactly by 'speed' pixels
    assert pacman.x == start_x + pacman.speed


def test_movement_wall_collision(pacman, mock_game_map):
    """Tests collision with a wall stops movement."""
    pacman.direction = Direction.RIGHT

    # Simulate wall at (2, 1)
    def side_effect_is_walkable(gx, gy):
        if gx == 2 and gy == 1:
            return False
        return True

    mock_game_map.is_walkable.side_effect = side_effect_is_walkable

    # Move towards the wall
    for _ in range(20):
        pacman.update([])

    # Should stop at the center of the current tile (1, 1)
    center_current_tile_x = 1 * settings.TILE_SIZE + settings.TILE_SIZE / 2

    # Allow small float tolerance
    assert abs(pacman.x - center_current_tile_x) < 0.1


def test_tunnel_wrapping(pacman):
    """Tests wrapping around the screen edges."""
    pacman.direction = Direction.LEFT
    pacman.position.x = 0

    pacman.update([])

    expected_x = pacman.game_map.width * settings.TILE_SIZE - 2  # 600 - 2 = 598
    assert pacman.x == expected_x


def test_eat_pellet(pacman, mock_game_map):
    """Tests score increment and pellet removal."""
    # Simulate pellet at current location
    mock_game_map.get_cell.return_value = 2

    pacman.update([])

    assert pacman.score == 10
    mock_game_map.set_cell.assert_called_with(1, 1, 0)


def test_eat_power_pellet(pacman, mock_game_map):
    """Tests power pellet activation."""
    # Simulate power pellet
    mock_game_map.get_cell.return_value = 3

    pacman.update([])

    assert pacman.score == 50
    assert pacman.powered_up is True
    assert pacman.power_up_timer > 0


def test_ghost_collision_death(pacman, mocker: MockerFixture):
    """Tests dying when touching a normal ghost."""
    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    # Specify ghost state
    ghost.is_frightened = False
    ghost.is_eaten = False

    # Suppress print output
    mocker.patch("builtins.print")

    pacman.update([ghost])

    assert pacman.lives == 2
    assert pacman.powered_up is False


def test_ghost_collision_eat_ghost(pacman, mocker: MockerFixture):
    """Tests eating a ghost when powered up."""
    pacman.powered_up = True
    # Ensure timer is > 0
    pacman.power_up_timer = 600

    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False

    # Ghost must be frightened
    ghost.is_frightened = True
    ghost.is_eaten = False

    pacman.update([ghost])

    # Should not die
    assert pacman.lives == 3
    # Eating score
    assert pacman.score == 200
    ghost.get_eaten.assert_called_once()


# Cornering tests


@pytest.mark.parametrize(
    "offset_x,offset_y,expected",
    [
        (0, 0, True),  # Centered
        (7, 0, True),  # Within tolerance
        (0, 7, True),  # Within tolerance
        (7, 7, True),  # Within tolerance diagonally
        (9, 0, False),  # Outside tolerance
        (0, 9, False),  # Outside tolerance
    ],
)
def test_can_turn_tolerance(pacman, offset_x: int, offset_y: int, expected: bool):
    """Tests _can_turn() with various distances from tile center."""
    center_x, center_y = pacman.game_map.grid_to_pixel(1, 1)
    pacman.position.x = center_x + offset_x
    pacman.position.y = center_y + offset_y

    assert pacman._can_turn() == expected


def test_smart_snap_horizontal_to_vertical(pacman):
    """Tests smart snap when turning from horizontal to vertical movement."""
    center_x, center_y = pacman.game_map.grid_to_pixel(1, 1)
    pacman.position.x = center_x + 5
    pacman.position.y = center_y - 3
    pacman.direction = Direction.RIGHT
    pacman.next_direction = Direction.UP

    pacman._try_change_direction()

    assert pacman.position.x == center_x
    assert pacman.position.y == center_y - 3
    assert pacman.direction == Direction.UP


def test_smart_snap_vertical_to_horizontal(pacman):
    """Tests smart snap when turning from vertical to horizontal movement."""
    center_x, center_y = pacman.game_map.grid_to_pixel(1, 1)
    pacman.position.x = center_x - 4
    pacman.position.y = center_y + 6
    pacman.direction = Direction.DOWN
    pacman.next_direction = Direction.RIGHT

    pacman._try_change_direction()

    assert pacman.position.x == center_x - 4
    assert pacman.position.y == center_y
    assert pacman.direction == Direction.RIGHT


def test_reverse_direction_no_snap(pacman):
    """Tests that reversing direction happens immediately without snap."""
    center_x, center_y = pacman.game_map.grid_to_pixel(1, 1)
    pacman.position.x = center_x + 5
    pacman.position.y = center_y + 3
    pacman.direction = Direction.RIGHT
    pacman.next_direction = Direction.LEFT

    pacman._try_change_direction()

    assert pacman.position.x == center_x + 5
    assert pacman.position.y == center_y + 3
    assert pacman.direction == Direction.LEFT


def test_turn_blocked_by_wall(pacman, mock_game_map):
    """Tests that turning is blocked when target tile is not walkable."""
    pacman.direction = Direction.RIGHT
    pacman.next_direction = Direction.UP
    mock_game_map.is_walkable.return_value = False

    pacman._try_change_direction()

    assert pacman.direction == Direction.RIGHT
    assert pacman.next_direction == Direction.UP


# Life System Tests


def test_initial_lives_count(pacman):
    """Tests that Pac-Man starts with correct number of lives."""
    assert pacman.lives == settings.STARTING_LIVES


def test_respawn_position(pacman, mocker: MockerFixture):
    """Tests that Pac-Man respawns at spawn position."""
    original_x = pacman.spawn_position.x
    original_y = pacman.spawn_position.y

    # Move Pac-Man away from spawn
    pacman.position.x = original_x + 100
    pacman.position.y = original_y + 100
    pacman.direction = Direction.RIGHT

    mocker.patch("builtins.print")

    pacman._die()

    assert pacman.x == original_x
    assert pacman.y == original_y
    assert pacman.direction == Direction.NONE


def test_death_timer_activation(pacman, mocker: MockerFixture):
    """Tests that death_timer is set after respawning."""
    mocker.patch("builtins.print")

    pacman._die()

    assert pacman.death_timer == settings.RESPAWN_INVINCIBILITY_FRAMES


def test_invincibility_prevents_death(pacman, mocker: MockerFixture):
    """Tests that Pac-Man cannot die while death_timer is active."""
    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False
    ghost.is_frightened = False
    ghost.is_eaten = False

    mocker.patch("builtins.print")

    # Set death timer to make Pac-Man invincible
    pacman.death_timer = 60

    initial_lives = pacman.lives
    pacman.update([ghost])

    # Should not lose a life
    assert pacman.lives == initial_lives


def test_death_timer_decrements(pacman):
    """Tests that death_timer decreases each frame."""
    pacman.death_timer = 10

    for _ in range(5):
        pacman.update([])

    assert pacman.death_timer == 5


def test_power_up_reset_on_death(pacman, mocker: MockerFixture):
    """Tests that power-up state is reset when Pac-Man dies."""
    pacman.powered_up = True
    pacman.power_up_timer = 300
    pacman.ghost_multiplier = 4

    mocker.patch("builtins.print")

    pacman._die()

    assert pacman.powered_up is False
    assert pacman.power_up_timer == 0
    assert pacman.ghost_multiplier == 1


# Extra Life System Tests


@pytest.mark.parametrize(
    "score,expected_lives",
    [
        (0, 3),  # Starting lives
        (9999, 3),  # Just before threshold
        (10000, 4),  # Exactly one extra life
        (19999, 4),  # Between first and second
        (20000, 5),  # Two extra lives
        (99999, 10),  # Max lives reached
    ],
)
def test_extra_life_by_score(pacman, score: int, expected_lives: int):
    """Tests that extra lives are awarded at correct score thresholds."""
    pacman.score = score
    pacman._check_extra_life()

    expected = min(expected_lives, settings.MAX_LIVES)
    assert pacman.lives == expected


def test_extra_life_max_limit(pacman):
    """Tests that lives cannot exceed settings.MAX_LIVES."""
    pacman.lives = settings.MAX_LIVES
    pacman.score = settings.EXTRA_LIFE_SCORE * 10

    pacman._check_extra_life()

    assert pacman.lives == settings.MAX_LIVES


def test_extra_life_from_pellet(pacman, mock_game_map, mocker: MockerFixture):
    """Tests that eating pellets can trigger extra life."""
    mock_game_map.get_cell.return_value = 2
    mock_game_map.is_walkable.return_value = True

    # Set score just before threshold
    pacman.score = 9990

    # Eat pellet (10 points)
    mocker.patch("builtins.print")
    pacman.update([])

    assert pacman.score == 10000
    assert pacman.lives == 4


def test_extra_life_from_power_pellet(pacman, mock_game_map, mocker: MockerFixture):
    """Tests that eating power pellets can trigger extra life."""
    mock_game_map.get_cell.return_value = 3
    mock_game_map.is_walkable.return_value = True

    pacman.score = 9950

    mocker.patch("builtins.print")
    pacman.update([])

    assert pacman.score == 10000
    assert pacman.lives == 4


def test_extra_life_from_ghost(pacman, mocker: MockerFixture):
    """Tests that eating ghosts can trigger extra life."""
    pacman.score = 9800
    pacman.ghost_multiplier = 1

    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False
    ghost.is_frightened = True
    ghost.is_eaten = False

    pacman.update([ghost])

    assert pacman.score == 10000
    assert pacman.lives == 4


def test_extra_life_only_once_per_threshold(pacman):
    """Tests that extra life is awarded only once per threshold."""
    pacman.score = 10000

    # Call check_extra_life multiple times
    pacman._check_extra_life()
    pacman._check_extra_life()
    pacman._check_extra_life()

    # Should only award one extra life
    assert pacman.lives == 4


# Ghost Multiplier Tests


def test_ghost_multiplier_initial_state(pacman):
    """Tests that ghost multiplier starts at 1."""
    assert pacman.ghost_multiplier == 1


def test_ghost_multiplier_increases(pacman, mocker: MockerFixture):
    """Tests that multiplier doubles after eating each ghost."""
    ghosts = []
    for _ in range(4):
        ghost = mocker.Mock(spec=Ghost)
        ghost.x = pacman.x
        ghost.y = pacman.y
        ghost.in_ghost_house = False
        ghost.is_frightened = True
        ghost.is_eaten = False
        ghosts.append(ghost)

    # Eat first ghost
    pacman.update([ghosts[0]])
    assert pacman.score == settings.GHOST_BASE_SCORE * 1
    assert pacman.ghost_multiplier == 2

    # Eat second ghost
    pacman.update([ghosts[1]])
    assert pacman.score == settings.GHOST_BASE_SCORE * 1 + settings.GHOST_BASE_SCORE * 2
    assert pacman.ghost_multiplier == 4

    # Eat third ghost
    pacman.update([ghosts[2]])
    assert pacman.ghost_multiplier == 8

    # Eat fourth ghost
    pacman.update([ghosts[3]])
    assert pacman.ghost_multiplier == 16


@pytest.mark.parametrize(
    "ghosts_eaten,expected_score,expected_multiplier",
    [
        (1, 200, 2),
        (2, 600, 4),  # 200 + 400
        (3, 1400, 8),  # 200 + 400 + 800
        (4, 3000, 16),  # 200 + 400 + 800 + 1600
    ],
)
def test_ghost_multiplier_progression(
    pacman,
    mocker: MockerFixture,
    ghosts_eaten: int,
    expected_score: int,
    expected_multiplier: int,
):
    """Tests ghost scoring progression with multiple ghosts."""
    ghosts = []
    for _ in range(ghosts_eaten):
        ghost = mocker.Mock(spec=Ghost)
        ghost.x = pacman.x
        ghost.y = pacman.y
        ghost.in_ghost_house = False
        ghost.is_frightened = True
        ghost.is_eaten = False
        ghosts.append(ghost)

    for ghost in ghosts:
        pacman.update([ghost])

    assert pacman.score == expected_score
    assert pacman.ghost_multiplier == expected_multiplier


def test_ghost_multiplier_resets_on_power_pellet_end(pacman):
    """Tests that multiplier resets when power pellet effect ends."""
    pacman.ghost_multiplier = 8
    pacman.powered_up = True
    pacman.power_up_timer = 1

    pacman._update_power_up()

    assert pacman.ghost_multiplier == 1
    assert pacman.powered_up is False


def test_ghost_multiplier_resets_on_new_power_pellet(pacman, mock_game_map):
    """Tests that multiplier resets when eating a new power pellet."""
    pacman.ghost_multiplier = 8
    mock_game_map.get_cell.return_value = 3
    mock_game_map.is_walkable.return_value = True

    pacman.update([])

    assert pacman.ghost_multiplier == 1


# Drawing Tests


def test_draw_score(pacman, mocker: MockerFixture):
    """Tests that score is drawn correctly."""
    screen = mocker.Mock()
    mock_render = mocker.Mock()
    mock_font = mocker.patch(
        "pygame.font.Font", return_value=mocker.Mock(render=mock_render)
    )

    pacman.score = 12345
    pacman.draw_score(screen)

    mock_font.assert_called_once()
    mock_render.assert_called_once()
    screen.blit.assert_called_once()


def test_draw_lives_count(pacman, mocker: MockerFixture):
    """Tests that correct number of life icons are drawn."""
    screen = mocker.MagicMock()
    mock_circle = mocker.patch.object(pygame.draw, "circle")
    mock_polygon = mocker.patch.object(pygame.draw, "polygon")

    pacman.lives = 3
    pacman.draw_lives(screen)

    # Should draw 3 circles (one for each life)
    assert mock_circle.call_count == 3
    # Should draw 3 polygons (mouths)
    assert mock_polygon.call_count == 3


@pytest.mark.parametrize("lives", [1, 2, 3, 5, 10])
def test_draw_lives_various_counts(pacman, mocker: MockerFixture, lives: int):
    """Tests that draw_lives renders correct icon count for various life values."""
    screen = mocker.MagicMock()
    mock_circle = mocker.patch.object(pygame.draw, "circle")
    mocker.patch.object(pygame.draw, "polygon")  # Also patch polygon

    pacman.lives = lives
    pacman.draw_lives(screen)

    assert mock_circle.call_count == lives


def test_draw_zero_lives(pacman, mocker: MockerFixture):
    """Tests that no icons are drawn when lives is 0."""
    screen = mocker.MagicMock()
    mock_circle = mocker.patch.object(pygame.draw, "circle")

    pacman.lives = 0
    pacman.draw_lives(screen)

    mock_circle.assert_not_called()


# Integration Tests


def test_complete_death_and_respawn_cycle(pacman, mocker: MockerFixture):
    """Tests complete cycle: death -> respawn -> invincibility -> vulnerable."""
    ghost = mocker.Mock(spec=Ghost)
    ghost.x = pacman.x
    ghost.y = pacman.y
    ghost.in_ghost_house = False
    ghost.is_frightened = False
    ghost.is_eaten = False

    mocker.patch("builtins.print")

    original_lives = pacman.lives

    # Die
    pacman.update([ghost])
    assert pacman.lives == original_lives - 1
    assert pacman.death_timer == settings.RESPAWN_INVINCIBILITY_FRAMES

    # Try to die again while invincible
    pacman.update([ghost])
    assert pacman.lives == original_lives - 1  # Should not lose another life

    # Wait out invincibility
    for _ in range(settings.RESPAWN_INVINCIBILITY_FRAMES):
        pacman.update([])

    assert pacman.death_timer == 0

    # Now can die again
    pacman.update([ghost])
    assert pacman.lives == original_lives - 2


def test_ghost_scoring_with_extra_life(pacman, mocker: MockerFixture):
    """Tests that eating ghosts both updates score correctly and can trigger extra life."""
    # Set score to be 200 points short of extra life
    pacman.score = 9800
    initial_lives = pacman.lives

    ghosts = []
    for _ in range(2):
        ghost = mocker.Mock(spec=Ghost)
        ghost.x = pacman.x
        ghost.y = pacman.y
        ghost.in_ghost_house = False
        ghost.is_frightened = True
        ghost.is_eaten = False
        ghosts.append(ghost)

    # Eat first ghost (200 points) -> 10000 total
    pacman.update([ghosts[0]])

    assert pacman.score == 10000
    assert pacman.lives == initial_lives + 1
    assert pacman.ghost_multiplier == 2
