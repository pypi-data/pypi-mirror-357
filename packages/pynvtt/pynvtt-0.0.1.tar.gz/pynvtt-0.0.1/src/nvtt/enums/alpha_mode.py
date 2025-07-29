from enum import IntEnum

class AlphaMode(IntEnum):
    """
    Enum for NVTT alpha modes.
    """
    NONE = 0
    TRANSPARENCY = 1
    PREMULTIPLIED = 2