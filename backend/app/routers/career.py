"""Career Intelligence Engine API Router.

Exposes endpoints for resume/cover letter generation.
Uses KnowledgeIntelligenceService for knowledge retrieval.
"""
import logging
from typing import Any, Callable, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.career_engine import CareerEngine
from app.services.knowledge_intelligence.context_builder import KnowledgeContextBuilder
from app.services.knowledge_intelligence.indexer import KnowledgeIndexer
from app.services.knowledge_intelligence.ranker import KnowledgeRanker
from app.services.knowledge_intelligence.retriever import KnowledgeRetriever
from app.repositories.knowledge_intelligence import KnowledgeRuleRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/career", tags=["Career Intelligence"])


# -----------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------


class GenerateBulletsRequest(BaseModel):
    """Request for generating resume bullets."""
    role_title: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    responsibilities: str = Field(..., min_length=1)
    technologies: str = Field(..., min_length=1)
    achievements: str = Field(default="")
    duration: str = Field(default="")
    num_bullets: int = Field(default=5, ge=1, le=10)


class GenerateSummaryRequest(BaseModel):
    """Request for generating resume summary."""
    target_role: str = Field(..., min_length=1, max_length=200)
    experience_years: int = Field(..., ge=0, le=50)
    skills: str = Field(..., min_length=1)
    achievements: str = Field(..., min_length=1)
    goals: str = Field(default="")


class GenerateCoverLetterRequest(BaseModel):
    """Request for generating cover letter."""
    company: str = Field(..., min_length=1, max_length=200)
    role_title: str = Field(..., min_length=1, max_length=200)
    job_description: str = Field(..., min_length=1)
    my_experience: str = Field(..., min_length=1)
    why_company: str = Field(..., min_length=1)
    relevant_skills: str = Field(..., min_length=1)


class BulletFeedbackRequest(BaseModel):
    """Request for bullet feedback."""
    bullet: str = Field(..., min_length=1)
    context: str = Field(default="")
    role_title: str = Field(default="Software Engineer")


class ATSOptimizationRequest(BaseModel):
    """Request for ATS optimization."""
    content: str = Field(..., min_length=1)
    job_description: str = Field(..., min_length=1)


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# -----------------------------------------------------------------------
# Career Engine dependency
# -----------------------------------------------------------------------

# CareerEngine instance (created once, shared across requests)
career_engine: Optional[CareerEngine] = None


def _create_knowledge_retriever(db: Session) -> Callable:
    """Create a knowledge retriever function using KnowledgeIntelligenceService.

    Returns a callable that retrieves knowledge rules from the database
    and returns them as a list of instruction strings.
    """
    rule_repo = KnowledgeRuleRepository(db)
    retriever = KnowledgeRetriever()
    ranker = KnowledgeRanker()
    context_builder = KnowledgeContextBuilder()

    def knowledge_retriever(
        task_type: str,
        job_description: str,
        domains: Optional[List[str]] = None,
    ) -> List[str]:
        """Retrieve knowledge rules as instruction strings.

        Args:
            task_type: The task type (resume_bullets, resume_summary, etc.)
            job_description: Job description or search context.
            domains: Optional domain filter.

        Returns:
            List of knowledge rule instruction strings.
        """
        try:
            # Get all active rules from database
            all_rules = rule_repo.get_active()
            if not all_rules:
                return []

            # Convert to dicts
            rules_dicts = []
            for rule in all_rules:
                rules_dicts.append({
                    "rule_id": rule.rule_key,
                    "source": rule.source,
                    "section_name": rule.section_name,
                    "priority": rule.priority,
                    "category": rule.category,
                    "instruction": rule.instruction,
                    "reason": rule.reason,
                    "examples": rule.examples,
                    "confidence": rule.confidence,
                })

            # Build gap results from job description (simplified)
            gap_results = {
                "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 0},
                "technology": {"categories": {}, "score": 0},
            }

            # Retrieve relevant rules
            retrieved = retriever.retrieve(rules_dicts, gap_results, max_rules=15)

            # Build context
            context = context_builder.build(retrieved)

            # Extract instruction strings from context
            instructions = []
            for section_key in [
                "summary_rules", "experience_rules", "skills_rules",
                "education_rules", "ats_rules", "formatting_rules",
            ]:
                section_rules = context.get(section_key, [])
                if isinstance(section_rules, list):
                    for rule in section_rules:
                        if isinstance(rule, dict) and rule.get("instruction"):
                            instructions.append(rule["instruction"])

            return instructions[:15]  # Cap at 15 rules

        except Exception as e:
            logger.warning("Knowledge retrieval failed: %s", e)
            return []

    return knowledge_retriever


