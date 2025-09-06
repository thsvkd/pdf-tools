from enum import StrEnum


class FormatType(StrEnum):
    """Supported file format types"""

    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"


class ConversionType(StrEnum):
    """Conversion direction types"""

    PDF = "pdf"
    IMAGE = "image"
