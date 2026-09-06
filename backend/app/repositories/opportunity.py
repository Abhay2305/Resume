"""Opportunity Intelligence Engine repository.

Data access layer for the Opportunity Intelligence Engine.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func

from app.models.opportunity import Opportunity, OpportunityEntity, ParsedOpportunityData
from app.repositories.base import BaseRepository


class OpportunityRepository(BaseRepository[Opportunity]):
    """Repository for Opportunity CRUD operations."""

    def __init__(self, db):
        super().__init__(Opportunity, db)

    def get_by_id(self, id: str) -> Optional[Opportunity]:
        """Get opportunity by ID."""
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.id == id, Opportunity.deleted_at.is_(None))
            .first()
        )

    def get_by_user_id(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Opportunity], int]:
        """Get opportunities for a specific user with pagination."""
        query = (
            self.db.query(Opportunity)
            .filter(Opportunity.user_id == user_id, Opportunity.deleted_at.is_(None))
            .order_by(Opportunity.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_status(self, user_id: str, status: str) -> List[Opportunity]:
        """Get opportunities by status for a user."""
        return (
            self.db.query(Opportunity)
            .filter(
                Opportunity.user_id == user_id,
                Opportunity.status == status,
                Opportunity.deleted_at.is_(None),
            )
            .order_by(Opportunity.created_at.desc())
            .all()
        )

    def search(
        self, user_id: str, q: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Opportunity], int]:
        """Search opportunities by title or company."""
        query = (
            self.db.query(Opportunity)
            .filter(
                Opportunity.user_id == user_id,
                Opportunity.deleted_at.is_(None),
                (Opportunity.title.ilike(f"%{q}%")) | (Opportunity.company.ilike(f"%{q}%")),
            )
            .order_by(Opportunity.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, obj_in: Dict[str, Any]) -> Opportunity:
        """Create a new opportunity."""
        db_obj = Opportunity(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: Opportunity, obj_in: Dict[str, Any]) -> Opportunity:
        """Update an opportunity."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, id: str) -> bool:
        """Soft delete an opportunity."""
        obj = self.db.query(Opportunity).filter(Opportunity.id == id).first()
        if obj:
            obj.deleted_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def count_by_status(self, user_id: str) -> Dict[str, int]:
        """Count opportunities by status for a user."""
        results = (
            self.db.query(Opportunity.status, func.count(Opportunity.id))
            .filter(Opportunity.user_id == user_id, Opportunity.deleted_at.is_(None))
            .group_by(Opportunity.status)
            .all()
        )
        return {status: count for status, count in results}


class ParsedOpportunityDataRepository(BaseRepository[ParsedOpportunityData]):
    """Repository for ParsedOpportunityData operations."""

    def __init__(self, db):
        super().__init__(ParsedOpportunityData, db)

    def get_by_opportunity_id(self, opportunity_id: str) -> Optional[ParsedOpportunityData]:
        """Get parsed data by opportunity ID."""
        return (
            self.db.query(ParsedOpportunityData)
            .filter(ParsedOpportunityData.opportunity_id == opportunity_id)
            .first()
        )

    def upsert(self, opportunity_id: str, data: Dict[str, Any]) -> ParsedOpportunityData:
        """Create or update parsed data for an opportunity."""
        existing = self.get_by_opportunity_id(opportunity_id)
        if existing:
            for field, value in data.items():
                setattr(existing, field, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            db_obj = ParsedOpportunityData(opportunity_id=opportunity_id, **data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj


class OpportunityEntityRepository(BaseRepository[OpportunityEntity]):
    """Repository for OpportunityEntity operations."""

    def __init__(self, db):
        super().__init__(OpportunityEntity, db)

    def get_by_opportunity_id(
        self, opportunity_id: str, *, entity_type: Optional[str] = None
    ) -> List[OpportunityEntity]:
        """Get entities for an opportunity, optionally filtered by type."""
        query = self.db.query(OpportunityEntity).filter(
            OpportunityEntity.opportunity_id == opportunity_id
        )
        if entity_type:
            query = query.filter(OpportunityEntity.entity_type == entity_type)
        return query.order_by(OpportunityEntity.entity_type, OpportunityEntity.entity_value).all()

    def bulk_create(self, opportunity_id: str, entities: List[Dict[str, Any]]) -> None:
        """Bulk create entities for an opportunity."""
        # Delete existing entities for this opportunity first
        self.db.query(OpportunityEntity).filter(
            OpportunityEntity.opportunity_id == opportunity_id
        ).delete()
        # Create new entities
        for entity_data in entities:
            db_obj = OpportunityEntity(opportunity_id=opportunity_id, **entity_data)
            self.db.add(db_obj)
        self.db.commit()
