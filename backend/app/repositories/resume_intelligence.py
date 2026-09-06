"""Resume Intelligence Engine repository.

Data access layer for the Resume Intelligence Engine.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func

from app.models.resume_intelligence import (
    ParsedResumeData,
    ResumeEntity,
    ResumeKnowledge,
    ResumeProfile,
)
from app.repositories.base import BaseRepository


class ResumeProfileRepository(BaseRepository[ResumeProfile]):
    """Repository for ResumeProfile CRUD operations."""

    def __init__(self, db):
        super().__init__(ResumeProfile, db)

    def get_by_id(self, id: str) -> Optional[ResumeProfile]:
        """Get resume profile by ID."""
        return (
            self.db.query(ResumeProfile)
            .filter(ResumeProfile.id == id, ResumeProfile.deleted_at.is_(None))
            .first()
        )

    def get_by_user_id(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ResumeProfile], int]:
        """Get resume profiles for a specific user with pagination."""
        query = (
            self.db.query(ResumeProfile)
            .filter(ResumeProfile.user_id == user_id, ResumeProfile.deleted_at.is_(None))
            .order_by(ResumeProfile.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_status(self, user_id: str, status: str) -> List[ResumeProfile]:
        """Get resume profiles by status for a user."""
        return (
            self.db.query(ResumeProfile)
            .filter(
                ResumeProfile.user_id == user_id,
                ResumeProfile.status == status,
                ResumeProfile.deleted_at.is_(None),
            )
            .order_by(ResumeProfile.created_at.desc())
            .all()
        )

    def search(
        self, user_id: str, q: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ResumeProfile], int]:
        """Search resume profiles by title."""
        query = (
            self.db.query(ResumeProfile)
            .filter(
                ResumeProfile.user_id == user_id,
                ResumeProfile.deleted_at.is_(None),
                ResumeProfile.title.ilike(f"%{q}%"),
            )
            .order_by(ResumeProfile.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, obj_in: Dict[str, Any]) -> ResumeProfile:
        """Create a new resume profile."""
        db_obj = ResumeProfile(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ResumeProfile, obj_in: Dict[str, Any]) -> ResumeProfile:
        """Update a resume profile."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, id: str) -> bool:
        """Soft delete a resume profile."""
        obj = self.db.query(ResumeProfile).filter(ResumeProfile.id == id).first()
        if obj:
            obj.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def count_by_status(self, user_id: str) -> Dict[str, int]:
        """Count resume profiles by status for a user."""
        results = (
            self.db.query(ResumeProfile.status, func.count(ResumeProfile.id))
            .filter(ResumeProfile.user_id == user_id, ResumeProfile.deleted_at.is_(None))
            .group_by(ResumeProfile.status)
            .all()
        )
        return {status: count for status, count in results}


class ParsedResumeDataRepository(BaseRepository[ParsedResumeData]):
    """Repository for ParsedResumeData operations."""

    def __init__(self, db):
        super().__init__(ParsedResumeData, db)

    def get_by_resume_profile_id(self, resume_profile_id: str) -> Optional[ParsedResumeData]:
        """Get parsed data by resume profile ID."""
        return (
            self.db.query(ParsedResumeData)
            .filter(ParsedResumeData.resume_profile_id == resume_profile_id)
            .first()
        )

    def upsert(self, resume_profile_id: str, data: Dict[str, Any]) -> ParsedResumeData:
        """Create or update parsed data for a resume profile."""
        existing = self.get_by_resume_profile_id(resume_profile_id)
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            db_obj = ParsedResumeData(resume_profile_id=resume_profile_id, **data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj


class ResumeEntityRepository(BaseRepository[ResumeEntity]):
    """Repository for ResumeEntity operations."""

    def __init__(self, db):
        super().__init__(ResumeEntity, db)

    def get_by_resume_profile_id(
        self, resume_profile_id: str, *, entity_type: Optional[str] = None
    ) -> List[ResumeEntity]:
        """Get entities for a resume profile, optionally filtered by type."""
        query = self.db.query(ResumeEntity).filter(
            ResumeEntity.resume_profile_id == resume_profile_id
        )
        if entity_type:
            query = query.filter(ResumeEntity.entity_type == entity_type)
        return query.order_by(ResumeEntity.entity_type, ResumeEntity.entity_value).all()

    def bulk_create(self, resume_profile_id: str, entities: List[Dict[str, Any]]) -> None:
        """Bulk create entities for a resume profile."""
        self.db.query(ResumeEntity).filter(
            ResumeEntity.resume_profile_id == resume_profile_id
        ).delete()
        for entity_data in entities:
            db_obj = ResumeEntity(resume_profile_id=resume_profile_id, **entity_data)
            self.db.add(db_obj)
        self.db.commit()


class ResumeKnowledgeRepository(BaseRepository[ResumeKnowledge]):
    """Repository for ResumeKnowledge operations."""

    def __init__(self, db):
        super().__init__(ResumeKnowledge, db)

    def get_by_resume_profile_id(self, resume_profile_id: str) -> Optional[ResumeKnowledge]:
        """Get knowledge by resume profile ID."""
        return (
            self.db.query(ResumeKnowledge)
            .filter(ResumeKnowledge.resume_profile_id == resume_profile_id)
            .first()
        )

    def upsert(self, resume_profile_id: str, data: Dict[str, Any]) -> ResumeKnowledge:
        """Create or update knowledge for a resume profile."""
        existing = self.get_by_resume_profile_id(resume_profile_id)
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            db_obj = ResumeKnowledge(resume_profile_id=resume_profile_id, **data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
