"""Resume domain repository.

Provides database access patterns for Resume, ResumeSection, ResumeVersion, and Template.
Extends BaseRepository with domain-specific queries.
"""
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.base import Base
from ..models.resume import Resume, ResumeSection, ResumeVersion, Template
from .base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Repository for Resume entity with domain-specific queries."""

    def __init__(self, db: Session):
        super().__init__(Resume, db)

    def get_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Resume]:
        """Get resumes by user ID."""
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_with_sections(self, resume_id: str) -> Optional[Resume]:
        """Get resume with all sections loaded."""
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def get_with_versions(self, resume_id: str) -> Optional[Resume]:
        """Get resume with version history."""
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def count_by_user(self, user_id: str) -> int:
        """Count resumes by user ID."""
        return (
            self.db.query(func.count(Resume.id))
            .filter(Resume.user_id == user_id)
            .scalar()
        )

    def count_by_template(self, template_id: str) -> int:
        """Count resumes using a specific template."""
        return (
            self.db.query(func.count(Resume.id))
            .filter(Resume.template_id == template_id)
            .scalar()
        )

    def get_recent_resumes(self, limit: int = 10) -> List[Resume]:
        """Get most recently updated resumes."""
        return (
            self.db.query(Resume)
            .order_by(Resume.updated_at.desc())
            .limit(limit)
            .all()
        )

    def search_resumes(
        self,
        search: str,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Resume]:
        """Search resumes by title."""
        query = self.db.query(Resume).filter(
            Resume.title.ilike(f"%{search}%")
        )
        if user_id:
            query = query.filter(Resume.user_id == user_id)
        return query.order_by(Resume.updated_at.desc()).offset(skip).limit(limit).all()

    def get_resumes_with_filters(
        self,
        user_id: Optional[str] = None,
        template_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> List[Resume]:
        """Get resumes with multiple filters."""
        query = self.db.query(Resume)

        if user_id:
            query = query.filter(Resume.user_id == user_id)
        if template_id:
            query = query.filter(Resume.template_id == template_id)
        if search:
            query = query.filter(Resume.title.ilike(f"%{search}%"))

        sort_column = getattr(Resume, sort_by, Resume.updated_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        return query.offset(skip).limit(limit).all()

    def count_with_filters(
        self,
        user_id: Optional[str] = None,
        template_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count resumes with filters."""
        query = self.db.query(func.count(Resume.id))

        if user_id:
            query = query.filter(Resume.user_id == user_id)
        if template_id:
            query = query.filter(Resume.template_id == template_id)
        if search:
            query = query.filter(Resume.title.ilike(f"%{search}%"))

        return query.scalar()


class ResumeSectionRepository(BaseRepository[ResumeSection]):
    """Repository for ResumeSection entity."""

    def __init__(self, db: Session):
        super().__init__(ResumeSection, db)

    def get_by_resume(self, resume_id: str) -> List[ResumeSection]:
        """Get all sections for a resume."""
        return (
            self.db.query(ResumeSection)
            .filter(ResumeSection.resume_id == resume_id)
            .order_by(ResumeSection.position)
            .all()
        )

    def get_by_type(
        self, resume_id: str, section_type: str
    ) -> Optional[ResumeSection]:
        """Get section by resume ID and type."""
        return (
            self.db.query(ResumeSection)
            .filter(
                ResumeSection.resume_id == resume_id,
                ResumeSection.section_type == section_type,
            )
            .first()
        )

    def delete_by_resume(self, resume_id: str) -> None:
        """Delete all sections for a resume."""
        self.db.query(ResumeSection).filter(
            ResumeSection.resume_id == resume_id
        ).delete()


class ResumeVersionRepository(BaseRepository[ResumeVersion]):
    """Repository for ResumeVersion entity."""

    def __init__(self, db: Session):
        super().__init__(ResumeVersion, db)

    def get_by_resume(self, resume_id: str) -> List[ResumeVersion]:
        """Get all versions for a resume."""
        return (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.version_number.desc())
            .all()
        )

    def get_latest_version(self, resume_id: str) -> Optional[ResumeVersion]:
        """Get the latest version for a resume."""
        return (
            self.db.query(ResumeVersion)
            .filter(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.version_number.desc())
            .first()
        )

    def count_versions(self, resume_id: str) -> int:
        """Count versions for a resume."""
        return (
            self.db.query(func.count(ResumeVersion.id))
            .filter(ResumeVersion.resume_id == resume_id)
            .scalar()
        )


class TemplateRepository(BaseRepository[Template]):
    """Repository for Template entity with CMS support."""

    def __init__(self, db: Session):
        super().__init__(Template, db)

    def get_by_category(self, category: str) -> List[Template]:
        """Get templates by category."""
        return (
            self.db.query(Template)
            .filter(Template.category == category)
            .order_by(Template.name)
            .all()
        )

    def get_all_templates(self) -> List[Template]:
        """Get all templates."""
        return self.db.query(Template).order_by(Template.name).all()

    def count_templates(self) -> int:
        """Count total templates."""
        return self.db.query(func.count(Template.id)).scalar()

    def get_published(self) -> List[Template]:
        """Get all published templates for Prompt Resume frontend."""
        return (
            self.db.query(Template)
            .filter(Template.status == "published")
            .order_by(Template.sort_order, Template.name)
            .all()
        )

    def get_by_status(self, status: str) -> List[Template]:
        """Get templates by status."""
        return (
            self.db.query(Template)
            .filter(Template.status == status)
            .order_by(Template.sort_order, Template.name)
            .all()
        )

    def get_paginated(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[List[Template], int]:
        """Get paginated templates with filters."""
        query = self.db.query(Template)

        if search:
            query = query.filter(
                Template.name.ilike(f"%{search}%") |
                Template.id.ilike(f"%{search}%") |
                Template.description.ilike(f"%{search}%")
            )
        if category:
            query = query.filter(Template.category == category)
        if status:
            query = query.filter(Template.status == status)

        total = query.count()
        items = (
            query.order_by(Template.sort_order, Template.name)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return items, total

    def get_by_slug(self, slug: str) -> Optional[Template]:
        """Get template by slug."""
        return self.db.query(Template).filter(Template.slug == slug).first()

    def slug_exists(self, slug: str, exclude_id: Optional[str] = None) -> bool:
        """Check if slug already exists."""
        query = self.db.query(Template).filter(Template.slug == slug)
        if exclude_id:
            query = query.filter(Template.id != exclude_id)
        return query.first() is not None

    def increment_usage(self, template_id: str) -> None:
        """Increment usage count for a template."""
        template = self.get(template_id)
        if template:
            template.usage_count = (template.usage_count or 0) + 1
            self.db.commit()

    def reorder(self, template_ids: List[str]) -> None:
        """Reorder templates by setting sort_order."""
        for idx, tid in enumerate(template_ids):
            template = self.get(tid)
            if template:
                template.sort_order = idx
        self.db.commit()
