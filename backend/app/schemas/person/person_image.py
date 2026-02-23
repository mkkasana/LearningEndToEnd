"""Person profile image response schemas."""

from sqlmodel import SQLModel


class PersonImageResponse(SQLModel):
    """Response with image URLs."""

    main_url: str
    thumbnail_url: str


class PersonImageUploadResponse(SQLModel):
    """Response after successful image upload."""

    message: str
    main_url: str
    thumbnail_url: str
