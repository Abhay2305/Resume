"""Import tests for the Prompt Intelligence Engine v2.

Verifies all types and errors are importable from the new package.
"""
import pytest

from app.services.prompt_intelligence_v2.types import (
    PromptRequest,
    PromptPackage,
    PromptTemplateMeta,
    ValidationResult,
)
from app.services.prompt_intelligence_v2.errors import (
    PromptIntelligenceError,
    UnknownPromptType,
    MissingVariables,
    InvalidTemplate,
    TokenLimitExceeded,
)


class TestTypesImport:
    """Verify all type dataclasses are importable."""

    def test_import_prompt_request(self):
        assert PromptRequest is not None

    def test_import_prompt_package(self):
        assert PromptPackage is not None

    def test_import_prompt_template_meta(self):
        assert PromptTemplateMeta is not None

    def test_import_validation_result(self):
        assert ValidationResult is not None

    def test_prompt_request_creation(self):
        req = PromptRequest(
            prompt_type="resume_bullets",
            context={"role_title": "Engineer"},
        )
        assert req.prompt_type == "resume_bullets"
        assert req.context == {"role_title": "Engineer"}
        assert req.template_id is None
        assert req.user_id is None
        assert req.metadata == {}

    def test_prompt_request_with_optional_fields(self):
        req = PromptRequest(
            prompt_type="cover_letter",
            context={"company": "TechCorp"},
            template_id="tmpl_001",
            user_id="user_123",
            metadata={"source": "test"},
        )
        assert req.template_id == "tmpl_001"
        assert req.user_id == "user_123"
        assert req.metadata == {"source": "test"}

    def test_prompt_package_creation(self):
        pkg = PromptPackage(
            prompt_type="resume_bullets",
            system_prompt="You are a resume writer.",
            user_prompt="Generate bullets for Engineer at TechCorp.",
            messages=[
                {"role": "system", "content": "You are a resume writer."},
                {"role": "user", "content": "Generate bullets for Engineer at TechCorp."},
            ],
            instructions=[],
            constraints=[],
            output_schema=None,
            token_estimate=50,
            template_version="abc123",
        )
        assert pkg.prompt_type == "resume_bullets"
        assert len(pkg.messages) == 2
        assert pkg.token_estimate == 50
        assert pkg.template_version == "abc123"
        assert pkg.metadata == {}

    def test_prompt_template_meta_creation(self):
        meta = PromptTemplateMeta(
            type="resume_bullets",
            name="Resume Bullet Generator",
            version="1.0",
            category="generation",
            required_variables=["role_title", "company"],
            optional_variables=["knowledge_chunks"],
            output_format="json_array",
        )
        assert meta.type == "resume_bullets"
        assert meta.output_schema is None
        assert meta.max_tokens is None

    def test_validation_result_creation(self):
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Low token count"],
            token_estimate=100,
        )
        assert result.is_valid
        assert result.errors == []
        assert result.warnings == ["Low token count"]
        assert result.token_estimate == 100

    def test_validation_result_invalid(self):
        result = ValidationResult(
            is_valid=False,
            errors=["Missing required variable: role_title"],
            warnings=[],
        )
        assert not result.is_valid
        assert len(result.errors) == 1


class TestErrorsImport:
    """Verify all error classes are importable."""

    def test_import_prompt_intelligence_error(self):
        assert PromptIntelligenceError is not None

    def test_import_unknown_prompt_type(self):
        assert UnknownPromptType is not None

    def test_import_missing_variables(self):
        assert MissingVariables is not None

    def test_import_invalid_template(self):
        assert InvalidTemplate is not None

    def test_import_token_limit_exceeded(self):
        assert TokenLimitExceeded is not None

    def test_unknown_prompt_type_creation(self):
        err = UnknownPromptType("bad_type")
        assert str(err) == "Unknown prompt type: 'bad_type'"
        assert err.prompt_type == "bad_type"
        assert err.to_dict()["error"] == "UnknownPromptType"

    def test_missing_variables_creation(self):
        err = MissingVariables(["role_title", "company"], prompt_type="resume_bullets")
        assert "role_title" in str(err)
        assert "company" in str(err)
        assert err.missing == ["role_title", "company"]
        assert err.prompt_type == "resume_bullets"
        d = err.to_dict()
        assert d["missing"] == ["role_title", "company"]

    def test_invalid_template_creation(self):
        err = InvalidTemplate("Template is empty", prompt_type="cover_letter")
        assert str(err) == "Template is empty"
        assert err.prompt_type == "cover_letter"

    def test_token_limit_exceeded_creation(self):
        err = TokenLimitExceeded(estimated=15000, limit=8000, prompt_type="resume_bullets")
        assert err.estimated == 15000
        assert err.limit == 8000
        assert err.prompt_type == "resume_bullets"
        d = err.to_dict()
        assert d["estimated"] == 15000
        assert d["limit"] == 8000

    def test_error_hierarchy(self):
        assert issubclass(UnknownPromptType, PromptIntelligenceError)
        assert issubclass(MissingVariables, PromptIntelligenceError)
        assert issubclass(InvalidTemplate, PromptIntelligenceError)
        assert issubclass(TokenLimitExceeded, PromptIntelligenceError)
        assert issubclass(PromptIntelligenceError, Exception)

    def test_errors_are_catchable(self):
        with pytest.raises(PromptIntelligenceError):
            raise UnknownPromptType("test")

        with pytest.raises(PromptIntelligenceError):
            raise MissingVariables(["x"])

        with pytest.raises(PromptIntelligenceError):
            raise InvalidTemplate("bad")

        with pytest.raises(PromptIntelligenceError):
            raise TokenLimitExceeded(100, 50)
