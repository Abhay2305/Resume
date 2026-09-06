"""Unit tests for the Prompt Registry.

Tests register, get, list_types, get_meta, and unknown type error.
"""
import pytest

from app.services.prompt_intelligence_v2.errors import UnknownPromptType
from app.services.prompt_intelligence_v2.registry import PromptRegistry, create_default_registry
from app.services.prompt_intelligence_v2.types import PromptTemplateMeta


class TestPromptRegistry:
    """Test the PromptRegistry class."""

    def setup_method(self):
        self.registry = PromptRegistry()

    def test_register_and_get(self):
        meta = PromptTemplateMeta(
            type="test_type",
            name="Test Type",
            version="1.0",
            category="generation",
            required_variables=["var1"],
            optional_variables=["var2"],
            output_format="text",
        )
        self.registry.register(meta)
        result = self.registry.get("test_type")
        assert result.type == "test_type"
        assert result.name == "Test Type"
        assert result.required_variables == ["var1"]
        assert result.optional_variables == ["var2"]

    def test_get_unknown_type_raises(self):
        with pytest.raises(UnknownPromptType) as exc_info:
            self.registry.get("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.prompt_type == "nonexistent"

    def test_list_types_empty(self):
        assert self.registry.list_types() == []

    def test_list_types_sorted(self):
        for t in ["zebra", "alpha", "middle"]:
            self.registry.register(PromptTemplateMeta(
                type=t, name=t, version="1.0", category="generation",
                required_variables=[], optional_variables=[], output_format="text",
            ))
        result = self.registry.list_types()
        assert result == ["alpha", "middle", "zebra"]

    def test_get_meta_found(self):
        meta = PromptTemplateMeta(
            type="t", name="T", version="1.0", category="generation",
            required_variables=[], optional_variables=[], output_format="text",
        )
        self.registry.register(meta)
        assert self.registry.get_meta("t") is meta

    def test_get_meta_not_found(self):
        assert self.registry.get_meta("nope") is None

    def test_len(self):
        assert len(self.registry) == 0
        self.registry.register(PromptTemplateMeta(
            type="a", name="A", version="1.0", category="generation",
            required_variables=[], optional_variables=[], output_format="text",
        ))
        assert len(self.registry) == 1

    def test_contains(self):
        assert "x" not in self.registry
        self.registry.register(PromptTemplateMeta(
            type="x", name="X", version="1.0", category="generation",
            required_variables=[], optional_variables=[], output_format="text",
        ))
        assert "x" in self.registry


class TestDefaultRegistry:
    """Test the pre-populated default registry."""

    def setup_method(self):
        self.registry = create_default_registry()

    def test_has_16_types(self):
        assert len(self.registry) == 16

    def test_all_types_listed(self):
        types = self.registry.list_types()
        expected = [
            "ats_optimization",
            "ats_optimization_pi",
            "bullet_feedback",
            "chat",
            "cover_letter",
            "cover_letter_direct",
            "resume_bullets",
            "resume_generation",
            "resume_summary",
            "resume_tailoring",
            "structured_resume",
            "text_autofix",
            "text_expand",
            "text_improve",
            "text_professional",
            "text_shorten",
        ]
        assert types == expected

    def test_generation_types(self):
        for t in ["resume_bullets", "resume_summary", "cover_letter", "resume_generation"]:
            meta = self.registry.get(t)
            assert meta.category == "generation", f"{t} should be generation"

    def test_optimization_types(self):
        for t in ["resume_tailoring", "ats_optimization", "ats_optimization_pi"]:
            meta = self.registry.get(t)
            assert meta.category == "optimization", f"{t} should be optimization"

    def test_improvement_types(self):
        for t in ["text_improve", "text_shorten", "text_expand", "text_professional", "text_autofix"]:
            meta = self.registry.get(t)
            assert meta.category == "improvement", f"{t} should be improvement"

    def test_feedback_type(self):
        meta = self.registry.get("bullet_feedback")
        assert meta.category == "feedback"

    def test_conversational_type(self):
        meta = self.registry.get("chat")
        assert meta.category == "conversational"

    def test_formatting_type(self):
        meta = self.registry.get("structured_resume")
        assert meta.category == "formatting"

    def test_resume_bullets_required_variables(self):
        meta = self.registry.get("resume_bullets")
        assert "role_title" in meta.required_variables
        assert "company" in meta.required_variables
        assert "responsibilities" in meta.required_variables
        assert "technologies" in meta.required_variables

    def test_resume_bullets_optional_variables(self):
        meta = self.registry.get("resume_bullets")
        assert "duration" in meta.optional_variables
        assert "achievements" in meta.optional_variables
        assert "num_bullets" in meta.optional_variables

    def test_cover_letter_required_variables(self):
        meta = self.registry.get("cover_letter")
        assert "company" in meta.required_variables
        assert "role_title" in meta.required_variables
        assert "job_description" in meta.required_variables
        assert "my_experience" in meta.required_variables

    def test_chat_required_variables(self):
        meta = self.registry.get("chat")
        assert "user_message" in meta.required_variables

    def test_chat_optional_variables(self):
        meta = self.registry.get("chat")
        assert "conversation_history" in meta.optional_variables

    def test_text_improve_required_variables(self):
        meta = self.registry.get("text_improve")
        assert "text_content" in meta.required_variables

    def test_structured_resume_required_variables(self):
        meta = self.registry.get("structured_resume")
        assert "archetype" in meta.required_variables
        assert "prompt" in meta.required_variables

    def test_cover_letter_direct_required_variables(self):
        meta = self.registry.get("cover_letter_direct")
        assert "job_role" in meta.required_variables
        assert "company_name" in meta.required_variables

    def test_all_types_have_version(self):
        for t in self.registry.list_types():
            meta = self.registry.get(t)
            assert meta.version, f"{t} should have a version"

    def test_all_types_have_output_format(self):
        for t in self.registry.list_types():
            meta = self.registry.get(t)
            assert meta.output_format in ("text", "json_object", "json_array"), \
                f"{t} has invalid output_format: {meta.output_format}"
