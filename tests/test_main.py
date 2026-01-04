"""
Basic tests for main module
"""

from pytest_mock import MockerFixture

from src.main import handle_ghost_release, main


def test_ghost_release_logic(mocker: MockerFixture):
    """Tests that ghosts are released at the correct time using pytest-mock."""
    # Create Mocks for all ghosts
    blinky = mocker.Mock()
    pinky = mocker.Mock()
    inky = mocker.Mock()
    clyde = mocker.Mock()

    # Test Frame 1 (Blinky exits immediately)
    handle_ghost_release(1, blinky, pinky, inky, clyde)
    blinky.release_from_house.assert_called_once()
    pinky.release_from_house.assert_not_called()

    # Test Frame 299 (No new exits)
    handle_ghost_release(299, blinky, pinky, inky, clyde)
    pinky.release_from_house.assert_not_called()

    # Test Frame 300 (Pinky exits)
    handle_ghost_release(300, blinky, pinky, inky, clyde)
    pinky.release_from_house.assert_called_once()

    # Test Frame 600 (Inky exits)
    handle_ghost_release(600, blinky, pinky, inky, clyde)
    inky.release_from_house.assert_called_once()

    # Test Frame 900 (Clyde exits)
    handle_ghost_release(900, blinky, pinky, inky, clyde)
    clyde.release_from_house.assert_called_once()


class TestMain:
    """Minimal tests for main function"""

    def test_main_function_exists(self):
        """main function should exist"""
        assert main is not None

    def test_main_is_callable(self):
        """main should be callable"""
        assert callable(main)