def get_career_engine(db: Session = Depends(get_db)) -> CareerEngine:
    """Get or create the CareerEngine singleton.

    Uses KnowledgeIntelligenceService for knowledge retrieval
    instead of the legacy KnowledgeEngine.
    """
    global career_engine
    if career_engine is None:
        knowledge_retriever = _create_knowledge_retriever(db)
        career_engine = CareerEngine.from_config(
            knowledge_retriever=knowledge_retriever,
        )
    return career_engine


# -----------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------


@router.post("/bullets", response_model=APIResponse)
async def generate_bullets(
    request: GenerateBulletsRequest,
    db: Session = Depends(get_db),
) -> APIResponse:
    """Generate resume bullet points for a role.

    Uses the full Knowledge → Prompt → AI → Rules pipeline.
    """
    engine = get_career_engine(db)

    result = await engine.generate_resume_bullets(
        role_title=request.role_title,
        company=request.company,
        responsibilities=request.responsibilities,
        technologies=request.technologies,
        achievements=request.achievements,
        duration=request.duration,
        num_bullets=request.num_bullets,
        db=db,
    )

    return APIResponse(
        success=result.get("success", False),
        data=result,
        error=result.get("error"),
    )


@router.post("/summary", response_model=APIResponse)
async def generate_summary(
    request: GenerateSummaryRequest,
    db: Session = Depends(get_db),
) -> APIResponse:
    """Generate a professional resume summary."""
    engine = get_career_engine(db)

    result = await engine.generate_resume_summary(
        target_role=request.target_role,
        experience_years=request.experience_years,
        skills=request.skills,
        achievements=request.achievements,
        goals=request.goals,
        db=db,
    )

    return APIResponse(
        success=result.get("success", False),
        data=result,
        error=result.get("error"),
    )


@router.post("/cover-letter", response_model=APIResponse)
async def generate_cover_letter(
    request: GenerateCoverLetterRequest,
    db: Session = Depends(get_db),
) -> APIResponse:
    """Generate a personalized cover letter."""
    engine = get_career_engine(db)

    result = await engine.generate_cover_letter(
        company=request.company,
        role_title=request.role_title,
        job_description=request.job_description,
        my_experience=request.my_experience,
        why_company=request.why_company,
        relevant_skills=request.relevant_skills,
        db=db,
    )

    return APIResponse(
        success=result.get("success", False),
        data=result,
        error=result.get("error"),
    )


@router.post("/bullet-feedback", response_model=APIResponse)
async def get_bullet_feedback(
    request: BulletFeedbackRequest,
    db: Session = Depends(get_db),
) -> APIResponse:
    """Review and improve a resume bullet point."""
    engine = get_career_engine(db)

    result = await engine.get_bullet_feedback(
        bullet=request.bullet,
        context=request.context,
        role_title=request.role_title,
        db=db,
    )

    return APIResponse(
        success=result.get("success", False),
        data=result,
        error=result.get("error"),
    )


@router.post("/ats-optimize", response_model=APIResponse)
async def optimize_for_ats(
    request: ATSOptimizationRequest,
    db: Session = Depends(get_db),
) -> APIResponse:
    """Optimize resume content for ATS systems."""
    engine = get_career_engine(db)

    result = await engine.optimize_for_ats(
        content=request.content,
        job_description=request.job_description,
        db=db,
    )

    return APIResponse(
        success=result.get("success", False),
        data=result,
        error=result.get("error"),
    )


@router.get("/knowledge/stats", response_model=APIResponse)
async def get_knowledge_stats(
    db: Session = Depends(get_db),
) -> APIResponse:
    """Get statistics about the knowledge base."""
    engine = get_career_engine(db)
    stats = engine.get_knowledge_stats()

    return APIResponse(success=True, data=stats)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "career_intelligence"}
