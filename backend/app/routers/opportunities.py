"""Opportunity Intelligence Engine router.

API endpoints for managing opportunities and triggering parsing.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models.identity import User
from app.schemas import (
    OpportunityCreate,
    OpportunityDetailOut,
    OpportunityEntityOut,
    OpportunityListOut,
    OpportunityListResponse,
    OpportunityOut,
    OpportunityUpdate,
    ParseTriggerResponse,
)
from app.services.opportunity.service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/", response_model=OpportunityOut)
def create_opportunity(
    data: OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new opportunity (without parsing)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    opportunity = service.create_opportunity(current_user.id, data)
    return opportunity


@router.get("/", response_model=OpportunityListResponse)
def list_opportunities(
    page: int = 1,
    size: int = 20,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List opportunities with pagination and filtering."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    items, total = service.list_opportunities(
        current_user.id, page=page, size=size, status=status
    )

    return OpportunityListResponse(
        items=[OpportunityListOut.from_orm(item) for item in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{opportunity_id}", response_model=OpportunityDetailOut)
def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get opportunity detail with parsed data and entities."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id, current_user.id)

    # Get parsed data
    parsed_data = service.get_parsed_data(opportunity_id, current_user.id)

    # Get entities
    entities = service.get_entities(opportunity_id, current_user.id)

    # Build response
    opp_dict = {
        "id": opportunity.id,
        "user_id": opportunity.user_id,
        "raw_text": opportunity.raw_text,
        "title": opportunity.title,
        "company": opportunity.company,
        "url": opportunity.url,
        "status": opportunity.status,
        "error_message": opportunity.error_message,
        "is_archived": opportunity.is_archived,
        "parser_version": opportunity.parser_version,
        "processing_time_ms": opportunity.processing_time_ms,
        "created_at": opportunity.created_at,
        "updated_at": opportunity.updated_at,
        "parsed_data": parsed_data,
        "entities": entities,
    }

    return opp_dict


@router.put("/{opportunity_id}", response_model=OpportunityOut)
def update_opportunity(
    opportunity_id: str,
    data: OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an opportunity."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    opportunity = service.update_opportunity(opportunity_id, current_user.id, data)
    return opportunity


@router.delete("/{opportunity_id}")
def delete_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete an opportunity."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    service.delete_opportunity(opportunity_id, current_user.id)
    return {"message": "Opportunity deleted successfully"}


@router.post("/{opportunity_id}/parse", response_model=ParseTriggerResponse)
def trigger_parse(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger parsing for an opportunity."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    opportunity = service.trigger_parse(opportunity_id, current_user.id)

    return ParseTriggerResponse(
        message="Opportunity parsed successfully",
        status=opportunity.status,
    )


@router.get("/{opportunity_id}/parsed")
def get_parsed_data(
    opportunity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parsed data for an opportunity."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    parsed_data = service.get_parsed_data(opportunity_id, current_user.id)

    if not parsed_data:
        raise HTTPException(status_code=404, detail="Parsed data not found")

    return {"data": parsed_data}


@router.get("/{opportunity_id}/entities")
def get_entities(
    opportunity_id: str,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get entities for an opportunity."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    service = OpportunityService(db)
    entities = service.get_entities(opportunity_id, current_user.id, entity_type=entity_type)

    return {"data": entities}
