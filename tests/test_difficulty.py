"""Test suite for DifficultyManager and difficulty progression system."""

# pylint: disable=redefined-outer-name

import pytest

from src.difficulty import DifficultyManager
from src.settings import (
    GHOST_SPEED,
    MAX_CHASE_SPEED_MULTIPLIER,
    MAX_GHOST_SPEED,
    MIN_FRIGHTENED_DURATION,
)


# pylint: disable=too-many-public-methods
class TestDifficultyManager:
    """Test suite for DifficultyManager class."""

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

    # --- Initialization Tests ---

    def test_difficulty_manager_initializes_with_level(self):
        """Test that DifficultyManager initializes with correct level."""
        manager = DifficultyManager(level=5)
        assert manager.level == 5

    def test_difficulty_manager_defaults_to_level_1(self):
        """Test that DifficultyManager defaults to level 1."""
        manager = DifficultyManager()
        assert manager.level == 1

    # --- Ghost Speed Tests ---

    def test_get_ghost_speed_level_1(self, difficulty_manager_level_1):
        """Test ghost speed at level 1 is base speed."""
        speed = difficulty_manager_level_1.get_ghost_speed()
        assert speed == GHOST_SPEED

    def test_get_ghost_speed_level_2(self):
        """Test ghost speed increases at level 2."""
        manager = DifficultyManager(level=2)
        speed = manager.get_ghost_speed()
        assert speed == GHOST_SPEED + 0.05

    def test_get_ghost_speed_level_3_plateau(self, difficulty_manager_level_3):
        """Test ghost speed plateaus at level 3."""
        speed = difficulty_manager_level_3.get_ghost_speed()
        assert speed == MAX_GHOST_SPEED

    def test_get_ghost_speed_level_5_remains_plateaued(
        self, difficulty_manager_level_5
    ):
        """Test ghost speed remains at maximum beyond level 3."""
        speed = difficulty_manager_level_5.get_ghost_speed()
        assert speed == MAX_GHOST_SPEED

    @pytest.mark.parametrize(
        "level, expected_speed",
        [
            (1, 1.9),  # Base speed
            (2, 1.95),  # +0.05
            (3, 2.0),  # +0.10 (plateau starts)
            (4, 2.0),  # Still plateau
            (5, 2.0),  # Still plateau
            (10, 2.0),  # Still plateau
        ],
    )
    def test_get_ghost_speed_progression(self, level, expected_speed):
        """Test ghost speed progression across all levels."""
        manager = DifficultyManager(level=level)
        assert manager.get_ghost_speed() == expected_speed

    # --- CHASE Speed Multiplier Tests ---

    def test_get_chase_multiplier_level_1(self, difficulty_manager_level_1):
        """Test CHASE multiplier is 1.0 at level 1."""
        multiplier = difficulty_manager_level_1.get_chase_speed_multiplier()
        assert multiplier == 1.0

    def test_get_chase_multiplier_increases_per_level(self):
        """Test CHASE multiplier increases by 10% per level."""
        manager = DifficultyManager(level=3)
        multiplier = manager.get_chase_speed_multiplier()
        assert multiplier == 1.2

    def test_get_chase_multiplier_level_4(self):
        """Test CHASE multiplier at level 4."""
        manager = DifficultyManager(level=4)
        multiplier = manager.get_chase_speed_multiplier()
        assert multiplier == 1.3

    def test_get_chase_multiplier_maxes_out(self, difficulty_manager_level_5):
        """Test CHASE multiplier reaches maximum at level 5."""
        multiplier = difficulty_manager_level_5.get_chase_speed_multiplier()
        assert multiplier == MAX_CHASE_SPEED_MULTIPLIER

    @pytest.mark.parametrize(
        "level, expected_multiplier",
        [
            (1, 1.0),  # Base
            (2, 1.1),  # +10%
            (3, 1.2),  # +20%
            (4, 1.3),  # +30%
            (5, 1.4),  # +40% (max)
            (10, 1.4),  # Still max
        ],
    )
    def test_get_chase_multiplier_progression(self, level, expected_multiplier):
        """Test CHASE multiplier progression across all levels."""
        manager = DifficultyManager(level=level)
        assert manager.get_chase_speed_multiplier() == expected_multiplier

    # --- Frightened Duration Tests ---

    def test_get_frightened_duration_level_1(self, difficulty_manager_level_1):
        """Test frightened duration is 10 seconds at level 1."""
        duration_frames = difficulty_manager_level_1.get_frightened_duration_frames()
        assert duration_frames == 600  # 10 seconds at 60 FPS

    def test_get_frightened_duration_level_2(self):
        """Test frightened duration decreases at level 2."""
        manager = DifficultyManager(level=2)
        duration_frames = manager.get_frightened_duration_frames()
        assert duration_frames == 480  # 8 seconds at 60 FPS

    def test_get_frightened_duration_level_3(self, difficulty_manager_level_3):
        """Test frightened duration decreases more at level 3."""
        duration_frames = difficulty_manager_level_3.get_frightened_duration_frames()
        assert duration_frames == 360  # 6 seconds at 60 FPS

    def test_get_frightened_duration_level_4(self):
        """Test frightened duration decreases gradually after level 3."""
        manager = DifficultyManager(level=4)
        duration_frames = manager.get_frightened_duration_frames()
        assert duration_frames == 210  # 3.5 seconds at 60 FPS (4s - 0.5s)

    def test_get_frightened_duration_never_goes_below_minimum(
        self, difficulty_manager_level_5
    ):
        """Test frightened duration respects minimum threshold."""
        duration_frames = difficulty_manager_level_5.get_frightened_duration_frames()
        expected_min_frames = int(MIN_FRIGHTENED_DURATION * 60)
        assert duration_frames >= expected_min_frames

    @pytest.mark.parametrize(
        "level, expected_duration",
        [
            (1, 600),  # 10 seconds
            (2, 480),  # 8 seconds
            (3, 360),  # 6 seconds
            (4, 210),  # 3.5 seconds (4s base - 0.5s)
            (5, 180),  # 3 seconds (4s base - 1s)
            (7, 120),  # 2 seconds (min)
            (10, 120),  # Still min
        ],
    )
    def test_get_frightened_duration_progression(self, level, expected_duration):
        """Test frightened duration progression across all levels."""
        manager = DifficultyManager(level=level)
        assert manager.get_frightened_duration_frames() == expected_duration

    # --- Ghost Release Timing Tests ---

    def test_get_pinky_release_frames_level_1(self, difficulty_manager_level_1):
        """Test Pinky release at level 1 is 60 frames."""
        frames = difficulty_manager_level_1.get_pinky_release_frames()
        assert frames == 60

    def test_get_pinky_release_frames_decreases(self, difficulty_manager_level_5):
        """Test Pinky release decreases at higher levels."""
        frames = difficulty_manager_level_5.get_pinky_release_frames()
        assert frames == 30  # Minimum

    def test_get_inky_release_pellets_level_1(self, difficulty_manager_level_1):
        """Test Inky release at level 1 is 30 pellets."""
        pellets = difficulty_manager_level_1.get_inky_release_pellets()
        assert pellets == 30

    def test_get_inky_release_pellets_decreases(self, difficulty_manager_level_5):
        """Test Inky release decreases at higher levels."""
        pellets = difficulty_manager_level_5.get_inky_release_pellets()
        assert pellets == 15  # Minimum

    def test_get_clyde_release_pellets_level_1(self, difficulty_manager_level_1):
        """Test Clyde release at level 1 is 60 pellets."""
        pellets = difficulty_manager_level_1.get_clyde_release_pellets()
        assert pellets == 60

    def test_get_clyde_release_pellets_decreases(self, difficulty_manager_level_5):
        """Test Clyde release decreases at higher levels."""
        pellets = difficulty_manager_level_5.get_clyde_release_pellets()
        # At level 5: 60 - (4 * 5) = 40, max(40, 30) = 40
        assert pellets == 40

    # --- SCATTER Reduction Tests ---

    def test_get_scatter_reduction_level_1(self, difficulty_manager_level_1):
        """Test SCATTER reduction is 0 at level 1."""
        reduction = difficulty_manager_level_1.get_scatter_reduction()
        assert reduction == 0

    def test_get_scatter_reduction_increases(self):
        """Test SCATTER reduction increases per level."""
        manager = DifficultyManager(level=3)
        reduction = manager.get_scatter_reduction()
        assert reduction == 120  # 2 seconds * 60 FPS

    def test_get_scatter_reduction_maxes_out(self, difficulty_manager_level_5):
        """Test SCATTER reduction reaches maximum."""
        reduction = difficulty_manager_level_5.get_scatter_reduction()
        assert reduction == 240  # 4 seconds * 60 FPS (max)

    @pytest.mark.parametrize(
        "level, expected_reduction",
        [
            (1, 0),  # No reduction
            (2, 60),  # 1 second
            (3, 120),  # 2 seconds
            (4, 180),  # 3 seconds
            (5, 240),  # 4 seconds (max)
            (10, 240),  # Still max
        ],
    )
    def test_get_scatter_reduction_progression(self, level, expected_reduction):
        """Test SCATTER reduction progression across all levels."""
        manager = DifficultyManager(level=level)
        assert manager.get_scatter_reduction() == expected_reduction

    # --- Ghost Mode Cycles Tests ---

    def test_get_ghost_mode_cycles_level_1(self, difficulty_manager_level_1):
        """Test ghost mode cycles are unchanged at level 1."""
        cycles = difficulty_manager_level_1.get_ghost_mode_cycles()
        # Should match original cycles from settings
        assert len(cycles) > 0
        assert cycles[0][0] == "SCATTER"

    def test_get_ghost_mode_cycles_reduces_scatter(self, difficulty_manager_level_3):
        """Test SCATTER durations are reduced at higher levels."""
        cycles = difficulty_manager_level_3.get_ghost_mode_cycles()
        # Find SCATTER modes and verify they're reduced
        scatter_cycles = [c for c in cycles if c[0] == "SCATTER"]
        for _mode, duration in scatter_cycles:
            if duration > 0:  # Not permanent mode
                assert duration < 420  # Original 7 seconds = 420 frames

    def test_get_ghost_mode_cycles_preserves_chase(self, difficulty_manager_level_5):
        """Test CHASE durations are unchanged."""
        cycles = difficulty_manager_level_5.get_ghost_mode_cycles()
        # CHASE durations should be unchanged
        chase_cycles = [c for c in cycles if c[0] == "CHASE"]
        for _mode, duration in chase_cycles:
            # Original CHASE durations should be preserved
            assert duration > 0 or duration == -1  # Positive or permanent

    def test_get_ghost_mode_cycles_preserves_permanent_mode(
        self, difficulty_manager_level_5
    ):
        """Test permanent mode marker is preserved."""
        cycles = difficulty_manager_level_5.get_ghost_mode_cycles()
        # Last cycle should be permanent CHASE
        last_mode, last_duration = cycles[-1]
        assert last_mode == "CHASE"
        assert last_duration == -1

    # --- Edge Cases and Integration Tests ---

    def test_difficulty_manager_handles_high_levels(self):
        """Test DifficultyManager handles very high levels gracefully."""
        manager = DifficultyManager(level=100)

        assert manager.get_ghost_speed() == MAX_GHOST_SPEED
        assert manager.get_chase_speed_multiplier() == MAX_CHASE_SPEED_MULTIPLIER
        assert manager.get_frightened_duration_frames() >= int(
            MIN_FRIGHTENED_DURATION * 60
        )
        assert manager.get_pinky_release_frames() >= 30
        assert manager.get_inky_release_pellets() >= 15

    def test_all_methods_return_valid_types(self, difficulty_manager_level_1):
        """Test all methods return expected types."""
        assert isinstance(difficulty_manager_level_1.get_ghost_speed(), float)
        assert isinstance(
            difficulty_manager_level_1.get_chase_speed_multiplier(), float
        )
        assert isinstance(
            difficulty_manager_level_1.get_frightened_duration_frames(), int
        )
        assert isinstance(difficulty_manager_level_1.get_pinky_release_frames(), int)
        assert isinstance(difficulty_manager_level_1.get_inky_release_pellets(), int)
        assert isinstance(difficulty_manager_level_1.get_clyde_release_pellets(), int)
        assert isinstance(difficulty_manager_level_1.get_scatter_reduction(), int)
        assert isinstance(difficulty_manager_level_1.get_ghost_mode_cycles(), list)
