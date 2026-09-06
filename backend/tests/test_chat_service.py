"""Tests for ChatService integration with Prompt Intelligence v2.

Verifies that ChatService._build_messages() delegates to v2 PromptBuilder,
preserves conversation history ordering, and maintains backward compatibility.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.chat_service import ChatService
from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest


class MockChatMessage:
    """Minimal mock for ChatMessage DB model."""

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class TestChatServiceUsesV2Builder:
    """Verify ChatService uses v2 PromptBuilder."""

    def setup_method(self):
        self.service = ChatService()

    def test_service_has_v2_builder(self):
        assert hasattr(self.service, "_prompt_builder_v2")
        assert isinstance(self.service._prompt_builder_v2, PromptBuilderV2)

    def test_build_messages_no_history(self):
        messages = self.service._build_messages([], "Hello")
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"].startswith("Hello")

    def test_system_prompt_is_v2_canonical(self):
        messages = self.service._build_messages([], "Hello")
        system_content = messages[0]["content"]
        # Should contain the career advisor content from v2 templates
        assert "career" in system_content.lower() or "resume" in system_content.lower()
        assert len(system_content) > 100

    def test_system_prompt_matches_v2_template(self):
        from app.services.prompt_intelligence_v2.templates import PromptTemplates
        t = PromptTemplates()
        v2_system = t.get_system("chat")
        messages = self.service._build_messages([], "Hello")
        assert messages[0]["content"] == v2_system

    def test_user_message_preserved(self):
        messages = self.service._build_messages([], "What is the weather?")
        assert messages[1]["content"].startswith("What is the weather?")


class TestConversationHistoryPreservation:
    """Verify conversation history is preserved exactly."""

    def setup_method(self):
        self.service = ChatService()

    def test_single_history_message(self):
        history = [MockChatMessage("user", "Hi")]
        messages = self.service._build_messages(history, "Hello")
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hi"
        assert messages[2]["role"] == "user"
        assert messages[2]["content"].startswith("Hello")

    def test_multiple_history_messages_order(self):
        history = [
            MockChatMessage("user", "Msg 1"),
            MockChatMessage("assistant", "Reply 1"),
            MockChatMessage("user", "Msg 2"),
            MockChatMessage("assistant", "Reply 2"),
        ]
        messages = self.service._build_messages(history, "Msg 3")
        assert len(messages) == 6
        # System
        assert messages[0]["role"] == "system"
        # History (exact order)
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Msg 1"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Reply 1"
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "Msg 2"
        assert messages[4]["role"] == "assistant"
        assert messages[4]["content"] == "Reply 2"
        # New user message
        assert messages[5]["role"] == "user"
        assert messages[5]["content"].startswith("Msg 3")

    def test_history_roles_preserved(self):
        history = [
            MockChatMessage("user", "U1"),
            MockChatMessage("assistant", "A1"),
            MockChatMessage("user", "U2"),
        ]
        messages = self.service._build_messages(history, "U3")
        roles = [m["role"] for m in messages]
        assert roles == ["system", "user", "assistant", "user", "user"]

    def test_history_content_preserved_exactly(self):
        history = [
            MockChatMessage("user", "Special chars: <>&\"'"),
            MockChatMessage("assistant", "Response with\nnewlines"),
        ]
        messages = self.service._build_messages(history, "Test")
        assert messages[1]["content"] == "Special chars: <>&\"'"
        assert messages[2]["content"] == "Response with\nnewlines"

    def test_empty_history_no_extra_messages(self):
        messages = self.service._build_messages([], "Hello")
        assert len(messages) == 2


class TestChatServicePublicBehavior:
    """Verify ChatService public API remains unchanged."""

    def setup_method(self):
        self.service = ChatService()

    def test_send_message_signature_unchanged(self):
        import inspect
        sig = inspect.signature(self.service.send_message)
        params = list(sig.parameters.keys())
        # inspect.signature on instance method excludes 'self'
        assert params == ["db", "session_id", "user_message"]

    def test_build_messages_returns_list_of_dicts(self):
        messages = self.service._build_messages([], "Hello")
        assert isinstance(messages, list)
        for msg in messages:
            assert isinstance(msg, dict)
            assert "role" in msg
            assert "content" in msg

    def test_messages_compatible_with_generate(self):
        messages = self.service._build_messages([], "Hello")
        for msg in messages:
            assert msg["role"] in ("system", "user", "assistant")
            assert isinstance(msg["content"], str)


class TestChatServiceWithProvider:
    """Integration test with mocked AI provider."""

    def setup_method(self):
        from app.services.ai_service import UniversalAIService, ProviderConfig, ProviderType
        self.provider = UniversalAIService(
            config=ProviderConfig(
                provider_type=ProviderType.OPENAI,
                api_key="test-key",
                model="gpt-4o-mini",
                max_retries=0,
            )
        )
        self.service = ChatService(provider=self.provider)

    @pytest.mark.asyncio
    async def test_send_message_calls_provider_with_correct_format(self):
        mock_response = MagicMock()
        mock_response.content = "Hello! I can help with your resume."
        mock_response.model = "gpt-4o-mini"
        mock_response.total_tokens = 30
        mock_response.prompt_tokens = 10
        mock_response.completion_tokens = 20

        with patch.object(self.provider, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            # Mock DB operations
            mock_db = MagicMock()
            mock_session = MagicMock()
            mock_session.id = "test-session"
            mock_session.status = "active"

            # Mock get_session to return a valid session
            with patch.object(self.service, 'get_session', return_value=mock_session):
                with patch.object(self.service, 'get_session_messages', return_value=[]):
                    with patch.object(self.service, 'create_session', return_value=mock_session):
                        result = await self.service.send_message(
                            mock_db, "test-session", "Hello"
                        )

                        # Verify generate was called
                        assert mock_gen.called
                        call_args = mock_gen.call_args
                        messages = call_args[0][0]

                        # Verify message format
                        assert isinstance(messages, list)
                        assert len(messages) == 2
                        assert messages[0]["role"] == "system"
                        assert messages[1]["role"] == "user"
                        assert messages[1]["content"].startswith("Hello")
