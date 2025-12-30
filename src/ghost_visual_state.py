from enum import Enum, auto

class GhostVisualState(Enum):
    """Visual state of a ghost."""
    NORMAL = auto()
    FRIGHTENED = auto()
    EYES = auto()
