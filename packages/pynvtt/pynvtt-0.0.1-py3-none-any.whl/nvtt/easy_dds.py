from .surface import Surface
from .compression import CompressionOptions
from .output import OutputOptions
from .enums import Format, Quality
from .context import Context
from pathlib import Path

class EasyDDS:
    """A class to quickly convert an image to a DDS format."""
    def __init__(self, path: Path | str):
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Path '{p}' does not exist.")
        self._img_path = str(p.resolve())
        self._img_ext = p.suffix.lower()
        
    @property
    def img_path(self) -> str:
        """Get the image path."""
        return self._img_path
    
    @property
    def img_ext(self) -> str:
        """Get the image extension."""
        return self._img_ext
    
    @staticmethod
    def convert_img(path: Path | str) -> None:
        """Static method to convert an image to DDS format."""
        inst = EasyDDS(path)
        surf: Surface = Surface(inst.img_path)
        co: CompressionOptions = CompressionOptions()
        co.format(Format.DXT1)
        co.quality(Quality.Normal)
        oo: OutputOptions = OutputOptions()
        oo.filename(inst.img_path.replace(inst.img_ext, ".dds"))
        ctx: Context = Context()
        ctx.compress_all(surf, co, oo)