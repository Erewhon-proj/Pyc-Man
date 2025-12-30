import pytest
import pygame

from src.ghost_renderer import GhostRenderer
from src.ghost_visual_state import GhostVisualState
from src.direction import Direction
from src.position import Position
from src.settings import (
    FRIGHTENED_BLUE,
    FRIGHTENED_WHITE,
    TILE_SIZE,
)


class DummyGhost:
    def __init__(self):
        self.visual_state = GhostVisualState.NORMAL
        self.color = (255, 0, 0)
        self._direction = Direction.RIGHT
        self._position = Position(0, 0)


@pytest.fixture
def ghost():
    return DummyGhost()



@pytest.fixture
def renderer(ghost):
    return GhostRenderer(ghost)



@pytest.fixture
def screen():
    pygame.init()
    return pygame.Surface((TILE_SIZE * 2, TILE_SIZE * 2))



def test_renderer_initial_state(renderer):
    """Renderer should start with default animation values."""
    assert renderer._leg_phase == 0.0
    assert renderer._blink is False
    assert renderer._blink_timer == 0



@pytest.mark.parametrize("state,expected_blink_timer", [
    (GhostVisualState.NORMAL, 0),
    (GhostVisualState.FRIGHTENED, 2),
])
def test_update_animation(renderer, ghost, state):
    """Leg phase always increases; blink timer depends on state."""
    ghost.visual_state = state

    renderer.update_animation()
    renderer.update_animation()

    assert renderer._leg_phase > 0
    if state == GhostVisualState.FRIGHTENED:
        assert renderer._blink_timer == 2
    else:
        assert renderer._blink_timer == 0


def test_frightened_blink_toggle(renderer, ghost):
    """Blink toggles after threshold."""
    ghost.visual_state = GhostVisualState.FRIGHTENED

    for _ in range(91):
        renderer.update_animation()

    assert renderer._blink is True
    assert renderer._blink_timer == 0


@pytest.mark.parametrize("state,blink,color_expected,circle_calls", [
    (GhostVisualState.EYES, False, None, 4),                 # eyes-only
    (GhostVisualState.FRIGHTENED, False, FRIGHTENED_BLUE, None),  # frightened non blinking
    (GhostVisualState.FRIGHTENED, True, FRIGHTENED_WHITE, None),  # frightened blinking
    (GhostVisualState.NORMAL, False, None, None),            # normal
])
def test_draw_states(renderer, ghost, screen, mocker, state, blink, color_expected, circle_calls):
    """Test draw function for all visual states."""
    ghost.visual_state = state
    renderer._blink = blink

    mock_circle = mocker.patch("pygame.draw.circle")
    mocker.patch("pygame.draw.rect")
    mocker.patch("pygame.draw.polygon")
    mocker.patch("pygame.draw.arc")

    renderer.draw(screen)

    if circle_calls is not None:
        # Eyes-only: numero di chiamate previsto
        assert mock_circle.call_count == circle_calls
    elif color_expected is not None:
        # Frightened: primo cerchio deve avere colore corretto
        args, _ = mock_circle.call_args_list[0]
        assert args[1] == color_expected
    else:
        # Stato normale: ci saranno più di 2 chiamate
        assert mock_circle.call_count > 2
