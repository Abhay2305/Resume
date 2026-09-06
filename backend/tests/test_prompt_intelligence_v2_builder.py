"""Tests for the Prompt Builder.

Verifies the full build pipeline for all 16 prompt types,
validate catches missing variables, token estimation,
build_messages convenience, and error handling.
"""
import pytest

from app.services.prompt_intelligence_v2.builder import PromptBuilder
from app.services.prompt_intelligence_v2.errors import MissingVariables, UnknownPromptType
from app.services.prompt_intelligence_v2.types import PromptRequest, PromptPackage, ValidationResult


class TestPromptBuilder:
    """Test the PromptBuilder class."""

    def setup_method(self):
        self.builder = PromptBuilder()

    # ------------------------------------------------------------------
    # Build for each prompt type — generation category
    # ------------------------------------------------------------------

    def test_build_resume_bullets(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "Software Engineer",
                "company": "Acme",
                "responsibilities": "Built APIs",
                "technologies": "Python, FastAPI",
                "achievements": "Reduced latency 40%",
                "num_bullets": 5,
            },
        )
        package = self.builder.build(request)
        assert isinstance(package, PromptPackage)
        assert package.prompt_type == "resume_bullets"
        assert "expert resume" in package.system_prompt.lower()
        assert "Acme" in package.user_prompt
        assert len(package.messages) == 2
        assert package.messages[0]["role"] == "system"
        assert package.messages[1]["role"] == "user"
        assert package.token_estimate > 0
        assert package.template_version == "1.0"

    def test_build_resume_summary(self):
        request = PromptRequest(
            prompt_type="resume_summary",
            context={
                "target_role": "Senior Engineer",
                "experience_years": 8,
                "skills": "Python, Go",
                "achievements": "Led migration",
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "resume_summary"
        assert "Senior Engineer" in package.user_prompt
        assert len(package.messages) == 2

    def test_build_cover_letter(self):
        request = PromptRequest(
            prompt_type="cover_letter",
            context={
                "company": "TechCorp",
                "role_title": "Staff Engineer",
                "job_description": "Lead backend team",
                "my_experience": "10 years building distributed systems",
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "cover_letter"
        assert "TechCorp" in package.user_prompt

    def test_build_resume_generation(self):
        request = PromptRequest(
            prompt_type="resume_generation",
            context={
                "resume_knowledge": {"skills": ["Python"], "experience": []},
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "resume_generation"
        assert "Resume Data" in package.user_prompt

    def test_build_ats_optimization(self):
        request = PromptRequest(
            prompt_type="ats_optimization",
            context={
                "content": "Experienced engineer",
                "job_description": "Python developer",
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "ats_optimization"
        assert "Experienced engineer" in package.user_prompt

    # ------------------------------------------------------------------
    # Build — optimization category
    # ------------------------------------------------------------------

    def test_build_resume_tailoring(self):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "Senior Engineer"},
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "resume_tailoring"
        assert "Resume Data" in package.user_prompt
        assert "Target Opportunity" in package.user_prompt

    def test_build_ats_optimization_pi(self):
        request = PromptRequest(
            prompt_type="ats_optimization_pi",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "Developer"},
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "ats_optimization_pi"
        assert "Resume Data" in package.user_prompt

    # ------------------------------------------------------------------
    # Build — improvement category
    # ------------------------------------------------------------------

    def test_build_text_improve(self):
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "We did stuff"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "text_improve"
        assert "We did stuff" in package.user_prompt

    def test_build_text_shorten(self):
        request = PromptRequest(
            prompt_type="text_shorten",
            context={"text_content": "Very long text"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "text_shorten"
        assert "Very long text" in package.user_prompt

    def test_build_text_expand(self):
        request = PromptRequest(
            prompt_type="text_expand",
            context={"text_content": "Short text"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "text_expand"

    def test_build_text_professional(self):
        request = PromptRequest(
            prompt_type="text_professional",
            context={"text_content": "Casual text"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "text_professional"

    def test_build_text_autofix(self):
        request = PromptRequest(
            prompt_type="text_autofix",
            context={"text_content": "Text with issues"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "text_autofix"

    # ------------------------------------------------------------------
    # Build — feedback, conversational, formatting categories
    # ------------------------------------------------------------------

    def test_build_bullet_feedback(self):
        request = PromptRequest(
            prompt_type="bullet_feedback",
            context={"bullet": "Did stuff"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "bullet_feedback"
        assert "Did stuff" in package.user_prompt

    def test_build_chat(self):
        request = PromptRequest(
            prompt_type="chat",
            context={"user_message": "Help me with my resume"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "chat"
        assert package.user_prompt == "Help me with my resume"
        assert "career" in package.system_prompt.lower()

    def test_build_structured_resume(self):
        request = PromptRequest(
            prompt_type="structured_resume",
            context={"archetype": "backend", "prompt": "Generate resume"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "structured_resume"
        assert "Generate resume" in package.user_prompt

    def test_build_cover_letter_direct(self):
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={"job_role": "Engineer", "company_name": "Acme"},
        )
        package = self.builder.build(request)
        assert package.prompt_type == "cover_letter_direct"
        assert "Acme" in package.user_prompt

    # ------------------------------------------------------------------
    # Build_messages convenience
    # ------------------------------------------------------------------

    def test_build_messages_returns_list(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
            },
        )
        messages = self.builder.build_messages(request)
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_build_messages_compatible_with_generate(self):
        """Messages format matches what UniversalAIService.generate() expects."""
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Hello"},
        )
        messages = self.builder.build_messages(request)
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ("system", "user", "assistant")

    # ------------------------------------------------------------------
    # Validate method
    # ------------------------------------------------------------------

    def test_validate_valid_request(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
            },
        )
        result = self.builder.validate(request)
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.errors == []
        assert result.token_estimate > 0

    def test_validate_missing_required_variable(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={"role_title": "SE"},  # missing company, responsibilities, technologies
        )
        result = self.builder.validate(request)
        assert result.is_valid is False
        assert len(result.errors) >= 1
        assert any("company" in e for e in result.errors)

    def test_validate_unknown_type(self):
        request = PromptRequest(
            prompt_type="nonexistent",
            context={},
        )
        result = self.builder.validate(request)
        assert result.is_valid is False
        assert any("nonexistent" in e for e in result.errors)

    def test_validate_context_driven_type(self):
        request = PromptRequest(
            prompt_type="chat",
            context={"user_message": "Hello"},
        )
        result = self.builder.validate(request)
        assert result.is_valid is True

    # ------------------------------------------------------------------
    # Estimate_tokens method
    # ------------------------------------------------------------------

    def test_estimate_tokens_returns_positive(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
            },
        )
        tokens = self.builder.estimate_tokens(request)
        assert tokens > 0

    def test_estimate_tokens_unknown_type_returns_zero(self):
        request = PromptRequest(prompt_type="nope", context={})
        assert self.builder.estimate_tokens(request) == 0

    def test_estimate_tokens_increases_with_content(self):
        short = self.builder.estimate_tokens(PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Hi"},
        ))
        long = self.builder.estimate_tokens(PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "A" * 1000},
        ))
        assert long > short

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_build_unknown_type_raises(self):
        request = PromptRequest(prompt_type="nonexistent", context={})
        with pytest.raises(UnknownPromptType):
            self.builder.build(request)

    def test_build_missing_required_variable_raises(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={"role_title": "SE"},  # missing required
        )
        with pytest.raises(MissingVariables) as exc_info:
            self.builder.build(request)
        assert len(exc_info.value.missing) >= 1

    # ------------------------------------------------------------------
    # Package metadata
    # ------------------------------------------------------------------

    def test_package_has_metadata(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
            },
            metadata={"custom": "value"},
        )
        package = self.builder.build(request)
        assert package.metadata["category"] == "generation"
        assert package.metadata["output_format"] == "json_array"
        assert package.metadata["custom"] == "value"

    def test_package_has_instructions_and_constraints(self):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
            },
        )
        package = self.builder.build(request)
        assert isinstance(package.instructions, list)
        assert isinstance(package.constraints, list)

    def test_package_has_output_schema(self):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"skills": ["Python"]},
                "opportunity": {"title": "SE"},
            },
        )
        package = self.builder.build(request)
        # Output schema may be empty dict or populated
        assert isinstance(package.output_schema, dict)

    # ------------------------------------------------------------------
    # Optional variables
    # ------------------------------------------------------------------

    def test_optional_variables_not_required(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
                # duration, achievements, num_bullets are optional
            },
        )
        package = self.builder.build(request)
        assert package.prompt_type == "resume_bullets"

    def test_optional_variables_used_when_provided(self):
        request = PromptRequest(
            prompt_type="resume_bullets",
            context={
                "role_title": "SE",
                "company": "X",
                "responsibilities": "A",
                "technologies": "B",
                "num_bullets": 3,
            },
        )
        package = self.builder.build(request)
        assert "3" in package.user_prompt
