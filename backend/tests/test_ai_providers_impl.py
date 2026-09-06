"""Tests for provider implementations and ProviderFactory."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.ai.error_classifier import AuthenticationError, ProviderUnavailableError
from app.services.ai.provider_factory import ProviderFactory
from app.services.ai.providers.gemini import GeminiProvider
from app.services.ai.providers.openai import OpenAIProvider
from app.services.ai.providers.anthropic import AnthropicProvider
from app.services.ai.types import ProviderConfig, ProviderResponse, ProviderType


class TestProviderFactory:
    def test_creates_gemini_provider(self):
        config = ProviderConfig(provider_type=ProviderType.GEMINI, api_key="key")
        provider = ProviderFactory.create(config)
        assert isinstance(provider, GeminiProvider)

    def test_creates_openai_provider(self):
        config = ProviderConfig(provider_type=ProviderType.OPENAI, api_key="key")
        provider = ProviderFactory.create(config)
        assert isinstance(provider, OpenAIProvider)

    def test_creates_anthropic_provider(self):
        config = ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="key")
        provider = ProviderFactory.create(config)
        assert isinstance(provider, AnthropicProvider)

    def test_unknown_provider_raises(self):
        from app.services.ai.types import ProviderType
        config = ProviderConfig(provider_type="unknown")
        with pytest.raises(ValueError, match="Unknown provider type"):
            ProviderFactory.create(config)


class TestOpenAIProvider:
    @pytest.mark.asyncio
    async def test_generate_returns_content(self):
        config = ProviderConfig(provider_type=ProviderType.OPENAI, api_key="test-key", model="gpt-4o-mini")
        provider = OpenAIProvider(config)

        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello"), finish_reason="stop")]
        mock_response.model = "gpt-4o-mini"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15

        mock_openai = MagicMock()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        mock_openai.AsyncOpenAI.return_value = mock_client

        with patch.dict("sys.modules", {"openai": mock_openai}):
            messages = [{"role": "user", "content": "Hello"}]
            response = await provider.generate(messages, "gpt-4o-mini", 0.7, 2048)
            assert response.content == "Hello"
            assert response.provider == ProviderType.OPENAI
            assert response.prompt_tokens == 10

    @pytest.mark.asyncio
    async def test_auth_error_no_key(self):
        config = ProviderConfig(provider_type=ProviderType.OPENAI, api_key="")
        provider = OpenAIProvider(config)
        with pytest.raises(AuthenticationError):
            await provider.generate([{"role": "user", "content": "Hi"}], "gpt-4o", 0.7, 100)

    @pytest.mark.asyncio
    async def test_import_error(self):
        config = ProviderConfig(provider_type=ProviderType.OPENAI, api_key="key")
        provider = OpenAIProvider(config)
        with patch.dict("sys.modules", {"openai": None}):
            with pytest.raises(ProviderUnavailableError):
                await provider.generate([{"role": "user", "content": "Hi"}], "gpt-4o", 0.7, 100)


class TestGeminiProvider:
    @pytest.mark.asyncio
    async def test_generate_returns_content(self):
        config = ProviderConfig(provider_type=ProviderType.GEMINI, api_key="test-key", model="gemini-2.0-flash")
        provider = GeminiProvider(config)

        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini"
        mock_response.candidates = [MagicMock(finish_reason="STOP")]
        mock_response.prompt_feedback.block_reason = None
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mock_response.usage_metadata.total_token_count = 15

        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict("sys.modules", {"google.generativeai": mock_genai}):
            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ]
            response = await provider.generate(messages, "gemini-2.0-flash", 0.7, 2048)
            assert response.content == "Hello from Gemini"
            assert response.prompt_tokens == 10

    @pytest.mark.asyncio
    async def test_auth_error_no_key(self):
        config = ProviderConfig(provider_type=ProviderType.GEMINI, api_key="")
        provider = GeminiProvider(config)
        with pytest.raises(AuthenticationError):
            await provider.generate([{"role": "user", "content": "Hi"}], "gemini-2.0-flash", 0.7, 100)

    @pytest.mark.asyncio
    async def test_import_error(self):
        config = ProviderConfig(provider_type=ProviderType.GEMINI, api_key="key")
        provider = GeminiProvider(config)
        with patch.dict("sys.modules", {"google.generativeai": None}):
            with pytest.raises(ProviderUnavailableError):
                await provider.generate([{"role": "user", "content": "Hi"}], "gemini-2.0-flash", 0.7, 100)


class TestAnthropicProvider:
    @pytest.mark.asyncio
    async def test_generate_returns_content(self):
        config = ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="test-key", model="claude-sonnet-4")
        provider = AnthropicProvider(config)

        mock_content = MagicMock()
        mock_content.text = "Hello from Claude"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        mock_response.model = "claude-sonnet-4"
        mock_response.stop_reason = "end_turn"
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 5

        mock_anthropic = MagicMock()
        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        with patch.dict("sys.modules", {"anthropic": mock_anthropic}):
            messages = [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hello"},
            ]
            response = await provider.generate(messages, "claude-sonnet-4", 0.7, 2048)
            assert response.content == "Hello from Claude"
            assert response.prompt_tokens == 10
            assert response.completion_tokens == 5

    @pytest.mark.asyncio
    async def test_auth_error_no_key(self):
        config = ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="")
        provider = AnthropicProvider(config)
        with pytest.raises(AuthenticationError):
            await provider.generate([{"role": "user", "content": "Hi"}], "claude-sonnet-4", 0.7, 100)

    @pytest.mark.asyncio
    async def test_import_error(self):
        config = ProviderConfig(provider_type=ProviderType.ANTHROPIC, api_key="key")
        provider = AnthropicProvider(config)
        with patch.dict("sys.modules", {"anthropic": None}):
            with pytest.raises(ProviderUnavailableError):
                await provider.generate([{"role": "user", "content": "Hi"}], "claude-sonnet-4", 0.7, 100)
