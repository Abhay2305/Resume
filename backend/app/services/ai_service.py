"""Universal AI Service — backward-compatibility re-export layer.

All symbols are re-exported from the decomposed `app.services.ai` package.
Existing callers continue working without modification.
"""

import logging
import traceback
from typing import Any, Dict, List, Optional

from app.services.ai.types import ProviderType, ProviderConfig, ProviderResponse, ProviderMetrics
from app.services.ai.error_classifier import (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    TimeoutError as AITimeoutError,
    ProviderUnavailableError,
    InvalidResponseError,
    ResponseParsingError,
    ConfigurationError,
    TokenBudgetExceeded,
)
from app.services.ai.cost_tracker import MODEL_COSTS, estimate_cost
from app.services.ai.provider_registry import _load_config, validate_provider_config, log_provider_info
from app.services.ai.utils import run_async
from app.services.ai.universal_service import UniversalAIService, get_ai_service, reset_ai_service
from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest

logger = logging.getLogger(__name__)

# Re-export all public symbols for backward compatibility
__all__ = [
    "ProviderType",
    "ProviderConfig",
    "ProviderResponse",
    "ProviderMetrics",
    "ProviderError",
    "AuthenticationError",
    "RateLimitError",
    "AITimeoutError",
    "TimeoutError",
    "ProviderUnavailableError",
    "InvalidResponseError",
    "ResponseParsingError",
    "ConfigurationError",
    "TokenBudgetExceeded",
    "MODEL_COSTS",
    "estimate_cost",
    "_load_config",
    "validate_provider_config",
    "log_provider_info",
    "run_async",
    "UniversalAIService",
    "get_ai_service",
    "reset_ai_service",
    "ResumeGeneratorService",
    "CoverLetterGeneratorService",
    "ATSScoreService",
    "get_knowledge_rules_for_context",
    "validate_resume_output",
]

# Alias for backward compat: code importing `TimeoutError` from this module
# should get the AI timeout error, not the builtin.
TimeoutError = AITimeoutError

# Prompt Intelligence v2 engine for prompt construction
prompt_engine = PromptBuilderV2()


def get_knowledge_rules_for_context(
    db,
    section_name: Optional[str] = None,
    max_rules: int = 15,
) -> List[Dict[str, Any]]:
    """Retrieve active knowledge rules from knowledge_intelligence for prompt injection.

    Returns a list of rule dicts suitable for PromptBuilderV2's knowledge_rules
    context parameter. Each dict contains: instruction, section_name, source, category.

    Args:
        db: SQLAlchemy database session.
        section_name: Optional section filter (e.g., 'summary', 'experience').
        max_rules: Maximum rules to return (default 15, matching InstructionComposer cap).

    Returns:
        List of knowledge rule dicts, or empty list if unavailable.
    """
    try:
        from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
        repo = KnowledgeRuleRepository(db)
        rules = repo.get_active()
        rule_dicts = []
        for r in rules:
            if section_name and r.section_name and r.section_name.lower() != section_name.lower():
                continue
            rule_dicts.append({
                "instruction": r.instruction,
                "section_name": r.section_name or "general",
                "source": r.source or "knowledge_intelligence",
                "category": r.category or "General",
            })
            if len(rule_dicts) >= max_rules:
                break
        return rule_dicts
    except Exception as e:
        logger.warning("Failed to retrieve knowledge rules: %s", e)
        return []


# ---------------------------------------------------------------------------
# Resume output validation utility
# ---------------------------------------------------------------------------

