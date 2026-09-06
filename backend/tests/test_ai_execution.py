"""Tests for the AI Execution Engine.

Tests the AIExecutionService, ResponseParser, and API endpoints.
Uses mock providers for deterministic testing.
"""
import json
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

from app.services.ai_execution.response_parser import ResponseParser
from app.services.ai_execution.service import AIExecutionService
from app.services.ai_service import (
    ProviderResponse,
    ProviderType,
    ProviderError,
    AuthenticationError,
    RateLimitError,
    TimeoutError,
    ProviderUnavailableError,
    ResponseParsingError,
)


# ============================================================
# ResponseParser Tests
# ============================================================

class TestResponseParser:
    def setup_method(self):
        self.parser = ResponseParser()

    def test_parse_to_dict_valid_json(self):
        content = '{"key": "value", "number": 42}'
        result = self.parser.parse_to_dict(content)
        assert result == {"key": "value", "number": 42}

    def test_parse_to_dict_json_array(self):
        content = '[{"item": 1}, {"item": 2}]'
        result = self.parser.parse_to_dict(content)
        assert result == [{"item": 1}, {"item": 2}]

    def test_parse_to_dict_markdown_wrapped(self):
        content = '```json\n{"key": "value"}\n```'
        result = self.parser.parse_to_dict(content)
        assert result == {"key": "value"}

    def test_parse_to_dict_markdown_without_json_label(self):
        content = '```\n{"key": "value"}\n```'
        result = self.parser.parse_to_dict(content)
        assert result == {"key": "value"}

    def test_parse_to_dict_embedded_json(self):
        content = 'Here is the result: {"key": "value"} and more text'
        result = self.parser.parse_to_dict(content)
        assert result == {"key": "value"}

    def test_parse_to_dict_empty_content(self):
        with pytest.raises(ResponseParsingError):
            self.parser.parse_to_dict("")

    def test_parse_to_dict_none_content(self):
        with pytest.raises(ResponseParsingError):
            self.parser.parse_to_dict(None)

    def test_parse_to_dict_invalid_json(self):
        with pytest.raises(ResponseParsingError):
            self.parser.parse_to_dict("not valid json at all")

    def test_parse_to_text_valid(self):
        content = "Hello, this is a response"
        result = self.parser.parse_to_text(content)
        assert result == "Hello, this is a response"

    def test_parse_to_text_markdown_wrapped(self):
        content = "```\nHello\n```"
        result = self.parser.parse_to_text(content)
        assert result == "Hello"

    def test_parse_to_text_empty(self):
        result = self.parser.parse_to_text("")
        assert result == ""

    def test_parse_to_text_none(self):
        result = self.parser.parse_to_text(None)
        assert result == ""

    def test_validate_response_valid(self):
        response = ProviderResponse(
            content="test",
            model="test-model",
            provider=ProviderType.OPENAI,
        )
        assert self.parser.validate_response(response) is True

    def test_validate_response_empty_content(self):
        response = ProviderResponse(
            content="",
            model="test-model",
            provider=ProviderType.OPENAI,
        )
        assert self.parser.validate_response(response) is False

    def test_validate_response_no_model(self):
        response = ProviderResponse(
            content="test",
            model="",
            provider=ProviderType.OPENAI,
        )
        assert self.parser.validate_response(response) is False

    def test_extract_metadata(self):
        response = ProviderResponse(
            content="test",
            model="test-model",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            latency_ms=150.5,
            request_id="test-123",
        )
        metadata = self.parser.extract_metadata(response)
        assert metadata["provider"] == "openai"
        assert metadata["model"] == "test-model"
        assert metadata["prompt_tokens"] == 10
        assert metadata["completion_tokens"] == 20
        assert metadata["total_tokens"] == 30
        assert metadata["latency_ms"] == 150.5
        assert metadata["request_id"] == "test-123"


# ============================================================
# AIExecutionRepository Tests
# ============================================================

