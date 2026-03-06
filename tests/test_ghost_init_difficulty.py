"""Test suite for ghost_init module with difficulty system integration."""

# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import pytest

from src.difficulty import DifficultyManager
from src.game_map import GameMap
from src.ghost_init import get_ghost_mode, ghost_creation
from src.settings import GHOST_MODE_CYCLES


class TestGhostInitDifficultyIntegration:
    """Test suite for ghost_init difficulty system integration."""

    @pytest.fixture
    def difficulty_manager_level_1(self):
        """Provide DifficultyManager for level 1."""
        return DifficultyManager(level=1)

    @pytest.fixture
    def difficulty_manager_level_3(self):
        """Provide DifficultyManager for level 3."""
        return DifficultyManager(level=3)

    @pytest.fixture
    def difficulty_manager_level_5(self):
        """Provide DifficultyManager for level 5."""
        return DifficultyManager(level=5)

    # --- get_ghost_mode Tests with Difficulty ---

    def test_get_ghost_mode_level_1_uses_default_cycles(
        self, difficulty_manager_level_1
    ):
        """Test that level 1 uses default ghost mode cycles."""
        mode = get_ghost_mode(0, difficulty_manager_level_1)
        assert mode == "SCATTER"

    def test_get_ghost_mode_level_1_progression(self, difficulty_manager_level_1):
        """Test ghost mode progression at level 1."""
        mode_at_start = get_ghost_mode(0, difficulty_manager_level_1)
        assert mode_at_start == "SCATTER"

        mode_after_7_seconds = get_ghost_mode(420, difficulty_manager_level_1)
        assert mode_after_7_seconds == "CHASE"

    def test_get_ghost_mode_without_difficulty_manager(self):
        """Test that get_ghost_mode works without difficulty manager."""
        mode = get_ghost_mode(0)
        assert mode == "SCATTER"

    def test_get_ghost_mode_high_level_reduces_scatter(
        self, difficulty_manager_level_5
    ):
        """Test that high levels reduce SCATTER duration."""
        # At level 5, SCATTER should be reduced significantly
        mode_at_start = get_ghost_mode(0, difficulty_manager_level_5)
        assert mode_at_start == "SCATTER"
        mode_after_short_time = get_ghost_mode(
            180, difficulty_manager_level_5
        )  # 3 seconds
        # At level 5, SCATTER is reduced from 7s to 3s, so at 3s should already be in CHASE
        assert mode_after_short_time == "CHASE"

    def test_get_ghost_mode_preserves_permanent_mode(self, difficulty_manager_level_5):
        """Test that permanent CHASE mode is preserved at high levels."""
        # Get total duration of all cycles except last
        total_duration = sum(d for _, d in GHOST_MODE_CYCLES if d > 0)

        # After all cycles, should be in permanent CHASE
        mode = get_ghost_mode(total_duration + 1000, difficulty_manager_level_5)
        assert mode == "CHASE"

    # --- Ghost Creation with Difficulty ---

    def test_ghost_creation_with_difficulty_manager(self, difficulty_manager_level_1):
        """Test that ghost_creation passes difficulty manager to ghosts."""
        game_map = GameMap()
        ghosts = ghost_creation(game_map, difficulty_manager_level_1)

        assert len(ghosts) == 4
        # All ghosts should have difficulty manager set
        for ghost in ghosts:
            assert ghost._difficulty_manager is not None
            assert ghost._difficulty_manager.level == 1

    def test_ghost_creation_without_difficulty_manager(self):
        """Test that ghost_creation works without difficulty manager."""
        game_map = GameMap()
        ghosts = ghost_creation(game_map)

        assert len(ghosts) == 4
        # Ghosts should have None as difficulty manager
        for ghost in ghosts:
            assert ghost._difficulty_manager is None

    def test_ghost_creation_high_level_ghosts(self, difficulty_manager_level_5):
        """Test that high level ghosts have correct difficulty settings."""
        game_map = GameMap()
        ghosts = ghost_creation(game_map, difficulty_manager_level_5)

        # All ghosts should have level 5 difficulty manager
        for ghost in ghosts:
            assert ghost._difficulty_manager.level == 5
            # Speed should be at maximum (plateau)
            assert ghost._speed == 2.0

    # --- Integration Tests for Difficulty System ---

    def test_difficulty_manager_affects_ghost_release_timing(
        self, difficulty_manager_level_5
    ):
        """Test that difficulty manager affects ghost release thresholds."""
        pinky_frames = difficulty_manager_level_5.get_pinky_release_frames()
        inky_pellets = difficulty_manager_level_5.get_inky_release_pellets()
        clyde_pellets = difficulty_manager_level_5.get_clyde_release_pellets()

        # At level 5, release should be faster than default
        assert pinky_frames == 30  # Minimum
        assert inky_pellets == 15  # Minimum
        assert clyde_pellets == 40  # 60 - (4 * 5) = 40, max(40, 30) = 40

    def test_difficulty_manager_cycles_change_correctly(
        self, difficulty_manager_level_3
    ):
        """Test that difficulty manager correctly modifies mode cycles."""
        cycles = difficulty_manager_level_3.get_ghost_mode_cycles()

        # Should have same number of cycles as original
        assert len(cycles) == len(GHOST_MODE_CYCLES)

        # SCATTER durations should be reduced
        scatter_cycles = [c for c in cycles if c[0] == "SCATTER" and c[1] > 0]
        for _mode, duration in scatter_cycles:
            original_duration = next(
                d
                for m, d in GHOST_MODE_CYCLES
                if m == "SCATTER" and d == duration + 120
            )
            assert duration < original_duration

    def test_difficulty_manager_respects_minimum_values(
        self, difficulty_manager_level_5
    ):
        """Test that difficulty manager respects minimum thresholds."""
        cycles = difficulty_manager_level_5.get_ghost_mode_cycles()
        scatter_cycles = [c for c in cycles if c[0] == "SCATTER" and c[1] > 0]

        for _mode, duration in scatter_cycles:
            # Minimum SCATTER duration is 60 frames (1 second)
            assert duration >= 60

    @pytest.mark.parametrize(
        "level, expected_pinky_frames, expected_inky_pellets, expected_clyde_pellets",
        [
            (1, 60, 30, 60),  # Default values
            (2, 50, 25, 55),  # Slightly faster (Clyde: 60 - 5 = 55)
            (3, 40, 20, 50),  # Even faster (Clyde: 60 - 10 = 50)
            (4, 30, 15, 45),  # Approaching minimum (Clyde: 60 - 15 = 45, min 30)
            (5, 30, 15, 40),  # At minimum (Clyde: 60 - 20 = 40, min 30)
        ],
    )
    def test_ghost_release_progression_across_levels(
        self,
        level,
        expected_pinky_frames,
        expected_inky_pellets,
        expected_clyde_pellets,
    ):
        """Test ghost release timing progression across levels."""
        manager = DifficultyManager(level=level)

        assert manager.get_pinky_release_frames() == expected_pinky_frames
        assert manager.get_inky_release_pellets() == expected_inky_pellets
        assert manager.get_clyde_release_pellets() == expected_clyde_pellets
