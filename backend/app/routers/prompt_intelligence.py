"""Prompt Intelligence API router.

Provides endpoints for prompt template management and prompt package building.
No AI execution - only prompt preparation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.schemas import (
    PromptBuildRequest,
    PromptBuildResponse,
    PromptPackageCreate,
    PromptPackageDetailOut,
    PromptPackageListResponse,
    PromptPackageOut,
    PromptTemplateCreate,
    PromptTemplateListResponse,
    PromptTemplateOut,
    PromptTemplateUpdate,
    PromptVersionListResponse,
    PromptVersionOut,
)
from app.services.prompt_intelligence.service import PromptIntelligenceService

router = APIRouter(prefix="/prompt-intelligence", tags=["Prompt Intelligence"])


# ── Template Endpoints ────────────────────────────────────────────────────────

@router.post("/templates", response_model=PromptTemplateOut, status_code=201)
async def create_template(
    data: PromptTemplateCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new prompt template."""
    try:
        service = PromptIntelligenceService(db)
        template = service.create_template(
            template_key=data.template_key,
            name=data.name,
            prompt_type=data.prompt_type,
            category=data.category,
            content=data.content,
            version=data.version,
            variables=data.variables,
            user_id=current_user.id,
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=PromptTemplateListResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List prompt templates."""
    service = PromptIntelligenceService(db)
    items, total = service.get_templates(skip=(page - 1) * size, limit=size)
    return PromptTemplateListResponse(
        items=[PromptTemplateOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/templates/{template_id}", response_model=PromptTemplateOut)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get prompt template by ID."""
    service = PromptIntelligenceService(db)
    template = service.get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=PromptTemplateOut)
async def update_template(
    template_id: str,
    data: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a prompt template."""
    service = PromptIntelligenceService(db)
    template = service.template_repo.update(template_id, data.model_dump(exclude_unset=True))
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a prompt template."""
    service = PromptIntelligenceService(db)
    deleted = service.template_repo.delete(template_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template deleted successfully"}


# ── Package Endpoints ─────────────────────────────────────────────────────────

@router.post("/packages/build", response_model=PromptBuildResponse)
async def build_prompt(
    data: PromptBuildRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Build a prompt package from a gap analysis."""
    try:
        service = PromptIntelligenceService(db)
        result = service.build_prompt(
            user_id=current_user.id,
            gap_analysis_id=data.gap_analysis_id,
            prompt_type=data.prompt_type,
            template_id=data.template_id,
        )
        return PromptBuildResponse(
            message="Prompt package built successfully",
            package_id=result["package"].id,
            is_validated=result["validation"]["is_valid"],
            total_tokens_estimate=result["tokens_estimate"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/packages", response_model=PromptPackageListResponse)
async def list_packages(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List prompt packages for the current user."""
    service = PromptIntelligenceService(db)
    items, total = service.get_packages_by_user(
        current_user.id,
        skip=(page - 1) * size,
        limit=size,
    )
    return PromptPackageListResponse(
        items=[PromptPackageOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/packages/{package_id}", response_model=PromptPackageDetailOut)
async def get_package(
    package_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get prompt package detail."""
    service = PromptIntelligenceService(db)
    package = service.get_package_by_id(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    return PromptPackageDetailOut.model_validate(package)


@router.get("/packages/{package_id}/versions", response_model=PromptVersionListResponse)
async def get_package_versions(
    package_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get version history for a prompt package's template."""
    service = PromptIntelligenceService(db)
    package = service.get_package_by_id(package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    from app.repositories.prompt_intelligence import PromptVersionRepository
    version_repo = PromptVersionRepository(db)
    versions = version_repo.get_by_template_id(package.template_id) if package.template_id else []
    return PromptVersionListResponse(
        items=[PromptVersionOut.model_validate(v) for v in versions],
        total=len(versions),
    )


@router.delete("/packages/{package_id}")
async def delete_package(
    package_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a prompt package."""
    service = PromptIntelligenceService(db)
    deleted = service.package_repo.delete(package_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Package not found")
    return {"message": "Package deleted successfully"}