class TestAIExecutionRepository:
    def setup_method(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base

        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def teardown_method(self):
        self.db.close()

    def test_create_execution(self):
        from app.repositories.ai_execution import AIExecutionRepository

        repo = AIExecutionRepository(self.db)
        execution = repo.create({
            "prompt_package_id": "test-package-id",
            "user_id": "test-user-id",
            "provider": "mock",
            "model": "mock-model",
            "status": "pending",
        })
        self.db.commit()

        assert execution.id is not None
        assert execution.prompt_package_id == "test-package-id"
        assert execution.user_id == "test-user-id"
        assert execution.provider == "mock"
        assert execution.model == "mock-model"
        assert execution.status == "pending"

    def test_get_by_id(self):
        from app.repositories.ai_execution import AIExecutionRepository

        repo = AIExecutionRepository(self.db)
        execution = repo.create({
            "prompt_package_id": "test-package-id",
            "user_id": "test-user-id",
            "provider": "mock",
            "model": "mock-model",
            "status": "pending",
        })
        self.db.commit()

        found = repo.get_by_id(execution.id)
        assert found is not None
        assert found.id == execution.id

    def test_get_by_user_id(self):
        from app.repositories.ai_execution import AIExecutionRepository

        repo = AIExecutionRepository(self.db)
        repo.create({
            "prompt_package_id": "test-package-id",
            "user_id": "user-1",
            "provider": "mock",
            "model": "mock-model",
            "status": "pending",
        })
        repo.create({
            "prompt_package_id": "test-package-id",
            "user_id": "user-2",
            "provider": "mock",
            "model": "mock-model",
            "status": "pending",
        })
        self.db.commit()

        items, total = repo.get_by_user_id("user-1")
        assert total == 1
        assert items[0].user_id == "user-1"

    def test_update_execution(self):
        from app.repositories.ai_execution import AIExecutionRepository

        repo = AIExecutionRepository(self.db)
        execution = repo.create({
            "prompt_package_id": "test-package-id",
            "user_id": "test-user-id",
            "provider": "mock",
            "model": "mock-model",
            "status": "pending",
        })
        self.db.commit()

        updated = repo.update(execution.id, {
            "status": "completed",
            "total_tokens": 100,
        })
        self.db.commit()

        assert updated.status == "completed"
        assert updated.total_tokens == 100


# ============================================================
# AIExecutionService Tests
# ============================================================

class TestAIExecutionService:
    def setup_method(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base

        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def teardown_method(self):
        self.db.close()

    def _create_mock_package(self, user_id="test-user-id"):
        from app.repositories.prompt_intelligence import PromptPackageRepository

        package_repo = PromptPackageRepository(self.db)
        package = package_repo.create({
            "user_id": user_id,
            "prompt_type": "resume_tailoring",
            "system_prompt": "You are a helpful assistant.",
            "resume_context": {"skills": ["Python", "FastAPI"]},
            "opportunity_context": {"requirements": ["Python", "Docker"]},
            "is_validated": True,
            "version": "1.0",
        })
        self.db.commit()
        return package

    @patch('app.services.ai_execution.service.get_ai_service')
    def test_execute_prompt_package_success(self, mock_get_ai_service):
        mock_service = MagicMock()
        mock_service.provider_name = "openai"
        mock_service.model = "gpt-4o-mini"
        mock_service.config = MagicMock()
        mock_service.config.model = "gpt-4o-mini"

        mock_response = ProviderResponse(
            content='{"result": "success"}',
            model="gpt-4o-mini",
            provider=ProviderType.OPENAI,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            latency_ms=100.0,
        )
        mock_service.generate = AsyncMock(return_value=mock_response)
        mock_get_ai_service.return_value = mock_service

        package = self._create_mock_package()
        service = AIExecutionService(self.db)

        result = service.execute_prompt_package(
            user_id="test-user-id",
            prompt_package_id=package.id,
        )

        assert result["status"] == "completed"
        assert result["provider"] == "openai"
        assert result["model"] == "gpt-4o-mini"
        assert result["total_tokens"] == 30
        assert result["parsed_response"] == {"result": "success"}

    def test_execute_prompt_package_not_found(self):
        service = AIExecutionService(self.db)

        with pytest.raises(ValueError, match="Prompt package not found"):
            service.execute_prompt_package(
                user_id="test-user-id",
                prompt_package_id="nonexistent-id",
            )

    def test_execute_prompt_package_wrong_user(self):
        package = self._create_mock_package(user_id="other-user")
        service = AIExecutionService(self.db)

        with pytest.raises(ValueError, match="does not belong to user"):
            service.execute_prompt_package(
                user_id="test-user-id",
                prompt_package_id=package.id,
            )

    @patch('app.services.ai_execution.service.get_ai_service')
    def test_execute_prompt_package_provider_error(self, mock_get_ai_service):
        mock_service = MagicMock()
        mock_service.provider_name = "mock"
        mock_service.model = "mock-model"
        mock_service.generate = AsyncMock(side_effect=AuthenticationError("Invalid key"))
        mock_get_ai_service.return_value = mock_service

        package = self._create_mock_package()
        service = AIExecutionService(self.db)

        with pytest.raises(AuthenticationError):
            service.execute_prompt_package(
                user_id="test-user-id",
                prompt_package_id=package.id,
            )

    def test_get_execution(self):
        from app.repositories.ai_execution import AIExecutionRepository

        package = self._create_mock_package()
        exec_repo = AIExecutionRepository(self.db)
        execution = exec_repo.create({
            "prompt_package_id": package.id,
            "user_id": "test-user-id",
            "provider": "mock",
            "model": "mock-model",
            "status": "completed",
        })
        self.db.commit()

        service = AIExecutionService(self.db)
        result = service.get_execution(execution.id)
        assert result is not None
        assert result.id == execution.id

    def test_get_executions_by_user(self):
        from app.repositories.ai_execution import AIExecutionRepository

        package = self._create_mock_package()
        exec_repo = AIExecutionRepository(self.db)
        exec_repo.create({
            "prompt_package_id": package.id,
            "user_id": "test-user-id",
            "provider": "mock",
            "model": "mock-model",
            "status": "completed",
        })
        self.db.commit()

        service = AIExecutionService(self.db)
        items, total = service.get_executions_by_user("test-user-id")
        assert total == 1
        assert items[0].user_id == "test-user-id"

    def test_build_messages(self):
        package = self._create_mock_package()
        service = AIExecutionService(self.db)

        messages = service._build_messages(package)
        assert len(messages) >= 1
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "You are a helpful assistant."
        assert messages[1]["role"] == "user"
        assert "Resume Context" in messages[1]["content"]
