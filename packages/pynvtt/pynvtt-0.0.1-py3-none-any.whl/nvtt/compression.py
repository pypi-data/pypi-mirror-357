
from .enums import Format, Quality, PixelType
from .core import nvtt

class CompressionOptions:
    """High-level wrapper for nvttCompressionOptions."""
    def __init__(self):
        self._lib = nvtt._lib
        self._ptr = nvtt._lib.nvttCreateCompressionOptions()
        if not self._ptr:
            raise RuntimeError("Failed to create nvttCompressionOptions.")
    
    def __del__(self):
        if getattr(self, '_ptr', None):
            self._lib.nvttDestroyCompressionOptions(self._ptr)
    
    def reset(self):
        """Reset the compression options to default values."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttResetCompressionOptions(self._ptr)
        
    def format(self, format: Format):
        """Set the compression format."""
        get_format: int = int(format)
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsFormat(self._ptr, get_format)
        
    def quality(self, quality: Quality):
        """Set the compression quality."""
        get_quality: int = int(quality)
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsQuality(self._ptr, get_quality)
        
    def color_weights(self, r: float, g: float, b: float, a: float):
        """Set the color weights for compression."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsColorWeights(self._ptr, r, g, b, a)
        
    def pixel_format(self, bitcount: int, rmask: int, gmask: int, bmask: int, amask: int):
        """Set the pixel format."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsPixelFormat(self._ptr, bitcount, rmask, gmask, bmask, amask)
        
    def pixel_type(self, pixel_type: PixelType):
        """Set the pixel type."""
        get_pixel_type: int = int(pixel_type)
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsPixelType(self._ptr, get_pixel_type)
        
    def pitch_alignment(self, alignment: int):
        """Set the pitch alignment."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsPitchAlignment(self._ptr, alignment)
        
    def quantization(self, color_dithering: bool, alpha_dithering: bool, binary_alpha: bool, alpha_threshold: int):
        """Set the quantization options."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        self._lib.nvttSetCompressionOptionsQuantization(self._ptr, color_dithering, alpha_dithering, binary_alpha, alpha_threshold)
        
    def d3d9_format(self) -> int:
        """Get the D3D9 format."""
        if not self._ptr:
            raise RuntimeError("Compression options have already been destroyed or not initialized.")
        return self._lib.nvttGetCompressionOptionsD3D9Format(self._ptr)