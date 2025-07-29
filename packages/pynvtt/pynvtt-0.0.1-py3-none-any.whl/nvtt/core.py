import ctypes
from pathlib import Path

LIBRARY_PATH = Path(Path(__file__).parent) / "libs"

NVTT_DLL_NAME: str = "nvtt30205.dll"


class NVTT:
    """Wrapper for the NVIDIA Texture Tools (nvtt) library."""
    def __init__(self, dll_path: str = str(Path.joinpath(LIBRARY_PATH, NVTT_DLL_NAME))):
        self._lib = ctypes.CDLL(dll_path)
        self._version: int = 0

        class NvttCompressionOptions(ctypes.Structure):
            pass

        class NvttOutputOptions(ctypes.Structure):
            pass

        class NvttContext(ctypes.Structure):
            pass

        class NvttSurface(ctypes.Structure):
            pass

        self.NvttCompressionOptionsPtr = ctypes.POINTER(NvttCompressionOptions)

        self.NvttOutputOptionsPtr = ctypes.POINTER(NvttOutputOptions)

        self.NvttContextPtr = ctypes.POINTER(NvttContext)

        self.NvttSurfacePtr = ctypes.POINTER(NvttSurface)

        self.map_comp_options_funcs()
        self.map_out_options_funcs()
        self.map_context_funcs()
        self.map_surface_funcs()
        self.map_nvtt_funcs()

    def map_nvtt_funcs(self):
        """Map NVTT functions."""
        self._lib.nvttVersion.restype = ctypes.c_uint
        self._lib.nvttVersion.argtypes = []

    def map_surface_funcs(self):
        """Map nvttSurface functions."""

        self._lib.nvttCreateSurface.restype = self.NvttSurfacePtr
        self._lib.nvttCreateSurface.argtypes = ()

        self._lib.nvttDestroySurface.restype = None
        self._lib.nvttDestroySurface.argtypes = [self.NvttSurfacePtr]

        self._lib.nvttSurfaceLoad.restype = ctypes.c_bool
        self._lib.nvttSurfaceLoad.argtypes = (
            self.NvttSurfacePtr,  # Surface
            ctypes.c_char_p,  # filename
            ctypes.POINTER(ctypes.c_bool),  # hasAlpha
            ctypes.c_bool,  # expectSigned
            ctypes.c_void_p,  # NvttTimingContext
        )

        self._lib.nvttSurfaceWidth.restype = ctypes.c_int
        self._lib.nvttSurfaceWidth.argtypes = [self.NvttSurfacePtr]
        self._lib.nvttSurfaceHeight.restype = ctypes.c_int
        self._lib.nvttSurfaceHeight.argtypes = [self.NvttSurfacePtr]

        self._lib.nvttSurfaceDepth.restype = ctypes.c_int
        self._lib.nvttSurfaceDepth.argtypes = [self.NvttSurfacePtr]

        self._lib.nvttSurfaceCountMipmaps.restype = ctypes.c_int
        self._lib.nvttSurfaceCountMipmaps.argtypes = [self.NvttSurfacePtr, ctypes.c_int]

        self._lib.nvttSurfaceBuildNextMipmapDefaults.restype = ctypes.c_bool
        self._lib.nvttSurfaceBuildNextMipmapDefaults.argtypes = [
            self.NvttSurfacePtr,
            ctypes.c_int,
        ]

    def map_comp_options_funcs(self):
        """Map nvttCompressionOptions functions."""
        self._lib.nvttCreateCompressionOptions.restype = self.NvttCompressionOptionsPtr
        self._lib.nvttCreateCompressionOptions.argtypes = ()

        self._lib.nvttDestroyCompressionOptions.restype = None
        self._lib.nvttDestroyCompressionOptions.argtypes = [
            self.NvttCompressionOptionsPtr
        ]

        self._lib.nvttResetCompressionOptions.restype = None
        self._lib.nvttResetCompressionOptions.argtypes = [
            self.NvttCompressionOptionsPtr
        ]

        self._lib.nvttSetCompressionOptionsFormat.restype = None
        self._lib.nvttSetCompressionOptionsFormat.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetCompressionOptionsQuality.restype = None
        self._lib.nvttSetCompressionOptionsQuality.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetCompressionOptionsColorWeights.restype = None
        self._lib.nvttSetCompressionOptionsColorWeights.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
            ctypes.c_float,
        ]

        self._lib.nvttSetCompressionOptionsPixelFormat.restype = None
        self._lib.nvttSetCompressionOptionsPixelFormat.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_uint,
        ]

        self._lib.nvttSetCompressionOptionsPixelType.restype = None
        self._lib.nvttSetCompressionOptionsPixelType.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetCompressionOptionsPitchAlignment.restype = None
        self._lib.nvttSetCompressionOptionsPitchAlignment.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetCompressionOptionsQuantization.restype = None
        self._lib.nvttSetCompressionOptionsQuantization.argtypes = [
            self.NvttCompressionOptionsPtr,
            ctypes.c_bool,
            ctypes.c_bool,
            ctypes.c_bool,
            ctypes.c_int,
        ]

        self._lib.nvttGetCompressionOptionsD3D9Format.restype = ctypes.c_uint
        self._lib.nvttGetCompressionOptionsD3D9Format.argtypes = [
            self.NvttCompressionOptionsPtr
        ]

    def map_out_options_funcs(self):
        """Map nvttOutputOptions functions."""
        self._lib.nvttCreateOutputOptions.restype = self.NvttOutputOptionsPtr
        self._lib.nvttCreateOutputOptions.argtypes = ()

        self._lib.nvttDestroyOutputOptions.restype = None
        self._lib.nvttDestroyOutputOptions.argtypes = [self.NvttOutputOptionsPtr]

        self._lib.nvttResetOutputOptions.restype = None
        self._lib.nvttResetOutputOptions.argtypes = [self.NvttOutputOptionsPtr]

        self._lib.nvttSetOutputOptionsFileName.restype = None
        self._lib.nvttSetOutputOptionsFileName.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_char_p,
        ]

        self._lib.nvttSetOutputOptionsErrorHandler.restype = None
        self._lib.nvttSetOutputOptionsErrorHandler.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetOutputOptionsContainer.restype = None
        self._lib.nvttSetOutputOptionsContainer.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetOutputOptionsOutputHeader.restype = None
        self._lib.nvttSetOutputOptionsOutputHeader.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_bool,
        ]

        self._lib.nvttSetOutputOptionsUserVersion.restype = None
        self._lib.nvttSetOutputOptionsUserVersion.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_int,
        ]

        self._lib.nvttSetOutputOptionsSrgbFlag.restype = None
        self._lib.nvttSetOutputOptionsSrgbFlag.argtypes = [
            self.NvttOutputOptionsPtr,
            ctypes.c_bool,
        ]

    def map_context_funcs(self):
        """Map nvttContext functions."""
        self._lib.nvttCreateContext.restype = self.NvttContextPtr
        self._lib.nvttCreateContext.argtypes = ()

        self._lib.nvttDestroyContext.restype = None
        self._lib.nvttDestroyContext.argtypes = [self.NvttContextPtr]

        self._lib.nvttSetContextCudaAcceleration.restype = None
        self._lib.nvttSetContextCudaAcceleration.argtypes = [
            self.NvttContextPtr,
            ctypes.c_bool,
        ]

        self._lib.nvttContextIsCudaAccelerationEnabled.restype = ctypes.c_bool
        self._lib.nvttContextIsCudaAccelerationEnabled.argtypes = [self.NvttContextPtr]

        self._lib.nvttContextOutputHeader.restype = ctypes.c_bool
        self._lib.nvttContextOutputHeader.argtypes = [
            self.NvttContextPtr,
            self.NvttSurfacePtr,
            ctypes.c_int,
            self.NvttCompressionOptionsPtr,
            self.NvttOutputOptionsPtr,
        ]

        self._lib.nvttContextCompress.restype = ctypes.c_bool
        self._lib.nvttContextCompress.argtypes = [
            self.NvttContextPtr,
            self.NvttSurfacePtr,
            ctypes.c_int,
            ctypes.c_int,
            self.NvttCompressionOptionsPtr,
            self.NvttOutputOptionsPtr,
        ]

        self._lib.nvttContextEstimateSize.restype = ctypes.c_int
        self._lib.nvttContextEstimateSize.argtypes = [
            self.NvttContextPtr,
            self.NvttSurfacePtr,
            ctypes.c_int,
            self.NvttCompressionOptionsPtr,
        ]

    @property
    def version(self) -> int:
        """Get NVTT's version."""
        if self._version == 0:
            self._version = self._lib.nvttVersion()
        return self._version

nvtt = NVTT()

# This software uses the FreeImage open source image library. See http://freeimage.sourceforge.net for details.
# FreeImage is used under the (GNU GPL or FIPL), version (license version).
