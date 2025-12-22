from typing import Generic, TypeVar
from uuid import UUID

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations"""

    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get_by_id(self, id: UUID) -> ModelType | None:
        """Get a record by ID"""
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, obj: ModelType) -> ModelType:
        """Create a new record"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Update an existing record"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete a record"""
        self.session.delete(obj)
        self.session.commit()

    def count(self) -> int:
        """Count total records"""
        from sqlmodel import func

        statement = select(func.count()).select_from(self.model)
        return self.session.exec(statement).one()
