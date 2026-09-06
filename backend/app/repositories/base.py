"""Base repository with common CRUD operations.

Provides generic database access patterns for all domain repositories.
Uses SQLAlchemy 2.0 async-ready patterns where applicable.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlalchemy import and_
from sqlalchemy.orm import Session, Query

from ..models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing CRUD operations.

    Subclass this and override methods for domain-specific queries.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        """Get entity by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[List] = None
    ) -> List[ModelType]:
        """Get multiple entities with optional filters."""
        query = self.db.query(self.model)
        if filters:
            query = query.filter(and_(*filters))
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new entity."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """Update an existing entity."""
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        """Delete entity by ID. Returns True if deleted, False if not found."""
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def soft_delete(self, id: str) -> bool:
        """Soft delete by setting deleted_at. Returns True if deleted."""
        from datetime import datetime
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        if obj and hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def count(self, filters: Optional[List] = None) -> int:
        """Count entities with optional filters."""
        query = self.db.query(self.model)
        if filters:
            query = query.filter(and_(*filters))
        return query.count()

    def exists(self, id: str) -> bool:
        """Check if entity exists by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
