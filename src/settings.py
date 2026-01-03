"""Game settings and constants."""

# Constants
TILE_SIZE = 30
SCREEN_WIDTH = 19 * TILE_SIZE  # columns from game_map layout
SCREEN_HEIGHT = 22 * TILE_SIZE  # rows from game_map layout
FPS = 60

# Ghost AI settings
GHOST_SPEED = 2
PINKY_TILES_AHEAD = 4
INKY_OFFSET_TILES = 2
CLYDE_SCATTER_DISTANCE_TILES = 8

# Ghost house exit coordinates (in tiles)
GHOST_HOUSE_EXIT_X = 13.5
GHOST_HOUSE_EXIT_Y = 11.5

# Tunnel settings
TUNNEL_ROW = 10  # The row where the horizontal tunnel is located
TUNNEL_SPEED_MULTIPLIER = 0.4  # Ghosts slow to 40% in tunnel


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
