"""Game settings and constants."""

# Constants
TILE_SIZE = 30
SCREEN_WIDTH = 19 * TILE_SIZE  # columns from game_map layout
SCREEN_HEIGHT = 22 * TILE_SIZE  # rows from game_map layout
FPS = 60

# Movement speeds
PACMAN_SPEED = 2.0
PACMAN_POWERED_SPEED = 2.2  # Pac-Man goes faster when powered-up (110%)
PACMAN_EATING_SPEED_MULTIPLIER = 0.71  # Pac-Man slows to 71% when eating
GHOST_SPEED = 1.9  # Ghosts slightly slower than Pac-Man
GHOST_FRIGHTENED_SPEED = 1.0  # 50% of normal Pac-Man speed
GHOST_EATEN_SPEED = 4.0  # Fast return to house

# Ghost AI settings
PINKY_TILES_AHEAD = 4
INKY_OFFSET_TILES = 2
CLYDE_SCATTER_DISTANCE_TILES = 8

# Scatter mode target corners (in tiles)
# Each ghost retreats to a different corner in SCATTER mode
BLINKY_SCATTER_CORNER = (25, -3)  # Top-right
PINKY_SCATTER_CORNER = (-3, -3)  # Top-left
INKY_SCATTER_CORNER = (25, 32)  # Bottom-right
CLYDE_SCATTER_CORNER = (-3, 32)  # Bottom-left

# Ghost house coordinates (in tiles)
# Ghosts cannot re-enter the house once they leave (except when EATEN)
# The exit point (9.5, 8.5) must be OUTSIDE these bounds
# Only the inner rectangle with walls (7-11, 9-11) to allow ghost movement in adjacent corridors
GHOST_HOUSE_MIN_X = 7
GHOST_HOUSE_MAX_X = 11
GHOST_HOUSE_MIN_Y = 9  # Start from row 9, so row 8 (exit) is outside
GHOST_HOUSE_MAX_Y = 11

# Ghost house exit coordinates (in tiles)
# Exit is at the center top of the ghost house
GHOST_HOUSE_EXIT_X = 9.5  # Center of the map (column 9)
GHOST_HOUSE_EXIT_Y = 8.5  # Above the ghost house (row 8)

# Tunnel settings
TUNNEL_ROW = 10  # The row where the horizontal tunnel is located
TUNNEL_SPEED_MULTIPLIER = 0.4  # Ghosts slow to 40% in tunnel

# Ghost mode cycles (in frames at 60 FPS)
GHOST_MODE_CYCLES = [
    ("SCATTER", 420),  # 7 seconds
    ("CHASE", 1200),  # 20 seconds
    ("SCATTER", 420),  # 7 seconds
    ("CHASE", 1200),  # 20 seconds
    ("SCATTER", 300),  # 5 seconds
    ("CHASE", 1200),  # 20 seconds
    ("SCATTER", 300),  # 5 seconds
    ("CHASE", -1),  # Permanent CHASE (-1 means infinite)
]


# Colors
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 139)
BLUE = (33, 33, 222)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)
FRIGHTENED_BLUE = (50, 50, 255)
FRIGHTENED_WHITE = (200, 200, 255)

# Life system
STARTING_LIVES = 3
MAX_LIVES = 10
EXTRA_LIFE_SCORE = 10000  # Earn an extra life every 10,000 points
RESPAWN_INVINCIBILITY_FRAMES = 120  # 2 seconds of invincibility after respawn (60 FPS)

# UI layout
LIVES_DISPLAY_X = 20  # X position for lives display
LIVES_DISPLAY_Y = SCREEN_HEIGHT - 15  # Y position for lives display (bottom)
LIVES_ICON_SIZE = 15  # Size of life icons
LIVES_SPACING = 20  # Space between life icons

# Score display
SCORE_DISPLAY_X = 20  # X position for score display
SCORE_DISPLAY_Y = 10  # Y position for score display (top)
SCORE_FONT_SIZE = 20

# Ghost scoring
GHOST_BASE_SCORE = 200  # Base score for first frightened ghost
