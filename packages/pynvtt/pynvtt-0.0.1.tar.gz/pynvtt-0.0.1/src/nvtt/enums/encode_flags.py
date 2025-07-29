from enum import IntFlag

class EncodeFlags(IntFlag):
    """
    Enum for NVTT encode flags.
    """
    NONE = 0
    USE_GPU = 1 << 0
    OUTPUT_TO_GPU_MEMORY = 1 << 1
    OPAQUE = 1 << 2