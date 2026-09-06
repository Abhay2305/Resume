"""LLM Service - Uses Universal AI Service for all provider communication.

No provider-specific code. All calls go through UniversalAIService.
"""
import logging
import traceback
from sqlalchemy.orm import Session
from ..models import ResumeRule
from .ai_service import UniversalAIService, get_ai_service, ProviderType, run_async

logger = logging.getLogger(__name__)


class LLMProviderService:
    """Wrapper around UniversalAIService for synchronous usage in routers."""

    def __init__(self):
        self._service = get_ai_service()
        self.is_configured = self._service.config.api_key is not None and self._service.config.api_key != ""
        self.default_model = self._service.model

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """Generate text using the Universal AI Service.

        Falls back to a high-quality simulated rewrite if the API key is missing.
        """
        if not self.is_configured:
            logger.info("%s API not configured, running offline fallback mode.", self._service.provider_name)
            return self._fallback_generate(prompt, system_instruction)

        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            response = run_async(self._service.generate(messages))

            return response.content
        except Exception as e:
            logger.error("%s API generation error: %s\n%s", self._service.provider_name, e, traceback.format_exc())
            return self._fallback_generate(prompt, system_instruction)

    def _fallback_generate(self, prompt: str, system_instruction: str = None) -> str:
        """Fallback when AI service is unavailable. Returns empty string (fail closed)."""
        logger.warning("AI service unavailable, returning empty response")
        return ""


# DEPRECATED: PromptBuilderService is a legacy class not used by any active code path.
# It exists for backward compatibility only. The active prompt construction uses
# PromptBuilderV2 in prompt_intelligence_v2/builder.py.
class PromptBuilderService:
    @staticmethod
    def get_active_rules_instruction(db: Session) -> str:
        """Gathers all active rules from the database to inject into prompts."""
        try:
            rules = db.query(ResumeRule).filter(ResumeRule.is_active == True).all()
            if not rules:
                return ""

            instructions = [
                "You are an elite career advisor and resume editor. Rewrite the user's content according to these strict rules:"
            ]
            for idx, rule in enumerate(rules, 1):
                instructions.append(f"{idx}. {rule.rule_name}: {rule.rule_prompt_instruction}")

            instructions.append("\nReturn ONLY the polished, rewritten content without intro, outro, or conversation prefix.")
            return "\n".join(instructions)
        except Exception as e:
            logger.error("Error fetching rules for prompt: %s", e)
            return ""