def validate_resume_output(
    structured_data: Dict[str, Any],
    user_text: str,
    db=None,
) -> Optional[Dict[str, Any]]:
    """Validate AI-generated resume output using governed validators.

    Runs schema, truth, and knowledge validation directly against the
    parsed response data. Used by both chat and direct generation paths.

    Returns validation summary dict or None if validation cannot run.
    """
    try:
        from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator
        from app.services.ai_response_intelligence.truth_validator import TruthValidator
        from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator

        schema_val = ResponseSchemaValidator()
        truth_val = TruthValidator()
        knowledge_val = KnowledgeValidator()

        # Schema validation
        schema_valid, schema_score, schema_issues, schema_details = (
            schema_val.validate(structured_data)
        )

        # Truth validation — compare AI output against user-provided text
        resume_knowledge = {"summary": user_text}
        truth_valid, truth_score, truth_issues, truth_details = (
            truth_val.validate(structured_data, resume_knowledge)
        )

        # Knowledge validation
        knowledge_rules = []
        if db:
            try:
                knowledge_rules = get_knowledge_rules_for_context(db)
            except Exception:
                pass

        knowledge_valid, knowledge_score, knowledge_issues, knowledge_details = (
            knowledge_val.validate(structured_data, knowledge_rules)
        )

        is_approved = schema_valid and truth_valid and knowledge_valid
        overall_confidence = (schema_score + truth_score + knowledge_score) / 300.0

        issues = []
        for issue in schema_issues:
            issues.append(issue.get("message", str(issue)))
        for issue in truth_issues:
            issues.append(issue.get("message", str(issue)))
        for issue in knowledge_issues:
            issues.append(issue.get("message", str(issue)))

        return {
            "is_approved": is_approved,
            "overall_confidence": round(overall_confidence, 2),
            "issues": issues,
            "validations": {
                "schema": {"valid": schema_valid, "score": schema_score},
                "truth": {"valid": truth_valid, "score": truth_score},
                "knowledge": {"valid": knowledge_valid, "score": knowledge_score},
            },
        }
    except Exception as e:
        logger.warning("Resume validation failed: %s", e)
        return None


# ---------------------------------------------------------------------------
# ResumeGeneratorService - backward-compatible wrapper
# ---------------------------------------------------------------------------

class ResumeGeneratorService:
    """Generates structured resume data from unstructured input.

    Backward-compatible wrapper around UniversalAIService.
    Injects knowledge rules from knowledge_intelligence when db is available.
    """

    def __init__(self):
        self._service = get_ai_service()

    def generate_structured_resume(self, db, user_id: str, prompt: str, archetype: str = "experienced") -> Dict[str, Any]:
        # Retrieve knowledge rules from knowledge_intelligence
        knowledge_rules = get_knowledge_rules_for_context(db) if db else []

        # Build prompt using Prompt Intelligence v2
        context = {
            "archetype": archetype,
            "prompt": prompt,
        }
        if knowledge_rules:
            context["knowledge_rules"] = knowledge_rules

        request = PromptRequest(
            prompt_type="structured_resume",
            context=context,
        )
        messages = prompt_engine.build_messages(request)

        try:
            response = run_async(self._service.generate(messages))

            structured_data = self._service.parse_json_response(response.content)

            defaults = {
                "personalInfo": {},
                "summary": "",
                "experience": [],
                "education": [],
                "skills": [],
                "projects": [],
                "certifications": [],
                "achievements": [],
            }
            for key, default_val in defaults.items():
                if key not in structured_data:
                    structured_data[key] = default_val

            return structured_data

        except Exception as e:
            logger.error("Resume generation failed: %s\n%s", e, traceback.format_exc())
            return {
                "personalInfo": {},
                "summary": f"Resume generation failed: {str(e)}",
                "experience": [],
                "education": [],
                "skills": [],
                "projects": [],
                "certifications": [],
                "achievements": [],
            }


# ---------------------------------------------------------------------------
# CoverLetterGeneratorService - backward-compatible wrapper
# ---------------------------------------------------------------------------

