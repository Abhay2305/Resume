"""PROCS Resume Management Service.

Business logic layer for PROCS resume management operations.
Follows the service pattern defined in PROCS_Development_Guide.md Section 5.4.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.resume import Resume, ResumeSection, ResumeVersion, Template
from ..repositories.resume import (
    ResumeRepository,
    ResumeSectionRepository,
    ResumeVersionRepository,
    TemplateRepository,
)
from ..services.audit_service import AuditService
from ..services.error_service import ErrorService

logger = logging.getLogger(__name__)


class ResumeManagementService:
    """Service for PROCS resume management operations.

    Provides business logic for resume listing, inspection, updates, and analytics.
    Integrates with AuditService and ErrorService for observability.
    """

    def __init__(self, db: Session):
        self.db = db
        self.resumes = ResumeRepository(db)
        self.sections = ResumeSectionRepository(db)
        self.versions = ResumeVersionRepository(db)
        self.templates = TemplateRepository(db)
        self.audit = AuditService(db)
        self.error = ErrorService(db)

    def get_resumes(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        user_id: Optional[str] = None,
        template_id: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """Get paginated resume list with filters.

        Args:
            page: Page number (1-indexed)
            limit: Items per page
            search: Search term for title
            user_id: Filter by user ID
            template_id: Filter by template ID
            sort_by: Field to sort by
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Dict with items, total, page, limit, totalPages
        """
        try:
            page = max(1, page)
            limit = max(1, min(limit, 100))
            offset = (page - 1) * limit

            items = self.resumes.get_resumes_with_filters(
                user_id=user_id,
                template_id=template_id,
                search=search,
                skip=offset,
                limit=limit,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            total = self.resumes.count_with_filters(
                user_id=user_id,
                template_id=template_id,
                search=search,
            )

            total_pages = max(1, (total + limit - 1) // limit)

            return {
                "items": items,
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": total_pages,
            }
        except Exception as e:
            logger.error("Failed to get resumes: %s", e)
            self.error.log_exception(e, context={"operation": "get_resumes"})
            raise

    def get_resume_detail(self, resume_id: str) -> Optional[Resume]:
        """Get resume detail by ID.

        Args:
            resume_id: Resume ID

        Returns:
            Resume object or None if not found
        """
        try:
            resume = self.resumes.get(resume_id)
            if not resume:
                return None
            return resume
        except Exception as e:
            logger.error("Failed to get resume detail: %s", e)
            self.error.log_exception(
                e, context={"operation": "get_resume_detail", "resume_id": resume_id}
            )
            raise

    def get_resume_sections(self, resume_id: str) -> List[ResumeSection]:
        """Get resume sections.

        Args:
            resume_id: Resume ID

        Returns:
            List of ResumeSection objects
        """
        try:
            return self.sections.get_by_resume(resume_id)
        except Exception as e:
            logger.error("Failed to get resume sections: %s", e)
            return []

    def get_resume_versions(self, resume_id: str) -> List[ResumeVersion]:
        """Get resume version history.

        Args:
            resume_id: Resume ID

        Returns:
            List of ResumeVersion objects
        """
        try:
            return self.versions.get_by_resume(resume_id)
        except Exception as e:
            logger.error("Failed to get resume versions: %s", e)
            return []

    def update_resume(
        self,
        resume_id: str,
        data: Dict[str, Any],
        admin_id: str,
    ) -> Optional[Resume]:
        """Update resume details.

        Args:
            resume_id: Resume ID to update
            data: Update data
            admin_id: ID of admin performing the update

        Returns:
            Updated Resume object or None if not found
        """
        try:
            resume = self.resumes.get(resume_id)
            if not resume:
                return None

            # Store old state for audit
            old_state = {
                "title": resume.title,
                "template_id": resume.template_id,
            }

            # Update fields
            for field, value in data.items():
                if hasattr(resume, field) and value is not None:
                    setattr(resume, field, value)

            resume.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(resume)

            # Audit log
            self.audit.log_update(
                entity_type="Resume",
                entity_id=resume_id,
                old_state=old_state,
                new_state=data,
                user_id=admin_id,
            )

            return resume
        except Exception as e:
            logger.error("Failed to update resume: %s", e)
            self.error.log_exception(
                e, context={"operation": "update_resume", "resume_id": resume_id}
            )
            self.db.rollback()
            raise

    def soft_delete_resume(self, resume_id: str, admin_id: str) -> bool:
        """Soft delete a resume.

        Args:
            resume_id: Resume ID to delete
            admin_id: ID of admin performing the deletion

        Returns:
            True if deleted, False if not found
        """
        try:
            resume = self.resumes.get(resume_id)
            if not resume:
                return False

            # Hard delete (resumes are recoverable via version history)
            self.db.delete(resume)
            self.db.commit()

            # Audit log
            self.audit.log_delete(
                entity_type="Resume",
                entity_id=resume_id,
                user_id=admin_id,
            )

            return True
        except Exception as e:
            logger.error("Failed to delete resume: %s", e)
            self.error.log_exception(
                e, context={"operation": "soft_delete_resume", "resume_id": resume_id}
            )
            self.db.rollback()
            raise

    def get_resume_stats(self) -> Dict[str, int]:
        """Get resume statistics.

        Returns:
            Dict with resume counts
        """
        try:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            month_start = today_start - timedelta(days=30)

            total = self.db.query(func.count(Resume.id)).scalar() or 0
            new_today = (
                self.db.query(func.count(Resume.id))
                .filter(Resume.created_at >= today_start)
                .scalar()
                or 0
            )
            new_week = (
                self.db.query(func.count(Resume.id))
                .filter(Resume.created_at >= week_start)
                .scalar()
                or 0
            )
            new_month = (
                self.db.query(func.count(Resume.id))
                .filter(Resume.created_at >= month_start)
                .scalar()
                or 0
            )
            total_templates = self.templates.count_templates()

            return {
                "total_resumes": total,
                "new_resumes_today": new_today,
                "new_resumes_this_week": new_week,
                "new_resumes_this_month": new_month,
                "total_templates": total_templates,
            }
        except Exception as e:
            logger.error("Failed to get resume stats: %s", e)
            return {
                "total_resumes": 0,
                "new_resumes_today": 0,
                "new_resumes_this_week": 0,
                "new_resumes_this_month": 0,
                "total_templates": 0,
            }

    def get_template_stats(self) -> List[Dict[str, Any]]:
        """Get template usage statistics.

        Returns:
            List of template stats
        """
        try:
            templates = self.templates.get_all_templates()
            stats = []
            for template in templates:
                count = self.resumes.count_by_template(template.id)
                stats.append(
                    {
                        "id": template.id,
                        "name": template.name,
                        "category": template.category,
                        "usage_count": count,
                    }
                )
            return sorted(stats, key=lambda x: x["usage_count"], reverse=True)
        except Exception as e:
            logger.error("Failed to get template stats: %s", e)
            return []
