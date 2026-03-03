"""
Basic tests for main module
"""

import pygame
import pytest

from src.main import main


class TestMain:
    """Tests for main functions"""

    def test_main_function_exists(self):
        """main function should exist"""
        assert main is not None

    def test_main_is_callable(self):
        """main should be callable"""
        assert callable(main)

    def test_main_play_and_quit(self, mocker):
        """Test starting the game and immediately quitting via pygame event."""
        # Patch external dependencies using the pytest-mock 'mocker' fixture
        mock_pygame = mocker.patch("src.main.pygame")
        mock_menu = mocker.patch("src.main.menu")
        mocker.patch("src.main.GameMap")
        mock_pacman_class = mocker.patch("src.main.PacMan")
        mock_ghost_creation = mocker.patch("src.main.ghost_creation")
        mocker.patch("src.main.handle_ghost_release")
        mock_get_ghost_mode = mocker.patch("src.main.get_ghost_mode")
        mock_set_ghost_modes = mocker.patch("src.main.set_ghost_modes")

        # Break the menu loop by returning "PLAY"
        mock_menu.show_start_screen.side_effect = ["PLAY", KeyboardInterrupt]

        # Setup mock objects for the game loop
        mock_pacman = mocker.MagicMock()
        mock_pacman.lives = 3
        mock_pacman.pellets_eaten = 0
        mock_pacman.score = 0
        mock_pacman.direction.value = (1, 0)
        mock_pacman_class.return_value = mock_pacman

        mock_ghosts = [mocker.MagicMock() for _ in range(4)]
        mock_ghost_creation.return_value = mock_ghosts

        # Simulate a pygame.QUIT event to break the 'while running' loop
        quit_event = mocker.MagicMock()
        quit_event.type = pygame.QUIT
        mock_pygame.event.get.return_value = [quit_event]
        mock_pygame.QUIT = (
            pygame.QUIT
        )  # Ensure the mock constant matches pygame's real constant

        # Simulate a ghost mode change to hit the 'if new_ghost_mode != current_ghost_mode:' block
        mock_get_ghost_mode.return_value = "CHASE"

        # Execute main
        with pytest.raises(KeyboardInterrupt):
         main()

        # Assertions to ensure expected functions were called
        mock_menu.show_start_screen.assert_call_count == 2
        mock_pacman.handle_input.assert_called_once()
        mock_pacman.update.assert_called_once()
        mock_set_ghost_modes.assert_called_once()

    def test_main_high_score_then_play(self, mocker):
        """Test clicking HIGH_SCORE, then PLAY."""
        mock_sys_exit = mocker.patch("src.main.sys.exit")
        mock_pygame = mocker.patch("src.main.pygame")
        mock_menu = mocker.patch("src.main.menu")
        mock_highscore = mocker.patch("src.main.highscore")
        mocker.patch("src.main.GameMap")
        mock_pacman_class = mocker.patch("src.main.PacMan")
        mocker.patch("src.main.ghost_creation")

        # Add integer value for pellets_eaten
        mock_pacman = mocker.MagicMock()
        mock_pacman.pellets_eaten = 0
        mock_pacman.lives = 3
        mock_pacman_class.return_value = mock_pacman

        # Return "HIGH_SCORE" on the first loop iteration, then "PLAY" to break the menu loop
        mock_menu.show_start_screen.side_effect = ["HIGH_SCORE", "PLAY", KeyboardInterrupt]

        # Immediately quit the main game loop
        quit_event = mocker.MagicMock()
        quit_event.type = pygame.QUIT
        mock_pygame.event.get.return_value = [quit_event]
        mock_pygame.QUIT = pygame.QUIT

        with pytest.raises(KeyboardInterrupt):
            main()

        # Verify highscore screen was shown once, but the menu was queried twice
        mock_highscore.show_high_scores_screen.assert_called_once()
        assert mock_menu.show_start_screen.call_count == 3

    def test_main_game_over(self, mocker):
        """Test the game loop exiting when Pacman runs out of lives."""
        mock_print = mocker.patch("builtins.print")
        mock_pygame = mocker.patch("src.main.pygame")
        mock_menu = mocker.patch("src.main.menu")
        mocker.patch("src.main.GameMap")
        mock_pacman_class = mocker.patch("src.main.PacMan")
        mocker.patch("src.main.ghost_creation")
        mocker.patch("src.main.save_high_score")

        mock_menu.show_start_screen.side_effect = ["PLAY", KeyboardInterrupt]

        # Mock empty events so it doesn't quit via pygame.QUIT (running goes to False via lives)
        mock_pygame.event.get.return_value = []

        # Set Pacman's lives to 0 to trigger game over
        mock_pacman = mocker.MagicMock()
        mock_pacman.lives = 0
        mock_pacman.pellets_eaten = 0
        mock_pacman.score = 0
        mock_pacman_class.return_value = mock_pacman

        with pytest.raises(KeyboardInterrupt):
            main()

        # Verify game over was printed and loop ended normally
        mock_print.assert_called_with("Game Over")
