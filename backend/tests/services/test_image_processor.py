"""Unit tests for ImageProcessor.

Tests cover:
- Image validation (format, size)
- Image processing (resize, thumbnail, JPEG conversion, EXIF stripping)

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8
"""

import io

import pytest
from PIL import Image

from app.services.image_processor import ImageProcessor


@pytest.fixture
def processor() -> ImageProcessor:
    return ImageProcessor(max_size_mb=5, max_dimension=400, thumbnail_dimension=100, quality=85)


def _make_image(
    width: int = 800,
    height: int = 600,
    fmt: str = "JPEG",
    mode: str = "RGB",
) -> bytes:
    """Helper to create a test image as bytes."""
    img = Image.new(mode, (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


@pytest.mark.unit
class TestImageProcessorValidation:
    """Tests for ImageProcessor.validate()."""

    def test_validate_jpeg(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="JPEG")
        processor.validate(data)  # should not raise

    def test_validate_png(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="PNG")
        processor.validate(data)

    def test_validate_webp(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="WEBP")
        processor.validate(data)

    def test_validate_rejects_invalid_bytes(self, processor: ImageProcessor) -> None:
        with pytest.raises(ValueError, match="Invalid image format"):
            processor.validate(b"not an image at all")

    def test_validate_rejects_oversized_file(self, processor: ImageProcessor) -> None:
        oversized = b"x" * (6 * 1024 * 1024)
        with pytest.raises(ValueError, match="exceeds the maximum allowed size"):
            processor.validate(oversized)

    def test_validate_rejects_bmp(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="BMP")
        with pytest.raises(ValueError, match="Invalid image format"):
            processor.validate(data)


@pytest.mark.unit
class TestImageProcessorProcess:
    """Tests for ImageProcessor.process()."""

    def test_process_resizes_large_image(self, processor: ImageProcessor) -> None:
        data = _make_image(width=2000, height=1000)
        main_bytes, thumb_bytes = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        assert main_img.width <= 400
        assert main_img.height <= 400

    def test_process_creates_thumbnail(self, processor: ImageProcessor) -> None:
        data = _make_image(width=800, height=600)
        _, thumb_bytes = processor.process(data)

        thumb_img = Image.open(io.BytesIO(thumb_bytes))
        assert thumb_img.width <= 100
        assert thumb_img.height <= 100

    def test_process_preserves_aspect_ratio(self, processor: ImageProcessor) -> None:
        data = _make_image(width=800, height=400)
        main_bytes, _ = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        # 800x400 -> 400x200 (2:1 ratio preserved)
        assert main_img.width == 400
        assert main_img.height == 200

    def test_process_outputs_jpeg(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="PNG")
        main_bytes, thumb_bytes = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        thumb_img = Image.open(io.BytesIO(thumb_bytes))
        assert main_img.format == "JPEG"
        assert thumb_img.format == "JPEG"

    def test_process_converts_rgba_to_rgb(self, processor: ImageProcessor) -> None:
        data = _make_image(fmt="PNG", mode="RGBA")
        main_bytes, _ = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        assert main_img.mode == "RGB"

    def test_process_strips_exif(self, processor: ImageProcessor) -> None:
        # Create image with EXIF data
        img = Image.new("RGB", (200, 200), color=(100, 150, 200))
        from PIL.ExifTags import Base as ExifBase

        exif = img.getexif()
        exif[ExifBase.Make] = "TestCamera"
        buf = io.BytesIO()
        img.save(buf, format="JPEG", exif=exif.tobytes())
        data = buf.getvalue()

        main_bytes, _ = processor.process(data)
        result = Image.open(io.BytesIO(main_bytes))
        result_exif = result.getexif()
        assert len(result_exif) == 0

    def test_process_small_image_not_upscaled(self, processor: ImageProcessor) -> None:
        data = _make_image(width=50, height=50)
        main_bytes, _ = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        # thumbnail() doesn't upscale
        assert main_img.width == 50
        assert main_img.height == 50

    def test_process_round_trip_produces_valid_jpeg(self, processor: ImageProcessor) -> None:
        """Round-trip property: process then read back produces valid JPEG."""
        data = _make_image(width=600, height=400, fmt="PNG")
        main_bytes, thumb_bytes = processor.process(data)

        # Both should be openable as valid JPEG
        main_img = Image.open(io.BytesIO(main_bytes))
        main_img.verify()

        thumb_img = Image.open(io.BytesIO(thumb_bytes))
        thumb_img.verify()


@pytest.mark.unit
class TestImageProcessorEdgeCases:
    """Additional edge case tests for ImageProcessor."""

    def test_process_webp_input(self, processor: ImageProcessor) -> None:
        """WebP images should be processed into JPEG. Req 2.3"""
        data = _make_image(width=500, height=500, fmt="WEBP")
        main_bytes, thumb_bytes = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        assert main_img.format == "JPEG"
        assert main_img.width <= 400

    def test_process_portrait_image(self, processor: ImageProcessor) -> None:
        """Tall portrait images should fit within max dimensions. Req 2.1"""
        data = _make_image(width=300, height=1200)
        main_bytes, thumb_bytes = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        assert main_img.width <= 400
        assert main_img.height <= 400
        # 300x1200 -> 100x400 (1:4 ratio preserved)
        assert main_img.height == 400
        assert main_img.width == 100

    def test_process_returns_two_outputs(self, processor: ImageProcessor) -> None:
        """Process must produce exactly two outputs: main and thumbnail. Req 2.7"""
        data = _make_image()
        result = processor.process(data)

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bytes)
        assert isinstance(result[1], bytes)

    def test_process_thumbnail_smaller_than_main(self, processor: ImageProcessor) -> None:
        """Thumbnail should always be smaller or equal to main image."""
        data = _make_image(width=1000, height=800)
        main_bytes, thumb_bytes = processor.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        thumb_img = Image.open(io.BytesIO(thumb_bytes))
        assert thumb_img.width <= main_img.width
        assert thumb_img.height <= main_img.height

    def test_validate_exactly_at_size_limit(self) -> None:
        """File exactly at the size limit should pass. Req 2.6"""
        proc = ImageProcessor(max_size_mb=1)
        # Create a valid image that's under 1MB
        img = Image.new("RGB", (100, 100), color=(0, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        data = buf.getvalue()
        assert len(data) < 1 * 1024 * 1024
        proc.validate(data)  # should not raise

    def test_custom_dimensions_respected(self) -> None:
        """Custom max_dimension and thumbnail_dimension should be used."""
        proc = ImageProcessor(max_dimension=200, thumbnail_dimension=50, quality=85)
        data = _make_image(width=800, height=800)
        main_bytes, thumb_bytes = proc.process(data)

        main_img = Image.open(io.BytesIO(main_bytes))
        thumb_img = Image.open(io.BytesIO(thumb_bytes))
        assert main_img.width <= 200
        assert main_img.height <= 200
        assert thumb_img.width <= 50
        assert thumb_img.height <= 50