class CoverLetterGeneratorService:
    """Generates cover letters using the Universal AI Service.

    Backward-compatible wrapper around UniversalAIService.
    Injects knowledge rules from knowledge_intelligence when db is available.
    """

    def __init__(self):
        self._service = get_ai_service()

    def generate_cover_letter(
        self,
        db,
        user_id: str,
        job_role: str,
        company_name: str,
        experience_summary: Optional[str] = None,
    ) -> str:
        # Retrieve knowledge rules from knowledge_intelligence
        knowledge_rules = get_knowledge_rules_for_context(db, section_name="cover_letter") if db else []

        # Build prompt using Prompt Intelligence v2
        context = {
            "job_role": job_role,
            "company_name": company_name,
        }
        if knowledge_rules:
            context["knowledge_rules"] = knowledge_rules

        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context=context,
        )
        messages = prompt_engine.build_messages(request)
        
        # Preserve dynamic experience_summary injection at integration boundary
        if experience_summary and len(messages) >= 2:
            # Append experience_summary to the user message content
            messages[1]["content"] += f"\n\nCandidate experience: {experience_summary}"

        try:
            response = run_async(self._service.generate(messages))

            return response.content.strip()

        except Exception as e:
            logger.error("Cover letter generation failed: %s\n%s", e, traceback.format_exc())
            return ""


# ---------------------------------------------------------------------------
# ATSScoreService - rule-based scoring (no AI required)
# ---------------------------------------------------------------------------

class ATSScoreService:
    """Calculates ATS (Applicant Tracking System) scores for resumes.

    Uses rule-based analysis. No AI required.
    """

    @staticmethod
    def calculate_score(resume_dict: Dict[str, Any]) -> Dict[str, Any]:
        score = 0
        details = {}
        recommendations = []

        personal_info = resume_dict.get("personalInfo", {})
        if personal_info:
            if personal_info.get("name"):
                score += 5
            if personal_info.get("email"):
                score += 5
            if personal_info.get("phone"):
                score += 5
        details["personal_info"] = 15 if personal_info else 0
        if not personal_info or not personal_info.get("name"):
            recommendations.append("Add your full name to personal information")
        if not personal_info or not personal_info.get("email"):
            recommendations.append("Add a professional email address")
        if not personal_info or not personal_info.get("phone"):
            recommendations.append("Add a phone number for contact")

        summary = resume_dict.get("summary", "")
        if summary:
            word_count = len(summary.split())
            if word_count >= 30:
                score += 15
            elif word_count >= 15:
                score += 10
            else:
                score += 5
        details["summary"] = 15 if summary and len(summary.split()) >= 30 else (10 if summary else 0)
        if not summary or len(summary.split()) < 30:
            recommendations.append("Add a professional summary of at least 30 words")

        experience = resume_dict.get("experience", [])
        if experience:
            if len(experience) >= 2:
                score += 15
            elif len(experience) >= 1:
                score += 10
            has_metrics = False
            for exp in experience:
                bullets = exp.get("description", []) if isinstance(exp, dict) else []
                if isinstance(bullets, list):
                    for bullet in bullets:
                        if isinstance(bullet, str) and any(c.isdigit() for c in bullet):
                            has_metrics = True
                            break
            if has_metrics:
                score += 10
        details["experience"] = 25 if experience and len(experience) >= 2 else (10 if experience else 0)
        if not experience:
            recommendations.append("Add work experience with quantified achievements")
        elif len(experience) < 2:
            recommendations.append("Add more work experience entries")

        education = resume_dict.get("education", [])
        if education:
            score += 10
        details["education"] = 10 if education else 0
        if not education:
            recommendations.append("Add your educational background")

        skills = resume_dict.get("skills", [])
        if skills:
            if len(skills) >= 5:
                score += 15
            elif len(skills) >= 3:
                score += 10
            else:
                score += 5
        details["skills"] = 15 if skills and len(skills) >= 5 else (10 if skills else 0)
        if not skills or len(skills) < 5:
            recommendations.append("Add at least 5 relevant technical skills")

        additional_sections = 0
        for section in ["projects", "certifications", "achievements"]:
            if resume_dict.get(section):
                additional_sections += 1
        if additional_sections >= 2:
            score += 10
        elif additional_sections >= 1:
            score += 5
        details["additional_sections"] = 10 if additional_sections >= 2 else (5 if additional_sections else 0)
        if additional_sections < 2:
            recommendations.append("Add projects, certifications, or achievements to stand out")

        score = min(score, 100)

        return {
            "score": score,
            "details": details,
            "recommendations": recommendations,
        }
