"""Career Intelligence Engine - Main Service.

High-level API for resume/cover letter generation.
Coordinates Knowledge, AI Orchestrator, Rules, and Persistence.
"""
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy.orm import Session

from .ai_orchestrator import AIOrchestrator, PipelineResult, TaskType
from .ai_service import UniversalAIService, get_ai_service
# DEPRECATED: PromptBuilder is a legacy stub that emits DeprecationWarning.
# It is passed to AIOrchestrator for backward compatibility. Actual prompt
# construction uses PromptBuilderV2 in ai_orchestrator._build_prompt().
from .prompt_builder import PromptBuilder
from .rules_engine import RulesEngine

logger = logging.getLogger(__name__)


class CareerEngine:
    """Main Career Intelligence Engine service.

    Provides high-level methods for:
    - Resume bullet generation
    - Resume summary generation
    - Cover letter generation
    - Bullet feedback/improvement
    - ATS optimization

    Knowledge is provided via a callable that returns knowledge rules
    from the KnowledgeIntelligenceService. This decouples the engine
    from the specific knowledge source.
    """

    def __init__(
        self,
        provider: Optional[UniversalAIService] = None,
        knowledge_retriever: Optional[Callable] = None,
    ):
        # Initialize AI provider (single universal service)
        if provider is None:
            try:
                self.provider = get_ai_service()
            except Exception as e:
                logger.error("Failed to initialize AI service: %s", e)
                raise
        else:
            self.provider = provider

        # Initialize orchestrator with knowledge retriever
        self.orchestrator = AIOrchestrator(
            provider=self.provider,
            knowledge_retriever=knowledge_retriever,
            prompt_builder=PromptBuilder(),
            rules_engine=RulesEngine(),
        )

    @classmethod
    def from_config(
        cls,
        provider_type: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        knowledge_retriever: Optional[Callable] = None,
    ) -> "CareerEngine":
        """Create CareerEngine from configuration.

        Args:
            provider_type: "openai", "gemini", or "anthropic". Reads AI_PROVIDER env if None.
            api_key: API key for the provider. Reads provider-specific env if None.
            model: Model name (optional). Reads provider-specific env if None.
            knowledge_retriever: Callable that returns knowledge rules from
                KnowledgeIntelligenceService. If None, pipeline runs without knowledge.
        """
        provider = get_ai_service()
        return cls(provider=provider, knowledge_retriever=knowledge_retriever)

    async def generate_resume_bullets(
        self,
        role_title: str,
        company: str,
        responsibilities: str,
        technologies: str,
        achievements: str = "",
        duration: str = "",
        num_bullets: int = 5,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate resume bullet points for a role.

        Pipeline: Knowledge -> Prompt -> AI -> Rules -> Validation
        """
        input_data = {
            "role_title": role_title,
            "company": company,
            "responsibilities": responsibilities,
            "technologies": technologies,
            "achievements": achievements,
            "duration": duration,
            "num_bullets": num_bullets,
        }

        result = await self.orchestrator.run_pipeline(
            task_type=TaskType.RESUME_BULLETS,
            input_data=input_data,
            validate=True,
        )

        # Log to audit if DB available
        if db and user_id:
            self._log_audit(db, user_id, "generate_resume_bullets", input_data, result)

        return result.to_dict()

    async def generate_resume_summary(
        self,
        target_role: str,
        experience_years: int,
        skills: str,
        achievements: str,
        goals: str = "",
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate a professional resume summary."""
        input_data = {
            "target_role": target_role,
            "experience_years": experience_years,
            "skills": skills,
            "achievements": achievements,
            "goals": goals,
        }

        result = await self.orchestrator.run_pipeline(
            task_type=TaskType.RESUME_SUMMARY,
            input_data=input_data,
            validate=True,
        )

        if db and user_id:
            self._log_audit(db, user_id, "generate_resume_summary", input_data, result)

        return result.to_dict()

    async def generate_cover_letter(
        self,
        company: str,
        role_title: str,
        job_description: str,
        my_experience: str,
        why_company: str,
        relevant_skills: str,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Generate a personalized cover letter."""
        input_data = {
            "company": company,
            "role_title": role_title,
            "job_description": job_description,
            "my_experience": my_experience,
            "why_company": why_company,
            "relevant_skills": relevant_skills,
        }

        result = await self.orchestrator.run_pipeline(
            task_type=TaskType.COVER_LETTER,
            input_data=input_data,
            validate=True,
        )

        if db and user_id:
            self._log_audit(db, user_id, "generate_cover_letter", input_data, result)

        return result.to_dict()

    async def get_bullet_feedback(
        self,
        bullet: str,
        context: str,
        role_title: str,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Review and improve a bullet point."""
        input_data = {
            "bullet": bullet,
            "context": context,
            "role_title": role_title,
        }

        result = await self.orchestrator.run_pipeline(
            task_type=TaskType.BULLET_FEEDBACK,
            input_data=input_data,
            validate=True,
        )

        if db and user_id:
            self._log_audit(db, user_id, "get_bullet_feedback", input_data, result)

        return result.to_dict()

    async def optimize_for_ats(
        self,
        content: str,
        job_description: str,
        user_id: Optional[str] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Optimize resume content for ATS systems."""
        input_data = {
            "content": content,
            "job_description": job_description,
        }

        result = await self.orchestrator.run_pipeline(
            task_type=TaskType.ATS_OPTIMIZATION,
            input_data=input_data,
            validate=False,
        )

        if db and user_id:
            self._log_audit(db, user_id, "optimize_for_ats", input_data, result)

        return result.to_dict()

    def _log_audit(
        self,
        db: Session,
        user_id: str,
        action: str,
        input_data: Dict[str, Any],
        result: PipelineResult,
    ):
        """Log AI operation to audit trail."""
        try:
            from app.models.audit import AuditLog

            audit_log = AuditLog(
                id=str(uuid.uuid4()),
                user_id=user_id,
                action=f"ai_{action}",
                entity_type="ai_operation",
                entity_id=str(uuid.uuid4()),
                old_value=None,
                new_value={
                    "task_type": result.task_type.value,
                    "success": result.success,
                    "latency_ms": result.latency_ms,
                    "validation_score": (
                        result.validation.score if result.validation else None
                    ),
                    "input_keys": list(input_data.keys()),
                },
                ip_address=None,
                user_agent="career_engine",
            )
            db.add(audit_log)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log audit: {e}")
            db.rollback()

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base.

        Returns knowledge stats from the knowledge_intelligence repository.
        Falls back to static defaults if DB is unavailable.
        """
        try:
            from app.database import SessionLocal
            from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
            db = SessionLocal()
            try:
                repo = KnowledgeRuleRepository(db)
                active_rules = repo.get_active()
                total_active = len(active_rules)
                by_section = {}
                for rule in active_rules:
                    section = rule.section_name or "general"
                    by_section[section] = by_section.get(section, 0) + 1
                return {
                    "total_active_rules": total_active,
                    "by_section": by_section,
                    "total_pdfs": 4,
                    "note": "For detailed governance stats, use KnowledgeIntelligenceService",
                }
            finally:
                db.close()
        except Exception:
            return {
                "total_active_rules": 0,
                "total_pdfs": 4,
                "note": "DB unavailable, using defaults",
            }
