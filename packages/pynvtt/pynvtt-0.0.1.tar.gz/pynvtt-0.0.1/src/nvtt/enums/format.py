from enum import IntEnum

class Format(IntEnum):
    """Enum for NVTT (NVIDIA Texture Tools) formats."""
    #No compression formats
    RGB = 0
    RGBA = RGB
    
    #DX9 Formats
    DXT1 = 1
    DXT1a = 2
    DXT3 = 3
    DXT5 = 4
    DXT5n = 5
    
    #DX10 Formats
    BC1 = DXT1
    BC1a = DXT1a
    BC2 = DXT3
    BC3 = DXT5
    BC3n = DXT5n
    BC4 = 6
    BC4S = 7
    ATI2 = 8
    BC5 = 9
    BC5S = 10
    DXT1n = 11
    CTX1 = 12
    BC6U = 13
    BC6S = 14
    BC7 = 15
    BC3_RGBM = 16
    
    #ASTC
    ASTC_LDR_4x4 = 17
    ASTC_LDR_5x4 = 18
    ASTC_LDR_5x5 = 19
    ASTC_LDR_6x5 = 20
    ASTC_LDR_6x6 = 21
    ASTC_LDR_8x5 = 22
    ASTC_LDR_8x6 = 23
    ASTC_LDR_8x8 = 24
    ASTC_LDR_10x5 = 25
    ASTC_LDR_10x6 = 26
    ASTC_LDR_10x8 = 27
    ASTC_LDR_10x10 = 28
    ASTC_LDR_12x10 = 29
    ASTC_LDR_12x12 = 30