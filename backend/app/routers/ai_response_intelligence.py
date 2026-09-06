"""AI Response Intelligence Engine API router.

Provides endpoints for validating AI responses and retrieving validation results.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import require_auth
from app.schemas import (
    AIResponseChangesResponse,
    AIResponseConfidenceResponse,
    AIResponseDiffResponse,
    AIResponseReportResponse,
    AIResponseValidateRequest,
    AIResponseValidateResponse,
    AIResponseValidationDetailOut,
    AIResponseValidationListOut,
    AIResponseValidationListResponse,
    AIResponseValidationOut,
    ChangeSetOut,
    ConfidenceScoreOut,
    ResumeDiffOut,
    ValidationReportOut,
)
from app.services.ai_response_intelligence.service import AIResponseIntelligenceService

router = APIRouter(prefix="/ai-response", tags=["AI Response Intelligence"])


@router.post("/validate", response_model=AIResponseValidateResponse, status_code=201)
async def validate_ai_response(
    data: AIResponseValidateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Validate an AI response through the full validation pipeline.

    Runs schema, truth, knowledge, and gap validation.
    Generates diffs, change sets, confidence scores, and approval package.
    """
    try:
        service = AIResponseIntelligenceService(db)
        result = service.validate_ai_response(
            user_id=current_user.id,
            ai_execution_id=data.ai_execution_id,
        )
        return AIResponseValidateResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/validations", response_model=AIResponseValidationListResponse)
async def list_validations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """List AI response validations for the current user."""
    service = AIResponseIntelligenceService(db)
    items, total = service.get_validations_by_user(
        current_user.id,
        skip=(page - 1) * size,
        limit=size,
    )
    return AIResponseValidationListResponse(
        items=[AIResponseValidationListOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/validations/{validation_id}", response_model=AIResponseValidationDetailOut)
async def get_validation(
    validation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get AI response validation detail with all sub-records."""
    service = AIResponseIntelligenceService(db)
    validation = service.get_validation(validation_id)
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    if validation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Load related records
    diffs = service.get_validation_diffs(validation_id)
    changes = service.get_validation_changes(validation_id)
    reports = service.get_validation_report(validation_id)
    confidence = service.get_validation_confidence(validation_id)

    result = AIResponseValidationDetailOut.model_validate(validation)
    result.diffs = [ResumeDiffOut.model_validate(d) for d in diffs]
    result.change_sets = [ChangeSetOut.model_validate(c) for c in changes]
    result.validation_reports = [ValidationReportOut.model_validate(r) for r in reports]
    result.confidence_scores = [ConfidenceScoreOut.model_validate(s) for s in confidence]

    return result


@router.get("/validations/{validation_id}/diff", response_model=AIResponseDiffResponse)
async def get_validation_diff(
    validation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get the diff for a validation."""
    service = AIResponseIntelligenceService(db)
    validation = service.get_validation(validation_id)
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    if validation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    diffs = service.get_validation_diffs(validation_id)
    summary = {
        "total_changes": len(diffs),
        "by_type": {},
        "by_section": {},
    }
    for d in diffs:
        summary["by_type"][d.change_type] = summary["by_type"].get(d.change_type, 0) + 1
        summary["by_section"][d.section] = summary["by_section"].get(d.section, 0) + 1

    return AIResponseDiffResponse(
        diffs=[ResumeDiffOut.model_validate(d) for d in diffs],
        summary=summary,
    )


@router.get("/validations/{validation_id}/report", response_model=AIResponseReportResponse)
async def get_validation_report(
    validation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get validation reports for a validation."""
    service = AIResponseIntelligenceService(db)
    validation = service.get_validation(validation_id)
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    if validation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    reports = service.get_validation_report(validation_id)
    overall_valid = all(r.is_valid for r in reports) if reports else False

    return AIResponseReportResponse(
        reports=[ValidationReportOut.model_validate(r) for r in reports],
        overall_valid=overall_valid,
    )


@router.get("/validations/{validation_id}/confidence", response_model=AIResponseConfidenceResponse)
async def get_validation_confidence(
    validation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get confidence scores for a validation."""
    service = AIResponseIntelligenceService(db)
    validation = service.get_validation(validation_id)
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    if validation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    scores = service.get_validation_confidence(validation_id)
    overall = validation.overall_confidence or 0.0

    return AIResponseConfidenceResponse(
        scores=[ConfidenceScoreOut.model_validate(s) for s in scores],
        overall_confidence=overall,
    )


@router.get("/validations/{validation_id}/changes", response_model=AIResponseChangesResponse)
async def get_validation_changes(
    validation_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_auth),
):
    """Get change sets for a validation."""
    service = AIResponseIntelligenceService(db)
    validation = service.get_validation(validation_id)
    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")
    if validation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    changes = service.get_validation_changes(validation_id)
    return AIResponseChangesResponse(
        changes=[ChangeSetOut.model_validate(c) for c in changes],
        total=len(changes),
    )
