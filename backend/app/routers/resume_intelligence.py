"""Resume Intelligence Engine router.

API endpoints for managing resume profiles and triggering parsing.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.identity import User
from app.schemas import (
    ResumeIntelligenceCreate,
    ResumeIntelligenceDetailOut,
    ResumeIntelligenceListOut,
    ResumeIntelligenceListResponse,
    ResumeIntelligenceOut,
    ResumeIntelligenceParseResponse,
    ResumeIntelligenceUpdate,
)
from app.services.resume_intelligence.service import ResumeIntelligenceService

router = APIRouter(prefix="/resume-intelligence", tags=["Resume Intelligence"])


@router.post("/", response_model=ResumeIntelligenceOut)
def create_profile(
    data: ResumeIntelligenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resume profile (without parsing)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    profile = service.create_profile(current_user.id, data)
    return profile


@router.get("/", response_model=ResumeIntelligenceListResponse)
def list_profiles(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List resume profiles with pagination and filtering."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    items, total = service.list_profiles(
        current_user.id, page=page, size=size, status=status
    )

    return ResumeIntelligenceListResponse(
        items=[ResumeIntelligenceListOut.from_orm(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{profile_id}", response_model=ResumeIntelligenceDetailOut)
def get_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get resume profile detail with parsed data, entities, and knowledge."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    profile = service.get_profile(profile_id, current_user.id)

    parsed_data = service.get_parsed_data(profile_id, current_user.id)
    entities = service.get_entities(profile_id, current_user.id)
    knowledge = service.get_knowledge(profile_id, current_user.id)

    profile_dict = {
        "id": profile.id,
        "user_id": profile.user_id,
        "raw_text": profile.raw_text,
        "title": profile.title,
        "status": profile.status,
        "error_message": profile.error_message,
        "is_archived": profile.is_archived,
        "parser_version": profile.parser_version,
        "processing_time_ms": profile.processing_time_ms,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
        "parsed_data": parsed_data,
        "entities": entities,
        "knowledge": knowledge,
    }

    return profile_dict


@router.put("/{profile_id}", response_model=ResumeIntelligenceOut)
def update_profile(
    profile_id: str,
    data: ResumeIntelligenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    profile = service.update_profile(profile_id, current_user.id, data)
    return profile


@router.delete("/{profile_id}")
def delete_profile(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    service.delete_profile(profile_id, current_user.id)
    return {"message": "Resume profile deleted successfully"}


@router.post("/{profile_id}/parse", response_model=ResumeIntelligenceParseResponse)
def trigger_parse(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger parsing for a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    profile = service.trigger_parse(profile_id, current_user.id)

    return ResumeIntelligenceParseResponse(
        message="Resume parsed successfully",
        status=profile.status,
    )


@router.get("/{profile_id}/parsed")
def get_parsed_data(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parsed data for a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    parsed_data = service.get_parsed_data(profile_id, current_user.id)

    if not parsed_data:
        raise HTTPException(status_code=404, detail="Parsed data not found")

    return {"data": parsed_data}


@router.get("/{profile_id}/entities")
def get_entities(
    profile_id: str,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get entities for a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    entities = service.get_entities(profile_id, current_user.id, entity_type=entity_type)

    return {"data": entities}


@router.get("/{profile_id}/knowledge")
def get_knowledge(
    profile_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Resume Knowledge for a resume profile."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = ResumeIntelligenceService(db)
    knowledge = service.get_knowledge(profile_id, current_user.id)

    if not knowledge:
        raise HTTPException(status_code=404, detail="Resume knowledge not found")

    return {"data": knowledge}
