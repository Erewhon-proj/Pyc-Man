"""Unit tests for highscore module."""

# pylint: disable=redefined-outer-name

import json
import os

import pygame
import pytest

from src.highscore import (
    MAX_SCORES,
    SCORE_FILE,
    _draw_scores,
    input_name_screen,
    load_high_scores,
    save_high_score,
    show_high_scores_screen,
)


@pytest.fixture
def mock_screen(mocker):
    """Mock of the Pygame surface."""
    return mocker.Mock(spec=pygame.Surface)


@pytest.fixture
def mock_clock(mocker):
    """Mock of the Pygame clock."""
    return mocker.Mock(spec=pygame.time.Clock)


def test_load_high_scores_no_file():
    """Test loading when the file does not exist."""
    if os.path.exists(SCORE_FILE):
        os.remove(SCORE_FILE)
    assert load_high_scores() == []


def test_load_high_scores_corrupted_file():
    """Test loading with a corrupted JSON file."""
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        f.write("invalid json")
    assert load_high_scores() == []
    os.remove(SCORE_FILE)


def test_load_high_scores_legacy_compatibility():
    """Test backward compatibility with old scores saved as simple integers."""
    legacy_data = [1000, 500]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f)

    scores = load_high_scores()
    assert len(scores) == 2
    assert scores[0] == {"name": "---", "score": 1000}
    os.remove(SCORE_FILE)


def test_save_high_score_zero_or_negative(mocker, mock_screen, mock_clock):
    """Verify that non-positive scores are not saved."""
    spy = mocker.spy(os.path, "exists")
    save_high_score(mock_screen, mock_clock, 0)
    save_high_score(mock_screen, mock_clock, -10)
    # It shouldn't even attempt to load the files
    assert spy.call_count == 0


def test_input_name_screen_interaction(mocker, mock_screen, mock_clock):
    """Test the name input logic by simulating Pygame events."""

    # Simulate pressing 'A', 'B', 'C' and then 'ENTER'
    mock_events = [
        mocker.Mock(type=pygame.KEYDOWN, key=pygame.K_a, unicode="A"),
        mocker.Mock(type=pygame.KEYDOWN, key=pygame.K_b, unicode="B"),
        mocker.Mock(type=pygame.KEYDOWN, key=pygame.K_c, unicode="C"),
        mocker.Mock(type=pygame.KEYDOWN, key=pygame.K_RETURN),
    ]
    mocker.patch("pygame.font.Font")
    mocker.patch("pygame.event.get", side_effect=[[e] for e in mock_events] + [[]])
    mocker.patch("pygame.display.flip")

    name = input_name_screen(mock_screen, mock_clock, 100)
    assert name == "ABC"


def test_save_high_score_full_list(mocker, mock_screen, mock_clock):
    """Test inserting a record when the list is full."""
    # Create a list of 10 low scores
    initial_scores = [{"name": "OLD", "score": 10} for _ in range(MAX_SCORES)]
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(initial_scores, f)

    # Mock the name input to return "NEW"
    mocker.patch("src.highscore.input_name_screen", return_value="NEW")
    mocker.patch("pygame.display.flip")

    save_high_score(mock_screen, mock_clock, 100)

    saved_scores = load_high_scores()
    assert len(saved_scores) == MAX_SCORES
    assert saved_scores[0]["score"] == 100
    assert saved_scores[0]["name"] == "NEW"
    os.remove(SCORE_FILE)


def test_show_high_scores_back_navigation(mocker, mock_screen, mock_clock):
    """Test the high scores screen and exiting via click."""

    # Mock the BACK button rectangle
    mock_rect = mocker.Mock()
    mock_rect.collidepoint.return_value = True

    # Configure the mocked Font to return mocked Surface, which returns mocked Rect
    mock_font_class = mocker.patch("pygame.font.Font")
    mock_surface = mocker.Mock()
    mock_surface.get_rect.return_value = mock_rect
    mock_font_class.return_value.render.return_value = mock_surface

    # Simulate mouse click
    mocker.patch(
        "pygame.event.get",
        return_value=[mocker.Mock(type=pygame.MOUSEBUTTONDOWN, pos=(0, 0))],
    )
    mocker.patch("pygame.mouse.get_pos", return_value=(0, 0))
    mocker.patch("pygame.display.flip")

    # If it doesn't crash and returns (thanks to the simulated click), the test passes
    show_high_scores_screen(mock_screen, mock_clock)


def test_draw_scores_rendering(mocker, mock_screen):
    """Test the helper function _draw_scores explicitly."""
    mock_font = mocker.Mock(spec=pygame.font.Font)
    mock_surface = mocker.Mock()
    mock_font.render.return_value = mock_surface

    # 1. Test con lista vuota
    _draw_scores(mock_screen, mock_font, [])
    # Verifica che venga renderizzato il testo "No high score yet!"
    mock_font.render.assert_called_with("No high score yet!", True, mocker.ANY)

    # 2. Test con dei punteggi presenti
    mock_font.reset_mock()
    scores = [{"name": "ABC", "score": 500}]
    _draw_scores(mock_screen, mock_font, scores)

    # Verifica che la stringa formatta correttamente il numero, il nome e il punteggio
    expected_str = " 1.      ABC      500"
    mock_font.render.assert_called_with(expected_str, True, mocker.ANY)
    assert mock_screen.blit.call_count > 0
