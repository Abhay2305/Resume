"""Prompt Registry — central catalog of all prompt types.

Maps prompt type keys to their metadata: required variables, output format,
category, and template information. Single source of truth for what each
prompt type requires and produces.
"""
from typing import Dict, List, Optional

from app.services.prompt_intelligence_v2.errors import UnknownPromptType
from app.services.prompt_intelligence_v2.types import PromptTemplateMeta


class PromptRegistry:
    """Central catalog of prompt types and their metadata.

    All prompt types used across Prompt Resume are registered here.
    Callers query the registry to discover what variables a prompt type
    requires, what output format to expect, and what category it belongs to.
    """

    def __init__(self) -> None:
        self._types: Dict[str, PromptTemplateMeta] = {}

    def register(self, meta: PromptTemplateMeta) -> None:
        """Register a prompt type metadata."""
        self._types[meta.type] = meta

    def get(self, prompt_type: str) -> PromptTemplateMeta:
        """Get metadata for a prompt type.

        Raises UnknownPromptType if the type is not registered.
        """
        if prompt_type not in self._types:
            raise UnknownPromptType(prompt_type)
        return self._types[prompt_type]

    def list_types(self) -> List[str]:
        """List all registered prompt type keys."""
        return sorted(self._types.keys())

    def get_meta(self, prompt_type: str) -> Optional[PromptTemplateMeta]:
        """Get metadata for a prompt type, returning None if not found."""
        return self._types.get(prompt_type)

    def __len__(self) -> int:
        return len(self._types)

    def __contains__(self, prompt_type: str) -> bool:
        return prompt_type in self._types


def create_default_registry() -> PromptRegistry:
    """Create a registry pre-populated with all 16 prompt types.

    Returns a PromptRegistry with types from design.md §5.2.
    """
    registry = PromptRegistry()

    # --- Generation ---

    registry.register(PromptTemplateMeta(
        type="resume_bullets",
        name="Resume Bullet Generator",
        version="1.0",
        category="generation",
        required_variables=["role_title", "company", "responsibilities", "technologies"],
        optional_variables=["duration", "achievements", "num_bullets", "knowledge_chunks", "rules"],
        output_format="json_array",
    ))

    registry.register(PromptTemplateMeta(
        type="resume_summary",
        name="Resume Summary Generator",
        version="1.0",
        category="generation",
        required_variables=["target_role", "experience_years", "skills", "achievements"],
        optional_variables=["goals", "knowledge_chunks"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="cover_letter",
        name="Cover Letter Generator",
        version="1.0",
        category="generation",
        required_variables=["company", "role_title", "job_description", "my_experience"],
        optional_variables=["why_company", "relevant_skills", "knowledge_chunks"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="resume_generation",
        name="Resume Generation (from scratch)",
        version="1.0",
        category="generation",
        required_variables=["resume_knowledge"],
        optional_variables=["opportunity"],
        output_format="json_object",
    ))

    # --- Optimization ---

    registry.register(PromptTemplateMeta(
        type="resume_tailoring",
        name="Resume Tailoring",
        version="1.0",
        category="optimization",
        required_variables=["resume_knowledge", "opportunity"],
        optional_variables=["gap_analysis", "knowledge_context", "template_id"],
        output_format="json_object",
    ))

    registry.register(PromptTemplateMeta(
        type="ats_optimization",
        name="ATS Optimization (inline)",
        version="1.0",
        category="optimization",
        required_variables=["content", "job_description"],
        optional_variables=[],
        output_format="json_object",
    ))

    registry.register(PromptTemplateMeta(
        type="ats_optimization_pi",
        name="ATS Optimization (Prompt Intelligence)",
        version="1.0",
        category="optimization",
        required_variables=["resume_knowledge", "opportunity"],
        optional_variables=["gap_analysis"],
        output_format="json_object",
    ))

    # --- Improvement ---

    registry.register(PromptTemplateMeta(
        type="text_improve",
        name="Text Improvement (general)",
        version="1.0",
        category="improvement",
        required_variables=["text_content"],
        optional_variables=["rules"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="text_shorten",
        name="Text Shortening",
        version="1.0",
        category="improvement",
        required_variables=["text_content"],
        optional_variables=["rules"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="text_expand",
        name="Text Expansion",
        version="1.0",
        category="improvement",
        required_variables=["text_content"],
        optional_variables=["rules"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="text_professional",
        name="Text Professionalization",
        version="1.0",
        category="improvement",
        required_variables=["text_content"],
        optional_variables=["rules"],
        output_format="text",
    ))

    registry.register(PromptTemplateMeta(
        type="text_autofix",
        name="Text Auto-Fix (Harvard rules)",
        version="1.0",
        category="improvement",
        required_variables=["text_content"],
        optional_variables=["rules"],
        output_format="text",
    ))

    # --- Feedback ---

    registry.register(PromptTemplateMeta(
        type="bullet_feedback",
        name="Bullet Feedback & Improvement",
        version="1.0",
        category="feedback",
        required_variables=["bullet"],
        optional_variables=["context", "role_title"],
        output_format="json_object",
    ))

    # --- Conversational ---

    registry.register(PromptTemplateMeta(
        type="chat",
        name="Career Advisor Chat",
        version="1.0",
        category="conversational",
        required_variables=["user_message"],
        optional_variables=["conversation_history"],
        output_format="text",
    ))

    # --- Formatting ---

    registry.register(PromptTemplateMeta(
        type="structured_resume",
        name="Structured Resume Formatter",
        version="1.0",
        category="formatting",
        required_variables=["archetype", "prompt"],
        optional_variables=[],
        output_format="json_object",
    ))

    registry.register(PromptTemplateMeta(
        type="cover_letter_direct",
        name="Direct Cover Letter Generator",
        version="1.0",
        category="generation",
        required_variables=["job_role", "company_name"],
        optional_variables=[],
        output_format="text",
    ))

    return registry
