from enum import IntEnum

class Error(IntEnum):
    """
    Enum for NVTT error codes.
    """
    NONE = 0
    UNKNOWN = NONE
    INVALID_INPUT = 1
    UNSUPPORTED_FEATURE = 2
    CUDA_ERROR = 3
    FILE_OPEN = 4
    FILE_WRITE = 5
    UNSUPPORTED_OUTPUT_FORMAT = 6
    MESSAGING = 7
    OUT_OF_HOST_MEMORY = 8
    OUT_OF_DEVICE_MEMORY = 9
    OUTPUT_WRITE = 10