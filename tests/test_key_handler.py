"""Unit tests for key_handler.py"""

# pylint: disable=no-member

import pygame

from src.key_handler import wants_to_pause, wants_to_run


class TestWantsToRun:
    """Class for testing the wants_to_run function"""

    def test_wants_to_run_empty_events(self):
        """Test when events is empty"""
        events = []
        assert wants_to_run(events) is True

    def test_wants_to_run_other_events(self):
        """Test when event is not quit"""
        events = [pygame.event.Event(pygame.MOUSEMOTION)]
        assert wants_to_run(events) is True

    def test_wants_to_run_quit_event(self):
        """Test when event is quit"""
        events = [
            pygame.event.Event(pygame.MOUSEMOTION),
            pygame.event.Event(pygame.QUIT),
        ]
        assert wants_to_run(events) is False


class TestWantsToPause:
    """Class for testing the wants_to_pause function"""

    def test_wants_to_pause_empty_events(self):
        """Test when events is empty"""
        events = []
        assert wants_to_pause(events, True) is True
        assert wants_to_pause(events, False) is False

    def test_wants_to_pause_unrelated_keypress(self):
        """Test when key is not escape"""
        events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
        assert wants_to_pause(events, True) is True
        assert wants_to_pause(events, False) is False

    def test_wants_to_pause_escape_key(self):
        """Test when key is escape"""
        events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
        assert wants_to_pause(events, False) is True
        assert wants_to_pause(events, True) is False
