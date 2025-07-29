from enum import IntEnum


class Quality(IntEnum):
    """Enum for NVTT (NVIDIA Texture Tools) quality levels."""
    Fastest = 0
    Normal = 1
    Production = 2
    Highest = 3