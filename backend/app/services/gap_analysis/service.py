"""Gap Analysis Service.

Orchestrates the complete gap analysis pipeline.
No AI involved.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from app.models.gap_analysis import GapAnalysis, GapResult, GapAnalysisStatus
from app.models.opportunity import Opportunity, OpportunityEntity, ParsedOpportunityData
from app.models.resume_intelligence import ResumeProfile, ResumeKnowledge
from app.repositories.gap_analysis import (
    GapAnalysisRepository,
    GapResultRepository,
    RecommendationRepository,
)
from app.services.audit_service import AuditService
from app.services.gap_analysis.analyzers.gap_analyzer import GapAnalyzerOrchestrator
from app.services.gap_analysis.match_scorer import MatchScorer
from app.services.gap_analysis.recommendation_engine import RecommendationEngine


class GapAnalysisService:
    """Service for gap analysis operations."""

    def __init__(self, db: Session):
        self.db = db
        self.gap_analysis_repo = GapAnalysisRepository(db)
        self.gap_result_repo = GapResultRepository(db)
        self.recommendation_repo = RecommendationRepository(db)
        self.audit_service = AuditService(db)
        self.analyzer = GapAnalyzerOrchestrator()
        self.scorer = MatchScorer()
        self.recommendation_engine = RecommendationEngine()

    def create(
        self,
        user_id: str,
        resume_profile_id: str,
        opportunity_id: str,
    ) -> GapAnalysis:
        """Create a new gap analysis."""
        existing = self.gap_analysis_repo.get_by_resume_and_opportunity(
            resume_profile_id, opportunity_id
        )
        if existing:
            raise ValueError("Gap analysis already exists for this resume-opportunity pair")

        resume_profile = self.db.query(ResumeProfile).filter(
            ResumeProfile.id == resume_profile_id
        ).first()
        if not resume_profile:
            raise ValueError(f"Resume profile not found: {resume_profile_id}")

        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        if not opportunity:
            raise ValueError(f"Opportunity not found: {opportunity_id}")

        analysis = GapAnalysis(
            user_id=user_id,
            resume_profile_id=resume_profile_id,
            opportunity_id=opportunity_id,
            status=GapAnalysisStatus.PENDING,
        )
        analysis = self.gap_analysis_repo.create(analysis.__dict__)

        self.audit_service.log_create(
            user_id=user_id,
            entity_type="gap_analysis",
            entity_id=analysis.id,
            details={
                "resume_profile_id": resume_profile_id,
                "opportunity_id": opportunity_id,
            },
        )

        return analysis

    def analyze(self, analysis_id: str) -> GapAnalysis:
        """Run the gap analysis pipeline."""
        analysis = self.gap_analysis_repo.get_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"Gap analysis not found: {analysis_id}")

        if analysis.status == GapAnalysisStatus.COMPLETED:
            return analysis

        start_time = datetime.utcnow()

        try:
            analysis.status = GapAnalysisStatus.ANALYZING
            self.db.commit()

            resume_knowledge = self._get_resume_knowledge(analysis.resume_profile_id)
            opportunity_entities = self._get_opportunity_entities(analysis.opportunity_id)
            opportunity_parsed_data = self._get_opportunity_parsed_data(analysis.opportunity_id)

            gap_results = self.analyzer.analyze(
                resume_knowledge, opportunity_entities, opportunity_parsed_data
            )

            scores = self.scorer.calculate_scores(gap_results)

            recommendations = self.recommendation_engine.generate(
                gap_results, resume_knowledge, opportunity_entities
            )

            for category, result_data in gap_results.items():
                self.gap_result_repo.create({
                    "gap_analysis_id": analysis_id,
                    "category": category,
                    "match_score": result_data.get("score"),
                    "matched_items": str(result_data.get("matched", [])),
                    "missing_items": str(result_data.get("missing", [])),
                    "partial_items": str(result_data.get("partial", [])),
                    "extra_items": str(result_data.get("extra", [])),
                    "details": str(result_data),
                })

            for rec in recommendations:
                self.recommendation_repo.create({
                    "gap_analysis_id": analysis_id,
                    "category": rec["category"],
                    "priority": rec["priority"],
                    "action": rec["action"],
                    "description": rec["description"],
                    "target_item": rec.get("target_item"),
                })

            end_time = datetime.utcnow()
            processing_time = int((end_time - start_time).total_seconds() * 1000)

            analysis.status = GapAnalysisStatus.COMPLETED
            analysis.overall_match_score = scores["overall_match_score"]
            analysis.skill_match_score = scores["skill_match_score"]
            analysis.technology_match_score = scores["technology_match_score"]
            analysis.experience_match_score = scores["experience_match_score"]
            analysis.education_match_score = scores["education_match_score"]
            analysis.certification_match_score = scores["certification_match_score"]
            analysis.keyword_match_score = scores["keyword_match_score"]
            analysis.total_gaps = sum(
                len(result_data.get("missing", []))
                for result_data in gap_results.values()
            )
            analysis.total_matches = sum(
                len(result_data.get("matched", []))
                for result_data in gap_results.values()
            )
            analysis.total_recommendations = len(recommendations)
            analysis.processing_time_ms = processing_time
            self.db.commit()

            self.audit_service.log_create(
                user_id=analysis.user_id,
                entity_type="gap_analysis_completed",
                entity_id=analysis.id,
                details={
                    "overall_score": scores["overall_match_score"],
                    "total_gaps": analysis.total_gaps,
                    "total_recommendations": analysis.total_recommendations,
                    "processing_time_ms": processing_time,
                },
            )

        except Exception as e:
            analysis.status = GapAnalysisStatus.FAILED
            analysis.error_message = str(e)
            self.db.commit()
            raise

        return analysis

    def get_by_id(self, analysis_id: str) -> Optional[GapAnalysis]:
        """Get gap analysis by ID."""
        return self.gap_analysis_repo.get_by_id(analysis_id)

    def get_by_user_id(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[GapAnalysis], int]:
        """Get gap analyses for a user."""
        return self.gap_analysis_repo.get_by_user_id(user_id, skip=skip, limit=limit)

    def get_gap_results(self, analysis_id: str) -> List[GapResult]:
        """Get all gap results for an analysis."""
        return self.gap_result_repo.get_by_gap_analysis_id(analysis_id)

    def get_recommendations(self, analysis_id: str) -> List[GapResult]:
        """Get all recommendations for an analysis."""
        return self.recommendation_repo.get_by_gap_analysis_id(analysis_id)

    def get_missing_items(self, analysis_id: str) -> Dict[str, List[str]]:
        """Get all missing items grouped by category."""
        results = self.gap_result_repo.get_by_gap_analysis_id(analysis_id)
        missing = {}
        for result in results:
            if result.missing_items:
                try:
                    items = json.loads(result.missing_items)
                    if items:
                        missing[result.category] = items
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning("Failed to parse missing_items JSON for category %s: %s", result.category, e)
        return missing

    def delete(self, analysis_id: str) -> bool:
        """Delete a gap analysis."""
        analysis = self.gap_analysis_repo.get_by_id(analysis_id)
        if not analysis:
            return False

        self.recommendation_repo.delete_by_gap_analysis_id(analysis_id)
        self.gap_result_repo.delete_by_gap_analysis_id(analysis_id)
        self.gap_analysis_repo.delete(analysis_id)

        self.audit_service.log_create(
            user_id=analysis.user_id,
            entity_type="gap_analysis_deleted",
            entity_id=analysis_id,
            details={"deleted_at": datetime.utcnow().isoformat()},
        )

        return True

    def _get_resume_knowledge(self, resume_profile_id: str) -> Dict[str, Any]:
        """Get resume knowledge as a dictionary."""
        knowledge = self.db.query(ResumeKnowledge).filter(
            ResumeKnowledge.resume_profile_id == resume_profile_id
        ).first()

        if not knowledge:
            return {}

        return {
            "personal_info": knowledge.personal_info or {},
            "contact_info": knowledge.contact_info or {},
            "summary": knowledge.summary or "",
            "skills": knowledge.skills or [],
            "technologies": knowledge.technologies or {},
            "experience_summary": knowledge.experience_summary or {},
            "education_summary": knowledge.education_summary or {},
            "certifications": knowledge.certifications or [],
            "projects": knowledge.projects or [],
            "achievements": knowledge.achievements or [],
            "total_experience_years": knowledge.total_experience_years or 0,
        }

    def _get_opportunity_entities(self, opportunity_id: str) -> List[Dict[str, Any]]:
        """Get opportunity entities as a list of dictionaries."""
        entities = self.db.query(OpportunityEntity).filter(
            OpportunityEntity.opportunity_id == opportunity_id
        ).all()

        return [
            {
                "entity_type": e.entity_type,
                "entity_value": e.entity_value,
                "is_required": e.is_required,
            }
            for e in entities
        ]

    def _get_opportunity_parsed_data(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        """Get opportunity parsed data as a dictionary."""
        parsed = self.db.query(ParsedOpportunityData).filter(
            ParsedOpportunityData.opportunity_id == opportunity_id
        ).first()

        if not parsed:
            return None

        return {
            "responsibilities": parsed.responsibilities or [],
            "benefits": parsed.benefits or [],
            "ats_keywords": parsed.ats_keywords or [],
            "raw_sections": parsed.raw_sections or {},
        }
