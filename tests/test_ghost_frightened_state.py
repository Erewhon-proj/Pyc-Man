"""Test suite for ghost frightened state functions in Ghost class"""

import pytest
from src.ghost import *


class TestGhostFrightenedState:
    """Test suite for Ghost frightened and eyes-only states."""

    def test_ghost_starts_not_frightened(self, concrete_ghost: Ghost) -> None:
        """Ghost should not start frightened."""
        assert concrete_ghost.is_frightened is False
        assert concrete_ghost.is_eyes_only is False

    def test_set_frightened_activates_state(self, concrete_ghost: Ghost) -> None:
        """Setting frightened should activate frightened state."""
        concrete_ghost.set_frightened(duration=5.0)

        assert concrete_ghost.is_frightened is True
        assert concrete_ghost.is_eyes_only is False
        assert concrete_ghost._frightened_timer == 5.0

    def test_frightened_timer_decreases(self, concrete_ghost: Ghost) -> None:
        """Frightened timer should decrease over time."""
        concrete_ghost.set_frightened(duration=5.0)

        concrete_ghost.update_frightened(delta_time=1.0)

        assert concrete_ghost._frightened_timer == 4.0
        assert concrete_ghost.is_frightened is True

    def test_frightened_ends_when_timer_expires(
        self, concrete_ghost: Ghost
    ) -> None:
        """Ghost should exit frightened state when timer reaches zero."""
        concrete_ghost.set_frightened(duration=1.0)

        concrete_ghost.update_frightened(delta_time=1.5)

        assert concrete_ghost.is_frightened is False
        assert concrete_ghost.is_eyes_only is False
        assert concrete_ghost._frightened_timer == 0.0

    def test_eat_ghost_while_frightened_enters_eyes_only(
        self, concrete_ghost: Ghost
    ) -> None:
        """Eating a frightened ghost should turn it into eyes-only."""
        concrete_ghost.set_frightened(duration=5.0)

        concrete_ghost.on_eaten()

        assert concrete_ghost.is_frightened is False
        assert concrete_ghost.is_eyes_only is True
        assert concrete_ghost._house_state == GhostHouseState.EXITING

    def test_eat_ghost_when_not_frightened_does_nothing(
        self, concrete_ghost: Ghost
    ) -> None:
        """Eating a normal ghost should have no effect."""
        concrete_ghost.on_eaten()

        assert concrete_ghost.is_frightened is False
        assert concrete_ghost.is_eyes_only is False

    def test_eyes_only_returns_to_house(
        self, concrete_ghost: Ghost
    ) -> None:
        """Eyes-only ghost should return to house."""
        concrete_ghost.set_frightened(duration=5.0)
        concrete_ghost.on_eaten()

        concrete_ghost.return_to_house()

        assert concrete_ghost.is_eyes_only is False
        assert concrete_ghost._house_state == GhostHouseState.IN_HOUSE
        assert concrete_ghost._direction == Direction.RIGHT
