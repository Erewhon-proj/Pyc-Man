"""Unit tests for the menu module."""

# pylint: disable=redefined-outer-name


import pygame
import pytest

from src.menu import show_start_screen
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame and its font module before each test to avoid errors."""
    pygame.init()
    # Set a hidden display to allow font rendering without popping up a window
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()


@pytest.fixture
def mock_game_elements(mocker):
    """Fixture to mock game elements like Map, PacMan and Ghosts to avoid loading assets."""
    mocker.patch("src.menu.GameMap")
    mock_pacman = mocker.patch("src.menu.PacMan").return_value
    mock_pacman.y = 100  # Mock arbitrary y-coordinate for ghost drawing

    mock_ghost = mocker.MagicMock()
    mocker.patch("src.menu.ghost_creation", return_value=[mock_ghost])

    return mock_pacman, mock_ghost


def test_show_start_screen_play(mocker, mock_game_elements):
    """Test clicking the PLAY button and the hover effect."""
    # pylint: disable=unused-argument
    _, mock_ghost = mock_game_elements
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Calculate the exact center where the PLAY button is located
    play_button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    # Frame 1: Empty event queue (allows testing hover logic and rendering)
    # Frame 2: Mouse click event on the PLAY button
    event_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=play_button_pos)
    mocker.patch("pygame.event.get", side_effect=[[], [event_click]])

    # Simulate mouse hovering over the PLAY button to trigger YELLOW text color
    mocker.patch("pygame.mouse.get_pos", return_value=play_button_pos)

    # Execute the function
    result = show_start_screen(screen, clock)

    # Assertions
    assert result == "PLAY"
    mock_ghost.draw_on_menu.assert_called()  # Verify ghost loop is covered


@pytest.mark.usefixtures("mock_game_elements")
def test_show_start_screen_high_scores(mocker):
    """Test clicking the HIGH SCORES button."""
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Calculate the exact center where the HIGH SCORES button is located
    scores_button_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)

    # Simulate empty events for one frame, then a click on the HIGH SCORES button
    event_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=scores_button_pos)
    mocker.patch("pygame.event.get", side_effect=[[], [event_click]])

    # Simulate mouse hovering over HIGH SCORES
    mocker.patch("pygame.mouse.get_pos", return_value=scores_button_pos)

    # Execute the function
    result = show_start_screen(screen, clock)

    # Assertions
    assert result == "HIGH_SCORE"


def test_show_start_screen_quit(mocker, mock_game_elements):
    """Test that clicking the close window button (QUIT) exits the game."""
    # pylint: disable=unused-argument
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Simulate a QUIT event
    event_quit = pygame.event.Event(pygame.QUIT)
    mocker.patch("pygame.event.get", return_value=[event_quit])

    # Mock sys.exit to raise a SystemExit exception so it doesn't kill pytest
    mock_sys_exit = mocker.patch("src.utils.sys.exit", side_effect=SystemExit)
    mock_pygame_quit = mocker.patch("src.utils.pygame.quit")

    # Assert that calling the menu function raises SystemExit
    with pytest.raises(SystemExit):
        show_start_screen(screen, clock)

    # Verify that pygame.quit() and sys.exit() were called correctly
    mock_pygame_quit.assert_called_once()
    mock_sys_exit.assert_called_once()
