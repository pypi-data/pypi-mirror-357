from .enums import Container
from .core import nvtt


class OutputOptions:
    """High-level wrapper for nvttOutputOptions."""

    def __init__(self):
        self._lib = nvtt._lib
        self._ptr = nvtt._lib.nvttCreateOutputOptions()
        if not self._ptr:
            raise RuntimeError("Failed to create nvttCompressionOptions.")

    def __del__(self):
        if getattr(self, "_ptr", None):
            self._lib.nvttDestroyOutputOptions(self._ptr)

    def reset(self):
        """Reset the options to their default values."""
        self._lib.nvttResetOutputOptions(self._ptr)

    def filename(self, filename: str) -> None:
        """Set the output filename."""
        if not self._ptr:
            raise RuntimeError("Failed to set output filename.")
        self._lib.nvttSetOutputOptionsFileName(self._ptr, filename.encode("utf-8"))

    def error_handler(self) -> int:
        """Set the current error handler."""
        if not self._ptr:
            raise RuntimeError("Failed to get error handler.")
        return self._lib.nvttSetOutputOptionsErrorHandler(self._ptr)

    def output_header(self, output_header: bool) -> None:
        """Set whether to output the header."""
        if not self._ptr:
            raise RuntimeError("Failed to set output header option.")
        self._lib.nvttSetOutputOptionsOutputHeader(self._ptr, output_header)

    def container(self, container: Container) -> None:
        """Set the output container format."""
        get_container: int = int(container)
        if not self._ptr:
            raise RuntimeError("Failed to set output container format.")
        self._lib.nvttSetOutputOptionsContainer(self._ptr, get_container)
