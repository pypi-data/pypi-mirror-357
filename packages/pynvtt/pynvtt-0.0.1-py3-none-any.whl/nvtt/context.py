import ctypes
from .surface import Surface
from .compression import CompressionOptions
from .output import OutputOptions
from .enums import MipmapFilter
from .core import nvtt

class Context:
    """Context for NVTT operations."""
    
    def __init__(self):
        self._lib = nvtt._lib
        self._ptr = nvtt._lib.nvttCreateContext()
        if not self._ptr:
            raise RuntimeError("Failed to create NVTT context.")
        
    def __del__(self):
        if getattr(self, '_ptr', None):
            self._lib.nvttDestroyContext(self._ptr)
            
    def set_cuda_acceleration(self, enabled: bool):
        """Enable or disable CUDA acceleration."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        self._lib.nvttSetContextCudaAcceleration(self._ptr, ctypes.c_bool(enabled))
        
    @property
    def is_cuda_acceleration_enabled(self) -> bool:
        """Check if CUDA acceleration is enabled."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextIsCudaAccelerationEnabled(self._ptr)
    
    def output_header(self, surface: Surface, mipmap_count: int, co: CompressionOptions, oo: OutputOptions):
        """Output the header for the given surface."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextOutputHeader(self._ptr, surface._ptr, mipmap_count, 
                                                 co._ptr, oo._ptr)
        
    def compress(self, surface: Surface, face: int, mipmap: int, co: CompressionOptions, oo: OutputOptions):
        """Compress the given surface."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextCompress(self._ptr, surface._ptr, face, mipmap, 
                                             co._ptr, oo._ptr)
        
    def compress_all(self, surface: Surface, co: CompressionOptions, oo: OutputOptions, face=0, min_level = 1, mipmap_filter: MipmapFilter = MipmapFilter.MITCHELL, do_mips: bool = True):
        """Compresses the surface with every mipmap level and exports the result."""
        mipmap_count: int = surface.count_mipmaps(min_level) if do_mips else 1
        self.output_header(surface, mipmap_count, co, oo)
        self.compress(surface, face, 0, co, oo)
        
        for level in range(1, mipmap_count):
            mipmap_has_built: bool = surface.build_next_mipmap(int(mipmap_filter), min_level)
            if not mipmap_has_built:
                raise RuntimeError(f"Failed to build mipmap level {level} for surface {surface._ptr}.")
            
            has_compressed: bool = self.compress(surface, face, level, co, oo)
            if not has_compressed:
                raise RuntimeError(f"Failed to compress the {surface._ptr} surface.")
        
    def estimate_size(self, surface: Surface, mipmap_count: int, co: CompressionOptions):
        """Estimate the size of the compressed data for the given surface."""
        if not self._ptr:
            raise RuntimeError("Context has already been destroyed or not initialized.")
        return self._lib.nvttContextEstimateSize(self._ptr, surface._ptr, mipmap_count, co._ptr)