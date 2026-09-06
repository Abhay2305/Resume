"""Prompt Intelligence Service.

Orchestrates the complete prompt intelligence pipeline.
No AI execution - only prompt preparation.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.gap_analysis import GapAnalysis, GapResult, Recommendation
from app.models.knowledge_intelligence import KnowledgeContext
from app.models.prompt_intelligence import PromptPackage, PromptTemplate
from app.models.resume_intelligence import ResumeKnowledge
from app.repositories.prompt_intelligence import (
    PromptPackageRepository,
    PromptTemplateRepository,
)
from app.services.audit_service import AuditService
from app.services.prompt_intelligence.validator import PromptValidator
from app.services.prompt_intelligence.version_service import PromptVersionService
from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest


class PromptIntelligenceService:
    """Service for prompt intelligence operations."""

    def __init__(self, db: Session):
        self.db = db
        self.template_repo = PromptTemplateRepository(db)
        self.package_repo = PromptPackageRepository(db)
        self.audit_service = AuditService(db)
        self.prompt_engine = PromptBuilderV2()
        self.validator = PromptValidator()
        self.version_service = PromptVersionService(db)

    def build_prompt(
        self,
        user_id: str,
        gap_analysis_id: str,
        prompt_type: str = "resume_tailoring",
        template_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        gap_analysis = self.db.query(GapAnalysis).filter(GapAnalysis.id == gap_analysis_id).first()
        if not gap_analysis:
            raise ValueError(f"Gap analysis not found: {gap_analysis_id}")

        resume_knowledge = self._get_resume_knowledge(gap_analysis.resume_profile_id)
        opportunity_entities = self._get_opportunity_entities(gap_analysis.opportunity_id)
        opportunity_parsed = self._get_opportunity_parsed_data(gap_analysis.opportunity_id)
        gap_data = self._build_gap_data(gap_analysis)
        knowledge_ctx = self._get_knowledge_context(gap_analysis_id)

        template = None
        if template_id:
            template = self.template_repo.get_by_id(template_id)
        else:
            templates = self.template_repo.get_by_type(prompt_type)
            template = templates[0] if templates else None

        # Build backward-compatible context dicts for DB storage
        resume_ctx = self._build_resume_context(resume_knowledge)
        opportunity_ctx = self._build_opportunity_context(opportunity_entities, opportunity_parsed)

        # Build v2 context and request
        v2_context = self._build_v2_context(
            resume_knowledge=resume_knowledge,
            opportunity_entities=opportunity_entities,
            opportunity_parsed=opportunity_parsed,
            gap_data=gap_data,
            knowledge_ctx=knowledge_ctx,
        )
        request = PromptRequest(
            prompt_type=prompt_type,
            context=v2_context,
            template_id=template.id if template else None,
            user_id=user_id,
        )

        # Use v2 engine to build prompt
        v2_package = self.prompt_engine.build(request)

        # Build package dict for old validator (backward compat)
        package_data = {
            "system_prompt": v2_package.system_prompt,
            "resume_context": resume_ctx,
            "opportunity_context": opportunity_ctx,
            "gap_context": gap_data,
            "knowledge_context": knowledge_ctx,
            "instructions": v2_package.instructions,
            "constraints": v2_package.constraints,
            "output_schema": v2_package.output_schema,
        }

        validation = self.validator.validate(package_data)
        tokens = v2_package.token_estimate

        package = self.package_repo.create({
            "template_id": template.id if template else None,
            "user_id": user_id,
            "gap_analysis_id": gap_analysis_id,
            "prompt_type": prompt_type,
            "system_prompt": v2_package.system_prompt,
            "resume_context": resume_ctx,
            "opportunity_context": opportunity_ctx,
            "gap_context": gap_data,
            "knowledge_context": knowledge_ctx,
            "instructions": v2_package.instructions,
            "constraints": v2_package.constraints,
            "output_schema": v2_package.output_schema,
            "total_tokens_estimate": tokens,
            "is_validated": validation["is_valid"],
            "validation_errors": validation["errors"] if not validation["is_valid"] else None,
            "version": "1.0",
        })

        if template:
            self.version_service.create_version(
                template_id=template.id,
                system_prompt=v2_package.system_prompt,
                changes="Auto-generated from gap analysis",
            )

        self.audit_service.log_create(
            user_id=user_id,
            entity_type="prompt_built",
            entity_id=package.id,
            details={
                "prompt_type": prompt_type,
                "gap_analysis_id": gap_analysis_id,
                "is_validated": validation["is_valid"],
                "tokens_estimate": tokens,
            },
        )

        return {
            "package": package,
            "validation": validation,
            "tokens_estimate": tokens,
        }

    def get_package_by_id(self, package_id: str) -> Optional[PromptPackage]:
        return self.package_repo.get_by_id(package_id)

    def get_packages_by_user(
        self, user_id: str, *, skip: int = 0, limit: int = 20
    ) -> Tuple[List[PromptPackage], int]:
        return self.package_repo.get_by_user_id(user_id, skip=skip, limit=limit)

    def get_template_by_id(self, template_id: str) -> Optional[PromptTemplate]:
        return self.template_repo.get_by_id(template_id)

    def get_templates(
        self, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[PromptTemplate], int]:
        return self.template_repo.get_all(skip=skip, limit=limit)

    def create_template(
        self,
        template_key: str,
        name: str,
        prompt_type: str,
        category: str,
        content: str,
        version: str = "1.0",
        variables: Optional[dict] = None,
        user_id: Optional[str] = None,
    ) -> PromptTemplate:
        existing = self.template_repo.get_by_key(template_key)
        if existing:
            raise ValueError(f"Template with key '{template_key}' already exists")

        template = self.template_repo.create({
            "template_key": template_key,
            "name": name,
            "prompt_type": prompt_type,
            "category": category,
            "content": content,
            "version": version,
            "variables": variables,
        })

        if user_id:
            self.audit_service.log_create(
                user_id=user_id,
                entity_type="prompt_template_created",
                entity_id=template.id,
                details={"template_key": template_key, "name": name},
            )

        return template

    def _get_resume_knowledge(self, resume_profile_id: str) -> Optional[Dict[str, Any]]:
        knowledge = self.db.query(ResumeKnowledge).filter(
            ResumeKnowledge.resume_profile_id == resume_profile_id
        ).first()
        if not knowledge:
            return None
        return {
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
        from app.models.opportunity import OpportunityEntity
        entities = self.db.query(OpportunityEntity).filter(
            OpportunityEntity.opportunity_id == opportunity_id
        ).all()
        return [{"entity_type": e.entity_type, "entity_value": e.entity_value, "is_required": e.is_required} for e in entities]

    def _get_opportunity_parsed_data(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        from app.models.opportunity import ParsedOpportunityData
        parsed = self.db.query(ParsedOpportunityData).filter(
            ParsedOpportunityData.opportunity_id == opportunity_id
        ).first()
        if not parsed:
            return None
        return {
            "responsibilities": parsed.responsibilities or [],
            "benefits": parsed.benefits or [],
            "ats_keywords": parsed.ats_keywords or [],
        }

    def _build_gap_data(self, gap_analysis: GapAnalysis) -> Dict[str, Any]:
        return {
            "overall_match_score": gap_analysis.overall_match_score or 0,
            "skill_match_score": gap_analysis.skill_match_score or 0,
            "technology_match_score": gap_analysis.technology_match_score or 0,
            "experience_match_score": gap_analysis.experience_match_score or 0,
            "education_match_score": gap_analysis.education_match_score or 0,
            "certification_match_score": gap_analysis.certification_match_score or 0,
            "keyword_match_score": gap_analysis.keyword_match_score or 0,
            "total_gaps": gap_analysis.total_gaps or 0,
            "total_recommendations": gap_analysis.total_recommendations or 0,
        }

    def _get_knowledge_context(self, gap_analysis_id: str) -> Optional[Dict[str, Any]]:
        ctx = self.db.query(KnowledgeContext).filter(
            KnowledgeContext.gap_analysis_id == gap_analysis_id
        ).first()
        if not ctx:
            return None
        return {
            "summary_rules": ctx.summary_rules or "[]",
            "experience_rules": ctx.experience_rules or "[]",
            "skills_rules": ctx.skills_rules or "[]",
            "education_rules": ctx.education_rules or "[]",
            "projects_rules": ctx.projects_rules or "[]",
            "certifications_rules": ctx.certifications_rules or "[]",
            "ats_rules": ctx.ats_rules or "[]",
            "formatting_rules": ctx.formatting_rules or "[]",
            "cover_letter_rules": ctx.cover_letter_rules or "[]",
            "citations": ctx.citations or "[]",
        }

    def _build_resume_context(self, resume_knowledge: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build resume context dict for DB storage (backward compat)."""
        if not resume_knowledge:
            return {}
        return {
            "summary": resume_knowledge.get("summary", ""),
            "skills": resume_knowledge.get("skills", []),
            "technologies": resume_knowledge.get("technologies", {}),
            "experience": resume_knowledge.get("experience_summary", {}),
            "education": resume_knowledge.get("education_summary", {}),
            "certifications": resume_knowledge.get("certifications", []),
            "projects": resume_knowledge.get("projects", []),
            "achievements": resume_knowledge.get("achievements", []),
            "total_experience_years": resume_knowledge.get("total_experience_years", 0),
        }

    def _build_opportunity_context(
        self,
        opportunity_entities: List[Dict[str, Any]],
        opportunity_parsed: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build opportunity context dict for DB storage (backward compat)."""
        entities_by_type: Dict[str, List[str]] = {}
        for entity in opportunity_entities:
            etype = entity.get("entity_type", "unknown")
            entities_by_type.setdefault(etype, []).append(entity.get("entity_value", ""))
        parsed = opportunity_parsed or {}
        return {
            "entities": entities_by_type,
            "responsibilities": parsed.get("responsibilities", []),
            "benefits": parsed.get("benefits", []),
            "ats_keywords": parsed.get("ats_keywords", []),
        }

    def _build_v2_context(
        self,
        resume_knowledge: Optional[Dict[str, Any]],
        opportunity_entities: List[Dict[str, Any]],
        opportunity_parsed: Optional[Dict[str, Any]],
        gap_data: Dict[str, Any],
        knowledge_ctx: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Transform DB entities into v2 PromptRequest context format."""
        opportunity = self._build_opportunity_context(opportunity_entities, opportunity_parsed)
        context: Dict[str, Any] = {
            "resume_knowledge": resume_knowledge or {},
            "opportunity": opportunity,
            "gap_analysis": gap_data,
        }
        if knowledge_ctx:
            context["knowledge_context"] = knowledge_ctx
        return context
