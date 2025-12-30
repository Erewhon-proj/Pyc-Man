import pygame
import math
from src.settings import (
    TILE_SIZE,
    FRIGHTENED_BLUE,
    FRIGHTENED_WHITE,
    WHITE,
)
from src.direction import Direction
from src.position import Position
from src.ghost_visual_state import GhostVisualState


class GhostRenderer:
    """Responsible only for rendering and animation of a Ghost."""

    def __init__(self, ghost):
        """
        Args:
            ghost: Reference to the Ghost logic object
        """
        self.ghost = ghost
        self.radius = TILE_SIZE // 2 - 2

        # Animation state
        self._leg_phase = 0.0
        self._blink_timer = 0
        self._blink = False

    def update_animation(self):
        """Update animation timers."""
        self._leg_phase += 0.15

        if self.ghost.visual_state == GhostVisualState.FRIGHTENED:
            self._blink_timer += 1
            if self._blink_timer > 90:
                self._blink = not self._blink
                self._blink_timer = 0
        else:
            self._blink = False
            self._blink_timer = 0

    def draw(self, screen: pygame.Surface):
        """Draw the ghost based on its visual state."""
        pos: Position = self.ghost._position
        cx = int(pos.x + TILE_SIZE / 2)
        cy = int(pos.y + TILE_SIZE / 2)

        if self.ghost.visual_state == GhostVisualState.EYES:
            self._draw_eyes_only(screen, cx, cy)
            return

        if self.ghost.visual_state == GhostVisualState.FRIGHTENED:
            color = FRIGHTENED_WHITE if self._blink else FRIGHTENED_BLUE
            self._draw_body(screen, cx, cy, color)
            self._draw_frightened_face(screen, cx, cy)
        else:
            self._draw_body(screen, cx, cy, self.ghost.color)
            self._draw_eyes(screen, cx, cy)

    # --------------------------------------------------
    # Body
    # --------------------------------------------------

    def _draw_body(self, screen, cx, cy, color):
        """Draw ghost body with animated legs."""
        pygame.draw.circle(screen, color, (cx, cy - 4), self.radius)

        body_rect = pygame.Rect(
            cx - self.radius,
            cy - 4,
            self.radius * 2,
            self.radius + 6,
        )
        pygame.draw.rect(screen, color, body_rect)

        leg_count = 4
        leg_width = (self.radius * 2) // leg_count

        for i in range(leg_count):
            phase = math.sin(self._leg_phase + i) * 4
            x = cx - self.radius + i * leg_width
            y = cy + self.radius
            pygame.draw.polygon(
                screen,
                color,
                [
                    (x, y),
                    (x + leg_width, y),
                    (x + leg_width // 2, y + phase),
                ],
            )

    # --------------------------------------------------
    # Eyes (normal)
    # --------------------------------------------------

    def _draw_eyes(self, screen, cx, cy):
        """Draw eyes following ghost direction."""
        dx, dy = self.ghost._direction.value
        offset = 4

        for sign in (-1, 1):
            ex = cx + sign * 6
            ey = cy - 6
            pygame.draw.circle(screen, WHITE, (ex, ey), 5)
            pygame.draw.circle(
                screen,
                (0, 0, 255),
                (ex + dx * offset, ey + dy * offset),
                2,
            )

    # --------------------------------------------------
    # Frightened face
    # --------------------------------------------------

    def _draw_frightened_face(self, screen, cx, cy):
        """Draw frightened eyes and mouth."""
        pygame.draw.circle(screen, WHITE, (cx - 6, cy - 4), 3)
        pygame.draw.circle(screen, WHITE, (cx + 6, cy - 4), 3)

        pygame.draw.arc(
            screen,
            WHITE,
            pygame.Rect(cx - 6, cy + 2, 12, 6),
            math.pi,
            2 * math.pi,
            2,
        )

    # --------------------------------------------------
    # Eyes only
    # --------------------------------------------------

    def _draw_eyes_only(self, screen, cx, cy):
        """Draw eyes when ghost body is gone."""
        dx, dy = self.ghost._direction.value
        offset = 5

        for sign in (-1, 1):
            ex = cx + sign * 6
            ey = cy
            pygame.draw.circle(screen, WHITE, (ex, ey), 5)
            pygame.draw.circle(
                screen,
                (0, 0, 255),
                (ex + dx * offset, ey + dy * offset),
                3,
            )
