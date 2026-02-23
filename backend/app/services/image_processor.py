"""Image validation, resizing, and compression using Pillow."""

import io
import logging

from PIL import Image, ImageFile, UnidentifiedImageError
from PIL.Image import Resampling

logger = logging.getLogger(__name__)

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


class ImageProcessor:
    """Validates, resizes, compresses, and strips EXIF from uploaded images."""

    def __init__(
        self,
        max_size_mb: int = 5,
        max_dimension: int = 400,
        thumbnail_dimension: int = 100,
        quality: int = 85,
    ) -> None:
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_dimension = max_dimension
        self.thumbnail_dimension = thumbnail_dimension
        self.quality = quality

    def validate(self, file_data: bytes) -> None:
        """Raise ValueError if file is not a valid image or exceeds size limits."""
        if len(file_data) > self.max_size_bytes:
            max_mb = self.max_size_bytes // (1024 * 1024)
            raise ValueError(
                f"Image file size exceeds the maximum allowed size of {max_mb} MB"
            )
        try:
            img = Image.open(io.BytesIO(file_data))
            img.verify()
        except (UnidentifiedImageError, Exception) as e:
            raise ValueError(
                "Invalid image format. Supported formats: JPEG, PNG, WebP"
            ) from e

        # Re-open after verify (verify can leave the file in a bad state)
        img = Image.open(io.BytesIO(file_data))
        if img.format not in ALLOWED_FORMATS:
            raise ValueError("Invalid image format. Supported formats: JPEG, PNG, WebP")

    def process(self, file_data: bytes) -> tuple[bytes, bytes]:
        """Resize, compress, strip EXIF. Returns (main_bytes, thumbnail_bytes)."""
        raw_img: ImageFile.ImageFile | Image.Image = Image.open(io.BytesIO(file_data))

        # Convert to RGB (handles RGBA PNGs, palette images, etc.)
        img: Image.Image
        if raw_img.mode != "RGB":
            img = raw_img.convert("RGB")
        else:
            img = raw_img

        # Main image — fit within max_dimension x max_dimension
        main_img = img.copy()
        main_img.thumbnail((self.max_dimension, self.max_dimension), Resampling.LANCZOS)
        main_buf = io.BytesIO()
        main_img.save(main_buf, format="JPEG", quality=self.quality)
        main_bytes = main_buf.getvalue()

        # Thumbnail — fit within thumbnail_dimension x thumbnail_dimension
        thumb_img = img.copy()
        thumb_img.thumbnail(
            (self.thumbnail_dimension, self.thumbnail_dimension), Resampling.LANCZOS
        )
        thumb_buf = io.BytesIO()
        thumb_img.save(thumb_buf, format="JPEG", quality=self.quality)
        thumb_bytes = thumb_buf.getvalue()

        logger.info(
            "Processed image: main=%dx%d (%d bytes), thumb=%dx%d (%d bytes)",
            main_img.width,
            main_img.height,
            len(main_bytes),
            thumb_img.width,
            thumb_img.height,
            len(thumb_bytes),
        )

        return main_bytes, thumb_bytes
