# pyNVTT
---

## About

A simple Python Wrapper for NVTT3 library, useful to convert most relevant images formats to DDS while doing modding or game development.

---

## Installation
```batch
pip install pynvtt
```
---

## Usage

Convert a PNG to DDS

```python
from nvtt.surface import Surface
from nvtt.compression import CompressionOptions
from nvtt.output import OutputOptions
from nvtt.context import Context
from nvtt.enums import Format, Quality

img_name = "texture_01.png"
parent = Path(__file__).resolve().parent
img = str(Path.joinpath(parent, img_name).resolve())

img_surface = Surface(img)

compression = CompressionOptions()
compression.format(Format.DXT1)
compression.quality(Quality.Normal)

output = OutputOptions()
output.filename(img_name.split('.')[0] + ".dds")

context = Context()
context.compress_all(img_surface, compression, output)
```

You can also use the `EasyDDS` class for your convenience.

```python
from nvtt.easy_dds import EasyDDS

img_name = "texture_01.png"
parent = Path(__file__).resolve().parent
img = Path.joinpath(parent, img_name).resolve()

EasyDDS.convert_img(img)
```
This will create a DXT1 DDS with default mipmap generation.

---

## Features

- NVTT 3.2.5 (with FreeImage 3.19.0.0)
- Multiple formats support (Mostly every format supported by FreeImage):
  - `.png`
  - `.tga`
  - `.webp`
  - `.jpg/.jpeg`
  - `.bmp`
  - `.tiff/.tif`
  - `.gif`
  - `.hdr`
  - `.dds`
  - `.psd`
- Partial API support:
  Includes `Surface`, `Context`, `OutputOptions`, and `CompressionOptions`.
- Mipmap level detection, minimum level and no mipmaps.
- Every DDS format supported (`DXT1`, `DXT5`, `BC7`, etc.)
- CUDA Acceleration support.

---

## License

Distributed under the [CC0 License](LICENSE).

