"""Import compatibility tests — verify all symbols importable from original paths."""
import pytest


class TestImportCompatibility:
    """Verify every symbol from proposal.md Section 6.2 is importable from app.services.ai_service."""

    def test_import_provider_type(self):
        from app.services.ai_service import ProviderType
        assert ProviderType.GEMINI == "gemini"

    def test_import_provider_config(self):
        from app.services.ai_service import ProviderConfig
        from dataclasses import fields
        field_names = [f.name for f in fields(ProviderConfig)]
        assert "provider_type" in field_names

    def test_import_provider_response(self):
        from app.services.ai_service import ProviderResponse
        from dataclasses import fields
        field_names = [f.name for f in fields(ProviderResponse)]
        assert "content" in field_names

    def test_import_provider_metrics(self):
        from app.services.ai_service import ProviderMetrics
        from dataclasses import fields
        field_names = [f.name for f in fields(ProviderMetrics)]
        assert "request_id" in field_names

    def test_import_provider_error(self):
        from app.services.ai_service import ProviderError
        assert issubclass(ProviderError, Exception)

    def test_import_authentication_error(self):
        from app.services.ai_service import AuthenticationError
        assert issubclass(AuthenticationError, Exception)

    def test_import_rate_limit_error(self):
        from app.services.ai_service import RateLimitError
        assert issubclass(RateLimitError, Exception)

    def test_import_timeout_error(self):
        from app.services.ai_service import TimeoutError
        assert issubclass(TimeoutError, Exception)

    def test_import_provider_unavailable_error(self):
        from app.services.ai_service import ProviderUnavailableError
        assert issubclass(ProviderUnavailableError, Exception)

    def test_import_invalid_response_error(self):
        from app.services.ai_service import InvalidResponseError
        assert issubclass(InvalidResponseError, Exception)

    def test_import_response_parsing_error(self):
        from app.services.ai_service import ResponseParsingError
        assert issubclass(ResponseParsingError, Exception)

    def test_import_configuration_error(self):
        from app.services.ai_service import ConfigurationError
        assert issubclass(ConfigurationError, Exception)

    def test_import_estimate_cost(self):
        from app.services.ai_service import estimate_cost
        assert callable(estimate_cost)

    def test_import_universal_ai_service(self):
        from app.services.ai_service import UniversalAIService
        assert hasattr(UniversalAIService, "generate")

    def test_import_get_ai_service(self):
        from app.services.ai_service import get_ai_service
        assert callable(get_ai_service)

    def test_import_reset_ai_service(self):
        from app.services.ai_service import reset_ai_service
        assert callable(reset_ai_service)

    def test_import_load_config(self):
        from app.services.ai_service import _load_config
        assert callable(_load_config)

    def test_import_validate_provider_config(self):
        from app.services.ai_service import validate_provider_config
        assert callable(validate_provider_config)

    def test_import_log_provider_info(self):
        from app.services.ai_service import log_provider_info
        assert callable(log_provider_info)

    def test_import_run_async(self):
        from app.services.ai_service import run_async
        assert callable(run_async)

    def test_import_resume_generator_service(self):
        from app.services.ai_service import ResumeGeneratorService
        assert hasattr(ResumeGeneratorService, "generate_structured_resume")

    def test_import_cover_letter_generator_service(self):
        from app.services.ai_service import CoverLetterGeneratorService
        assert hasattr(CoverLetterGeneratorService, "generate_cover_letter")

    def test_import_ats_score_service(self):
        from app.services.ai_service import ATSScoreService
        assert hasattr(ATSScoreService, "calculate_score")

    def test_import_from_ai_providers_package(self):
        from app.services.ai_providers import (
            ProviderConfig, ProviderMetrics, ProviderResponse, ProviderType,
            ProviderError, AuthenticationError, RateLimitError,
            ProviderUnavailableError, InvalidResponseError, ResponseParsingError,
            estimate_cost, UniversalAIService, get_ai_service, reset_ai_service,
        )
        assert ProviderType.GEMINI == "gemini"

    def test_import_token_budget_exceeded(self):
        from app.services.ai_service import TokenBudgetExceeded
        assert issubclass(TokenBudgetExceeded, Exception)
