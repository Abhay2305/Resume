"""Gap Analysis API router.

Provides endpoints for gap analysis operations.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.gap_analysis import GapAnalysisStatus
from app.schemas import (
    GapAnalysisCreate,
    GapAnalysisAnalyzeResponse,
    GapAnalysisDetailOut,
    GapAnalysisListOut,
    GapAnalysisListResponse,
    GapAnalysisMissingResponse,
    GapAnalysisMatchesResponse,
    GapAnalysisOut,
    GapAnalysisRecommendationsResponse,
    GapResultOut,
    MatchScoresOut,
    MissingItemsOut,
    RecommendationOut,
)
from app.auth import get_current_user
from app.services.gap_analysis.service import GapAnalysisService

router = APIRouter(prefix="/gap-analysis", tags=["Gap Analysis"])


@router.post("/", response_model=GapAnalysisOut, status_code=201)
async def create_gap_analysis(
    data: GapAnalysisCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create a new gap analysis."""
    try:
        service = GapAnalysisService(db)
        analysis = service.create(
            user_id=current_user.id,
            resume_profile_id=data.resume_profile_id,
            opportunity_id=data.opportunity_id,
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{analysis_id}/analyze", response_model=GapAnalysisOut)
async def analyze_gap(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Run the gap analysis pipeline."""
    try:
        service = GapAnalysisService(db)
        analysis = service.analyze(analysis_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=GapAnalysisListResponse)
async def list_gap_analyses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List gap analyses for the current user."""
    service = GapAnalysisService(db)
    items, total = service.get_by_user_id(
        current_user.id,
        skip=(page - 1) * size,
        limit=size,
    )
    return GapAnalysisListResponse(
        items=[GapAnalysisListOut.model_validate(i) for i in items],
        total=total,
        page=page,
        size=size,
    )


@router.get("/{analysis_id}", response_model=GapAnalysisDetailOut)
async def get_gap_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get gap analysis detail with results and recommendations."""
    service = GapAnalysisService(db)
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")

    results = service.get_gap_results(analysis_id)
    recommendations = service.get_recommendations(analysis_id)

    detail = GapAnalysisDetailOut.model_validate(analysis)
    detail.gap_results = [GapResultOut.model_validate(r) for r in results]
    detail.recommendations = [RecommendationOut.model_validate(r) for r in recommendations]

    return detail


@router.get("/{analysis_id}/recommendations", response_model=GapAnalysisRecommendationsResponse)
async def get_recommendations(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get recommendations for a gap analysis."""
    service = GapAnalysisService(db)
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")

    recs = service.get_recommendations(analysis_id)
    return GapAnalysisRecommendationsResponse(
        recommendations=[RecommendationOut.model_validate(r) for r in recs],
        total=len(recs),
    )


@router.get("/{analysis_id}/matches", response_model=GapAnalysisMatchesResponse)
async def get_matches(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get match results for a gap analysis."""
    service = GapAnalysisService(db)
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")

    results = service.get_gap_results(analysis_id)
    return GapAnalysisMatchesResponse(
        gap_results=[GapResultOut.model_validate(r) for r in results],
        total=len(results),
    )


@router.get("/{analysis_id}/missing", response_model=GapAnalysisMissingResponse)
async def get_missing(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get missing items for a gap analysis."""
    service = GapAnalysisService(db)
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")

    missing = service.get_missing_items(analysis_id)
    return GapAnalysisMissingResponse(
        missing_items=MissingItemsOut(
            missing_skills=missing.get("skills", []),
            missing_technologies=missing.get("technology", []),
            missing_certifications=missing.get("certifications", []),
            missing_education=missing.get("education", []),
            missing_keywords=missing.get("keywords", []),
        )
    )


@router.get("/{analysis_id}/scores", response_model=MatchScoresOut)
async def get_scores(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get match scores for a gap analysis."""
    service = GapAnalysisService(db)
    analysis = service.get_by_id(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Gap analysis not found")

    return MatchScoresOut(
        overall_match_score=analysis.overall_match_score,
        skill_match_score=analysis.skill_match_score,
        technology_match_score=analysis.technology_match_score,
        experience_match_score=analysis.experience_match_score,
        education_match_score=analysis.education_match_score,
        certification_match_score=analysis.certification_match_score,
        keyword_match_score=analysis.keyword_match_score,
    )


@router.delete("/{analysis_id}")
async def delete_gap_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a gap analysis."""
    service = GapAnalysisService(db)
    deleted = service.delete(analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Gap analysis not found")
    return {"message": "Gap analysis deleted successfully"}
