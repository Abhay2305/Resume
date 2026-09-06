"""Knowledge Intelligence API router.

Provides endpoints for knowledge document management, retrieval, and governance.
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.database import get_db
from app.auth import get_current_user, require_role
from app.schemas import (
    KnowledgeContextDetailOut,
    KnowledgeContextResponse,
    KnowledgeDocumentCreate,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentOut,
    KnowledgeDocumentUpdate,
    KnowledgeGovernanceStatsResponse,
    KnowledgeRuleCreate,
    KnowledgeRuleGovernanceResponse,
    KnowledgeRuleListByStateResponse,
    KnowledgeRuleListResponse,
    KnowledgeRuleOut,
    KnowledgeRetrieveRequest,
    KnowledgeRetrieveResponse,
    KnowledgeRetrievalOut,
)
from app.services.knowledge_intelligence.service import KnowledgeIntelligenceService
from app.services.knowledge_intelligence.document_service import KnowledgeDocumentService

router = APIRouter(prefix="/knowledge", tags=["Knowledge Intelligence"])


@router.post("/documents", response_model=KnowledgeDocumentOut, status_code=201)
async def create_document(
    data: KnowledgeDocumentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Register a new knowledge document."""
    try:
        service = KnowledgeDocumentService(db)
        doc = service.register(
            document_key=data.document_key,
            name=data.name,
            source=data.source,
            document_type=data.document_type,
            version=data.version,
            description=data.description,
            confidence=data.confidence,
            user_id=current_user.id,
        )
        return doc
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents", response_model=KnowledgeDocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List knowledge documents."""
    service = KnowledgeDocumentService(db)
    items, total = service.get_all(skip=(page - 1) * size, limit=size)
    return KnowledgeDocumentListResponse(
        items=[KnowledgeDocumentOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentOut)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get knowledge document by ID."""
    service = KnowledgeDocumentService(db)
    doc = service.get_by_id(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.put("/documents/{document_id}", response_model=KnowledgeDocumentOut)
async def update_document(
    document_id: str,
    data: KnowledgeDocumentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a knowledge document."""
    service = KnowledgeDocumentService(db)
    doc = service.update(
        document_id,
        name=data.name,
        version=data.version,
        description=data.description,
        confidence=data.confidence,
        is_active=data.is_active,
        user_id=current_user.id,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a knowledge document."""
    service = KnowledgeDocumentService(db)
    deleted = service.delete(document_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}


@router.post("/retrieve", response_model=KnowledgeRetrieveResponse)
async def retrieve_knowledge(
    data: KnowledgeRetrieveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Retrieve relevant knowledge based on gap analysis."""
    try:
        service = KnowledgeIntelligenceService(db)
        result = service.retrieve_knowledge(
            gap_analysis_id=data.gap_analysis_id,
            user_id=current_user.id,
        )
        return KnowledgeRetrieveResponse(
            message="Knowledge retrieved successfully",
            retrieval_id=result["retrieval"].id,
            total_rules=result["retrieval"].total_rules_retrieved,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", response_model=KnowledgeRuleListResponse)
async def list_rules(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List knowledge rules."""
    service = KnowledgeIntelligenceService(db)
    if q:
        items, total = service.search_rules(q, skip=(page - 1) * size, limit=size)
    else:
        items, total = service.get_all_rules(skip=(page - 1) * size, limit=size)
    return KnowledgeRuleListResponse(
        items=[KnowledgeRuleOut(**i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/rules/{rule_id}", response_model=KnowledgeRuleOut)
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get knowledge rule by ID."""
    service = KnowledgeIntelligenceService(db)
    rule = service.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return KnowledgeRuleOut(**rule)


@router.get("/context/{gap_analysis_id}", response_model=KnowledgeContextResponse)
async def get_context(
    gap_analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get knowledge context for a gap analysis."""
    service = KnowledgeIntelligenceService(db)
    context = service.get_context_by_gap_analysis(gap_analysis_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found for this gap analysis")

    citations = []
    try:
        citations = json.loads(context.citations) if context.citations else []
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Failed to parse citations JSON: %s", e)

    return KnowledgeContextResponse(
        context=KnowledgeContextDetailOut.model_validate(context),
        total_rules=context.total_rules,
        citations=citations,
    )


# ============================================================================
# Governance Endpoints
# ============================================================================

@router.get("/rules/by-state/{state}", response_model=KnowledgeRuleListByStateResponse)
async def list_rules_by_state(
    state: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List knowledge rules filtered by governance state.

    Valid states: DISCOVERED, EXTRACTED, CLASSIFIED, VERIFIED, APPROVED, ACTIVE, VERSIONED, AUDITED, REJECTED.
    """
    valid_states = {"DISCOVERED", "EXTRACTED", "CLASSIFIED", "VERIFIED", "APPROVED", "ACTIVE", "VERSIONED", "AUDITED", "REJECTED"}
    if state.upper() not in valid_states:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state '{state}'. Valid states: {', '.join(sorted(valid_states))}"
        )
    service = KnowledgeIntelligenceService(db)
    items, total = service.list_rules_by_state(
        state.upper(), skip=(page - 1) * size, limit=size
    )
    return KnowledgeRuleListByStateResponse(
        items=[KnowledgeRuleOut(**i) for i in items],
        total=total,
        page=page,
        size=size,
        state=state.upper(),
    )


@router.get("/governance/stats", response_model=KnowledgeGovernanceStatsResponse)
async def get_governance_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get governance statistics: rule counts by state and source."""
    service = KnowledgeIntelligenceService(db)
    stats = service.get_governance_stats()
    return KnowledgeGovernanceStatsResponse(**stats)


@router.post("/rules/{rule_id}/approve", response_model=KnowledgeRuleGovernanceResponse)
async def approve_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Approve a knowledge rule: VERIFIED → APPROVED.

    Requires admin role. Enforces provenance validation for PDF-derived rules.
    """
    service = KnowledgeIntelligenceService(db)
    try:
        result = service.approve_rule(rule_id, current_user.id)
        return KnowledgeRuleGovernanceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to approve rule: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/activate", response_model=KnowledgeRuleGovernanceResponse)
async def activate_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Activate a knowledge rule: APPROVED → ACTIVE.

    Requires admin role. Only APPROVED rules can be activated.
    """
    service = KnowledgeIntelligenceService(db)
    try:
        result = service.activate_rule(rule_id, current_user.id)
        return KnowledgeRuleGovernanceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to activate rule: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/deactivate", response_model=KnowledgeRuleGovernanceResponse)
async def deactivate_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Deactivate a knowledge rule: sets is_active=False.

    Requires admin role. The rule remains in its current state
    but is removed from runtime retrieval.
    """
    service = KnowledgeIntelligenceService(db)
    try:
        result = service.deactivate_rule(rule_id, current_user.id)
        return KnowledgeRuleGovernanceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to deactivate rule: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/{rule_id}/reject", response_model=KnowledgeRuleGovernanceResponse)
async def reject_rule(
    rule_id: str,
    reason: str = Query("", description="Rejection reason"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    """Reject a knowledge rule: transitions to REJECTED state.

    Requires admin role. Rejected rules are excluded from runtime.
    """
    service = KnowledgeIntelligenceService(db)
    try:
        result = service.reject_rule(rule_id, current_user.id, reason=reason)
        return KnowledgeRuleGovernanceResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to reject rule: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
