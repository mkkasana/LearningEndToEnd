"""Service for person profile image upload, deletion, and URL retrieval."""

import logging
import uuid

from sqlmodel import Session

from app.core.config import settings
from app.db_models.person.person import Person
from app.services.image_processor import ImageProcessor
from app.services.storage import get_storage_backend

logger = logging.getLogger(__name__)


class ImageUploadService:
    """Orchestrates image validation, processing, storage, and DB updates."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.storage = get_storage_backend()
        self.processor = ImageProcessor(
            max_size_mb=settings.IMAGE_MAX_SIZE_MB,
            max_dimension=settings.IMAGE_MAX_DIMENSION,
            thumbnail_dimension=settings.IMAGE_THUMBNAIL_DIMENSION,
            quality=settings.IMAGE_QUALITY,
        )

    def upload_profile_image(self, person: Person, file_data: bytes) -> dict[str, str]:
        """Validate, process, store image and update person record.

        Returns dict with message, main_url, and thumbnail_url.
        """
        # Validate
        self.processor.validate(file_data)

        # Process into main + thumbnail
        main_bytes, thumb_bytes = self.processor.process(file_data)

        # Generate unique filenames
        image_id = uuid.uuid4().hex
        main_filename = f"{image_id}.jpg"
        thumb_filename = f"{image_id}_thumb.jpg"

        # Clean up old image if exists
        if person.profile_image_key:
            self._delete_image_files(person.profile_image_key)

        # Upload both variants
        self.storage.upload(main_bytes, main_filename)
        self.storage.upload(thumb_bytes, thumb_filename)

        # Update person record
        person.profile_image_key = main_filename
        self.session.add(person)
        self.session.commit()
        self.session.refresh(person)

        logger.info(
            "Uploaded profile image for person %s: %s",
            person.id,
            main_filename,
        )

        return {
            "message": "Profile image uploaded successfully",
            "main_url": self.storage.get_url(main_filename),
            "thumbnail_url": self.storage.get_url(thumb_filename),
        }

    def delete_profile_image(self, person: Person) -> None:
        """Delete image files from storage and clear person record."""
        if not person.profile_image_key:
            return

        self._delete_image_files(person.profile_image_key)

        person.profile_image_key = None
        self.session.add(person)
        self.session.commit()
        self.session.refresh(person)

        logger.info("Deleted profile image for person %s", person.id)

    def get_image_urls(self, person: Person) -> dict[str, str] | None:
        """Return main and thumbnail URLs, or None if no image."""
        if not person.profile_image_key:
            return None

        main_filename = person.profile_image_key
        thumb_filename = main_filename.replace(".jpg", "_thumb.jpg")

        return {
            "main_url": self.storage.get_url(main_filename),
            "thumbnail_url": self.storage.get_url(thumb_filename),
        }

    def _delete_image_files(self, image_key: str) -> None:
        """Delete both main and thumbnail files for a given image key."""
        thumb_key = image_key.replace(".jpg", "_thumb.jpg")
        try:
            self.storage.delete(image_key)
            self.storage.delete(thumb_key)
        except Exception:
            logger.exception("Error deleting image files: %s", image_key)
