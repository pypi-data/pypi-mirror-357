from enum import IntEnum

class NormalTransform(IntEnum):
    """
    Enum for NVTT normal transform modes.
    """
    ORTOGRAPHIC = 0
    STEREOGRAPHIC = 1
    PARABOLOID = 2
    QUARTIC = 3