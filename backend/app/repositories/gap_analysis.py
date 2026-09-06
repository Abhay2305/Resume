"""Gap Analysis Engine repository.

Data access layer for the Gap Analysis Engine.
"""
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_

from app.models.gap_analysis import GapAnalysis, GapResult, Recommendation
from app.repositories.base import BaseRepository


class GapAnalysisRepository(BaseRepository[GapAnalysis]):
    """Repository for GapAnalysis CRUD operations."""

    def __init__(self, db):
        super().__init__(GapAnalysis, db)

    def get_by_id(self, id: str) -> Optional[GapAnalysis]:
        """Get gap analysis by ID."""
        return (
            self.db.query(GapAnalysis)
            .filter(GapAnalysis.id == id)
            .first()
        )

    def get_by_user_id(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[GapAnalysis], int]:
        """Get gap analyses for a specific user with pagination."""
        query = (
            self.db.query(GapAnalysis)
            .filter(GapAnalysis.user_id == user_id)
            .order_by(GapAnalysis.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_by_resume_and_opportunity(
        self, resume_profile_id: str, opportunity_id: str
    ) -> Optional[GapAnalysis]:
        """Get existing gap analysis for a resume-opportunity pair."""
        return (
            self.db.query(GapAnalysis)
            .filter(
                GapAnalysis.resume_profile_id == resume_profile_id,
                GapAnalysis.opportunity_id == opportunity_id,
            )
            .first()
        )

    def get_by_status(self, user_id: str, status: str) -> List[GapAnalysis]:
        """Get gap analyses by status for a user."""
        return (
            self.db.query(GapAnalysis)
            .filter(
                GapAnalysis.user_id == user_id,
                GapAnalysis.status == status,
            )
            .order_by(GapAnalysis.created_at.desc())
            .all()
        )

    def search(
        self, user_id: str, q: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[GapAnalysis], int]:
        """Search gap analyses by resume profile or opportunity ID."""
        query = (
            self.db.query(GapAnalysis)
            .filter(
                GapAnalysis.user_id == user_id,
                (GapAnalysis.resume_profile_id.contains(q))
                | (GapAnalysis.opportunity_id.contains(q)),
            )
            .order_by(GapAnalysis.created_at.desc())
        )
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def delete(self, id: str) -> bool:
        """Delete a gap analysis by ID."""
        item = self.get_by_id(id)
        if item:
            self.db.delete(item)
            self.db.flush()
            return True
        return False

    def count(self, user_id: str) -> int:
        """Count total gap analyses for a user."""
        return (
            self.db.query(GapAnalysis)
            .filter(GapAnalysis.user_id == user_id)
            .count()
        )

    def has_duplicate(
        self, user_id: str, resume_profile_id: str, opportunity_id: str
    ) -> bool:
        """Check if a gap analysis already exists for this combination."""
        return (
            self.db.query(GapAnalysis)
            .filter(
                GapAnalysis.user_id == user_id,
                GapAnalysis.resume_profile_id == resume_profile_id,
                GapAnalysis.opportunity_id == opportunity_id,
            )
            .first()
            is not None
        )


class GapResultRepository(BaseRepository[GapResult]):
    """Repository for GapResult CRUD operations."""

    def __init__(self, db):
        super().__init__(GapResult, db)

    def get_by_gap_analysis_id(self, gap_analysis_id: str) -> List[GapResult]:
        """Get all gap results for a gap analysis."""
        return (
            self.db.query(GapResult)
            .filter(GapResult.gap_analysis_id == gap_analysis_id)
            .order_by(GapResult.category)
            .all()
        )

    def get_by_category(
        self, gap_analysis_id: str, category: str
    ) -> Optional[GapResult]:
        """Get gap result by analysis ID and category."""
        return (
            self.db.query(GapResult)
            .filter(
                GapResult.gap_analysis_id == gap_analysis_id,
                GapResult.category == category,
            )
            .first()
        )

    def create(self, data: dict) -> GapResult:
        """Create a gap result."""
        result = GapResult(**data)
        self.db.add(result)
        self.db.flush()
        return result

    def create_many(self, results: List[dict]) -> List[GapResult]:
        """Create multiple gap results."""
        created = []
        for data in results:
            result = GapResult(**data)
            self.db.add(result)
            created.append(result)
        self.db.flush()
        return created

    def delete_by_gap_analysis_id(self, gap_analysis_id: str) -> bool:
        """Delete all gap results for a gap analysis."""
        self.db.query(GapResult).filter(
            GapResult.gap_analysis_id == gap_analysis_id
        ).delete()
        self.db.flush()
        return True


class RecommendationRepository(BaseRepository[Recommendation]):
    """Repository for Recommendation CRUD operations."""

    def __init__(self, db):
        super().__init__(Recommendation, db)

    def get_by_gap_analysis_id(self, gap_analysis_id: str) -> List[Recommendation]:
        """Get all recommendations for a gap analysis."""
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.gap_analysis_id == gap_analysis_id)
            .order_by(
                Recommendation.priority.desc(),
                Recommendation.category,
            )
            .all()
        )

    def get_by_priority(
        self, gap_analysis_id: str, priority: str
    ) -> List[Recommendation]:
        """Get recommendations by priority."""
        return (
            self.db.query(Recommendation)
            .filter(
                Recommendation.gap_analysis_id == gap_analysis_id,
                Recommendation.priority == priority,
            )
            .order_by(Recommendation.category)
            .all()
        )

    def get_by_category(
        self, gap_analysis_id: str, category: str
    ) -> List[Recommendation]:
        """Get recommendations by category."""
        return (
            self.db.query(Recommendation)
            .filter(
                Recommendation.gap_analysis_id == gap_analysis_id,
                Recommendation.category == category,
            )
            .order_by(Recommendation.priority.desc())
            .all()
        )

    def create(self, data: dict) -> Recommendation:
        """Create a recommendation."""
        rec = Recommendation(**data)
        self.db.add(rec)
        self.db.flush()
        return rec

    def create_many(self, recommendations: List[dict]) -> List[Recommendation]:
        """Create multiple recommendations."""
        created = []
        for data in recommendations:
            rec = Recommendation(**data)
            self.db.add(rec)
            created.append(rec)
        self.db.flush()
        return created

    def delete_by_gap_analysis_id(self, gap_analysis_id: str) -> bool:
        """Delete all recommendations for a gap analysis."""
        self.db.query(Recommendation).filter(
            Recommendation.gap_analysis_id == gap_analysis_id
        ).delete()
        self.db.flush()
        return True

    def count(self, gap_analysis_id: str) -> int:
        """Count recommendations for a gap analysis."""
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.gap_analysis_id == gap_analysis_id)
            .count()
        )
