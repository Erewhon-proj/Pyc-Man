"""Unit tests for pause.py module"""

import pygame

from src.pause import pause
from src.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WHITE


def test_pause_is_true(mocker):
    """Unit test for pause function when is_paused is True"""

    # Arrange: Mock the pygame Surface and the font module
    mock_screen = mocker.Mock(spec=pygame.Surface)

    mock_font = mocker.Mock()
    mock_text_surface = mocker.Mock()
    mock_rect = mocker.Mock()

    # Set up the mock chain: SysFont() -> render() -> get_rect()
    mock_sysfont = mocker.patch("pygame.font.SysFont", return_value=mock_font)
    mock_font.render.return_value = mock_text_surface
    mock_text_surface.get_rect.return_value = mock_rect

    # Act
    pause(True, mock_screen)

    # Assert
    mock_sysfont.assert_called_once_with(None, 72)
    mock_font.render.assert_called_once_with("PAUSE", True, WHITE)
    mock_text_surface.get_rect.assert_called_once_with(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    )
    mock_screen.blit.assert_called_once_with(mock_text_surface, mock_rect)


def test_pause_is_false(mocker):
    """Unit test for pause function when is_paused is False"""
    # Arrange
    mock_screen = mocker.Mock(spec=pygame.Surface)
    mock_sysfont = mocker.patch("pygame.font.SysFont")

    # Act
    pause(False, mock_screen)

    # Assert: If not paused, no fonts should be initialized and nothing blitted
    mock_sysfont.assert_not_called()
    mock_screen.blit.assert_not_called()
