"""PROCS Resume Management Router.

API endpoints for PROCS resume management.
All routes require admin authentication and are prefixed with /api/procs/resumes.

Follows the dependency chain: Routers → Services → Repositories → Database
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..auth import require_admin
from ..models.identity import User
from ..schemas.procs_resume import (
    ResumeListResponse,
    ResumeDetailResponse,
    ResumeUpdateRequest,
    ResumeUpdateResponse,
    ResumeActionResponse,
    ResumeStatsResponse,
    ResumeStatsOut,
    TemplateListResponse,
    TemplateStatsResponse,
)
from ..services.resume_management_service import ResumeManagementService
from ..services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["PROCS Resumes"])


@router.get("")
def get_resumes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
    sort_by: str = Query("updated_at"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get paginated resume list with filters.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    result = service.get_resumes(
        page=page,
        limit=limit,
        search=search,
        user_id=user_id,
        template_id=template_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return ResumeListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        limit=result["limit"],
        totalPages=result["totalPages"],
    )


@router.get("/stats")
def get_resume_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get resume statistics.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    stats = service.get_resume_stats()

    return ResumeStatsResponse(data=ResumeStatsOut(**stats))


@router.get("/templates")
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all templates.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    templates = service.templates.get_all_templates()

    return TemplateListResponse(
        items=templates,
        total=len(templates),
    )


@router.get("/templates/stats")
def get_template_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get template usage statistics.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    stats = service.get_template_stats()

    return TemplateStatsResponse(items=stats)


@router.get("/analytics")
def get_resume_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get resume analytics.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    stats = service.get_resume_stats()
    template_stats = service.get_template_stats()

    return {
        "stats": stats,
        "templates": template_stats,
    }


@router.get("/{resume_id}")
def get_resume_detail(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get resume detail by ID.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    resume = service.get_resume_detail(resume_id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get sections and versions
    sections = service.get_resume_sections(resume_id)
    versions = service.get_resume_versions(resume_id)

    return ResumeDetailResponse(
        data={
            "id": resume.id,
            "user_id": resume.user_id,
            "title": resume.title,
            "template_id": resume.template_id,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
            "sections": [
                {
                    "id": s.id,
                    "section_type": s.section_type,
                    "content": s.content,
                    "position": s.position,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
                for s in sections
            ],
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "content": v.content,
                    "created_at": v.created_at,
                }
                for v in versions
            ],
        }
    )


@router.put("/{resume_id}")
def update_resume(
    resume_id: str,
    body: ResumeUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update resume details.

    Requires admin role.
    """
    service = ResumeManagementService(db)

    # Filter out None values
    update_data = body.model_dump(exclude_unset=True)

    resume = service.update_resume(resume_id, update_data, current_user.id)

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Audit: log the update
    audit = AuditService(db)
    audit.log_update(
        entity_type="admin_resume",
        entity_id=resume_id,
        new_state=update_data,
        description=f"Updated resume {resume_id}",
    )

    # Get updated resume with sections and versions
    sections = service.get_resume_sections(resume_id)
    versions = service.get_resume_versions(resume_id)

    return ResumeUpdateResponse(
        data={
            "id": resume.id,
            "user_id": resume.user_id,
            "title": resume.title,
            "template_id": resume.template_id,
            "created_at": resume.created_at,
            "updated_at": resume.updated_at,
            "sections": [
                {
                    "id": s.id,
                    "section_type": s.section_type,
                    "content": s.content,
                    "position": s.position,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
                for s in sections
            ],
            "versions": [
                {
                    "id": v.id,
                    "version_number": v.version_number,
                    "content": v.content,
                    "created_at": v.created_at,
                }
                for v in versions
            ],
        }
    )


@router.delete("/{resume_id}")
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete a resume.

    Requires admin role.
    """
    service = ResumeManagementService(db)
    success = service.soft_delete_resume(resume_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Audit: log the deletion
    audit = AuditService(db)
    audit.log_delete(
        entity_type="admin_resume",
        entity_id=resume_id,
        description=f"Deleted resume {resume_id}",
    )

    return ResumeActionResponse(message="Resume deleted successfully")
