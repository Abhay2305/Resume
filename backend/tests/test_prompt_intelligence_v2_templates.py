"""Tests for the Prompt Templates store.

Verifies all migrated templates load correctly and variable placeholders
match the registry metadata.
"""
import pytest

from app.services.prompt_intelligence_v2.templates import PromptTemplates
from app.services.prompt_intelligence_v2.registry import create_default_registry


class TestPromptTemplates:
    """Test the PromptTemplates class."""

    def setup_method(self):
        self.templates = PromptTemplates()
        self.registry = create_default_registry()

    # ------------------------------------------------------------------
    # System prompt tests — one per migrated source
    # ------------------------------------------------------------------

    def test_resume_bullets_system_from_prompt_builder(self):
        """SYSTEM_BASE from prompt_builder.py → resume_bullets system."""
        content = self.templates.get_system("resume_bullets")
        assert content
        assert "expert resume" in content.lower()
        assert "knowledge context" in content.lower()

    def test_resume_summary_system_from_prompt_builder(self):
        """SYSTEM_BASE → resume_summary system."""
        content = self.templates.get_system("resume_summary")
        assert content
        assert "expert resume" in content.lower()

    def test_cover_letter_system_from_prompt_builder(self):
        """SYSTEM_BASE + SYSTEM_COVER_LETTER → cover_letter system."""
        content = self.templates.get_system("cover_letter")
        assert content
        assert "cover letter writer" in content.lower()
        assert "knowledge context" in content.lower()

    def test_bullet_feedback_system_from_prompt_builder(self):
        """SYSTEM_BASE + SYSTEM_BULLET_WRITER → bullet_feedback system."""
        content = self.templates.get_system("bullet_feedback")
        assert content
        assert "bullet point reviewer" in content.lower()
        assert "knowledge context" in content.lower()

    def test_ats_optimization_system_from_prompt_builder(self):
        """SYSTEM_BASE → ats_optimization system."""
        content = self.templates.get_system("ats_optimization")
        assert content
        assert "ats optimization specialist" in content.lower()

    def test_resume_tailoring_system_from_json(self):
        """prompt_templates.json → resume_tailoring system."""
        content = self.templates.get_system("resume_tailoring")
        assert content
        assert "tailoring" in content.lower()
        assert "knowledge context" in content.lower()

    def test_resume_generation_system_from_json(self):
        """prompt_templates.json → resume_generation system."""
        content = self.templates.get_system("resume_generation")
        assert content
        assert "resume writer" in content.lower()

    def test_ats_optimization_pi_system_from_json(self):
        """prompt_templates.json → ats_optimization_pi system."""
        content = self.templates.get_system("ats_optimization_pi")
        assert content
        assert "ats optimization" in content.lower()

    def test_chat_system_from_chat_service(self):
        """CAREER_ADVISOR_SYSTEM from chat_service.py → chat system."""
        content = self.templates.get_system("chat")
        assert content
        assert "career advisor" in content.lower()
        assert "conversation flow" in content.lower()
        # JSON block extraction is still present for backend structured_data parsing
        assert "generate_resume" in content
        # Skill filtering rules are present
        assert "skills must only" in content.lower()

    def test_structured_resume_system_from_ai_service(self):
        """ResumeGeneratorService system_instruction → structured_resume system."""
        content = self.templates.get_system("structured_resume")
        assert content
        assert "unstructured" in content.lower()
        assert "personalInfo" in content

    def test_cover_letter_direct_system_from_ai_service(self):
        """CoverLetterGeneratorService system_instruction → cover_letter_direct system."""
        content = self.templates.get_system("cover_letter_direct")
        assert content
        assert "cover letter writer" in content.lower()

    # ------------------------------------------------------------------
    # User prompt tests — migrated from prompt_builder.py
    # ------------------------------------------------------------------

    def test_resume_bullets_user_has_variables(self):
        """USER_RESUME_BULLETS → resume_bullets user with placeholders."""
        content = self.templates.get_user("resume_bullets")
        assert content
        assert "{role_title}" in content
        assert "{company}" in content
        assert "{responsibilities}" in content
        assert "{technologies}" in content
        assert "{num_bullets}" in content

    def test_resume_summary_user_has_variables(self):
        """USER_RESUME_SUMMARY → resume_summary user with placeholders."""
        content = self.templates.get_user("resume_summary")
        assert content
        assert "{target_role}" in content
        assert "{experience_years}" in content
        assert "{skills}" in content
        assert "{achievements}" in content

    def test_cover_letter_user_has_variables(self):
        """USER_COVER_LETTER → cover_letter user with placeholders."""
        content = self.templates.get_user("cover_letter")
        assert content
        assert "{company}" in content
        assert "{role_title}" in content
        assert "{job_description}" in content
        assert "{my_experience}" in content

    def test_bullet_feedback_user_has_variables(self):
        """USER_BULLET_FEEDBACK → bullet_feedback user with placeholders."""
        content = self.templates.get_user("bullet_feedback")
        assert content
        assert "{bullet}" in content
        assert "{context}" in content
        assert "{role_title}" in content

    def test_ats_optimization_user_has_variables(self):
        """ATS_OPTIMIZATION → ats_optimization user with placeholders."""
        content = self.templates.get_user("ats_optimization")
        assert content
        assert "{content}" in content
        assert "{job_description}" in content

    # ------------------------------------------------------------------
    # User prompt tests — migrated from ats.py
    # ------------------------------------------------------------------

    def test_text_improve_user(self):
        """ats.py improve action → text_improve user."""
        content = self.templates.get_user("text_improve")
        assert content
        assert "{text_content}" in content
        assert "polishing" in content.lower()

    def test_text_shorten_user(self):
        """ats.py shorten action → text_shorten user."""
        content = self.templates.get_user("text_shorten")
        assert content
        assert "{text_content}" in content
        assert "condense" in content.lower()

    def test_text_expand_user(self):
        """ats.py expand action → text_expand user."""
        content = self.templates.get_user("text_expand")
        assert content
        assert "{text_content}" in content
        assert "expand" in content.lower()

    def test_text_professional_user(self):
        """ats.py professional action → text_professional user."""
        content = self.templates.get_user("text_professional")
        assert content
        assert "{text_content}" in content
        assert "professional" in content.lower()

    def test_text_autofix_user(self):
        """ats.py autofix action → text_autofix user."""
        content = self.templates.get_user("text_autofix")
        assert content
        assert "{text_content}" in content
        assert "fix style" in content.lower()

    # ------------------------------------------------------------------
    # User prompt tests — migrated from ai_service.py
    # ------------------------------------------------------------------

    def test_structured_resume_user_has_variables(self):
        """ResumeGeneratorService user_message → structured_resume user."""
        content = self.templates.get_user("structured_resume")
        assert content
        assert "{archetype}" in content
        assert "{prompt}" in content

    def test_cover_letter_direct_user_has_variables(self):
        """CoverLetterGeneratorService user_message → cover_letter_direct user."""
        content = self.templates.get_user("cover_letter_direct")
        assert content
        assert "{job_role}" in content
        assert "{company_name}" in content

    # ------------------------------------------------------------------
    # Context templates — migrated from prompt_builder.py
    # ------------------------------------------------------------------

    def test_knowledge_context_template(self):
        """KNOWLEDGE_CONTEXT_HEADER → knowledge context."""
        content = self.templates.get_context("knowledge")
        assert content
        assert "{knowledge_text}" in content
        assert "knowledge" in content.lower()

    def test_rules_context_template(self):
        """RESUME_RULES_HEADER → rules context."""
        content = self.templates.get_context("rules")
        assert content
        assert "{rules_text}" in content
        assert "resume writing rules" in content.lower()

    # ------------------------------------------------------------------
    # JSON data loading — instructions, constraints, output_schemas
    # ------------------------------------------------------------------

    def test_instructions_loaded_from_json(self):
        """Instructions from prompt_templates.json are accessible."""
        instructions = self.templates.get_instructions("resume_tailoring")
        assert len(instructions) > 0
        assert instructions[0]["id"] == "INST_RT_001"

    def test_cover_letter_instructions_from_json(self):
        """Cover letter instructions from prompt_templates.json."""
        instructions = self.templates.get_instructions("cover_letter")
        assert len(instructions) > 0
        assert instructions[0]["id"] == "INST_CL_001"

    def test_constraints_universal_loaded(self):
        """Universal constraints from prompt_templates.json."""
        constraints = self.templates.get_constraints("resume_bullets")
        # Universal constraints should be present for all types
        ids = [c["id"] for c in constraints]
        assert "CONST_001" in ids

    def test_constraints_type_specific_merged(self):
        """Type-specific constraints merged with universal."""
        constraints = self.templates.get_constraints("resume_tailoring")
        ids = [c["id"] for c in constraints]
        assert "CONST_001" in ids  # universal
        assert "CONST_RT_001" in ids  # resume_tailoring specific

    def test_output_schema_loaded(self):
        """Output schema from prompt_templates.json."""
        schema = self.templates.get_output_schema("resume_tailoring")
        assert schema is not None
        assert schema["type"] == "object"
        assert "summary" in schema["properties"]

    def test_output_schema_returns_none_for_unknown(self):
        """Unknown type returns None for output schema."""
        assert self.templates.get_output_schema("nonexistent") is None

    # ------------------------------------------------------------------
    # Completeness — all registry types have templates
    # ------------------------------------------------------------------

    # Context-driven types use structured data (resume_knowledge, opportunity, etc.)
    # passed to the assembler, not simple {variable} placeholders in user templates.
    CONTEXT_DRIVEN_TYPES = {"resume_tailoring", "resume_generation", "ats_optimization_pi", "chat"}

    def test_all_registry_types_have_system_prompts(self):
        """Every registered prompt type has a system prompt."""
        for prompt_type in self.registry.list_types():
            content = self.templates.get_system(prompt_type)
            assert content, f"Missing system prompt for {prompt_type}"

    def test_all_registry_types_have_user_prompts(self):
        """Every registered prompt type has a user prompt (except context-driven types)."""
        for prompt_type in self.registry.list_types():
            if prompt_type in self.CONTEXT_DRIVEN_TYPES:
                continue  # Context-driven types use assembler, not user template
            content = self.templates.get_user(prompt_type)
            assert content, f"Missing user prompt for {prompt_type}"

    def test_variable_placeholders_match_registry_required(self):
        """User prompt placeholders correspond to registry required_variables."""
        import re
        for prompt_type in self.registry.list_types():
            if prompt_type in self.CONTEXT_DRIVEN_TYPES:
                continue  # Context-driven types don't use {variable} placeholders
            meta = self.registry.get(prompt_type)
            user_template = self.templates.get_user(prompt_type)
            placeholders = set(re.findall(r"\{(\w+)\}", user_template))
            # All required variables should appear as placeholders
            for var in meta.required_variables:
                assert var in placeholders, \
                    f"Required variable '{var}' not in {prompt_type} user template placeholders {placeholders}"

    def test_listing_methods(self):
        """list_system_types and list_user_types return sorted lists."""
        system_types = self.templates.list_system_types()
        user_types = self.templates.list_user_types()
        assert system_types == sorted(system_types)
        assert user_types == sorted(user_types)
        assert len(system_types) >= 16  # All 16 types have system prompts
        assert len(user_types) >= 12  # 16 minus 4 context-driven types
