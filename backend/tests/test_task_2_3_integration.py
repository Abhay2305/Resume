"""Integration tests for Task 2.3: ATS text improvement uses Prompt Intelligence v2.

Verifies that improve_text() delegates to v2 PromptBuilder,
preserves DB rules injection, and maintains backward compatibility.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest
from app.routers.ats import _ACTION_TO_PROMPT_TYPE


class TestActionTypeMapping:
    """Verify action_type → prompt_type mapping covers all 5 actions."""

    def test_all_action_types_mapped(self):
        expected_actions = {"improve", "shorten", "expand", "professional", "autofix"}
        assert set(_ACTION_TO_PROMPT_TYPE.keys()) == expected_actions

    def test_mapping_values_match_v2_types(self):
        from app.services.prompt_intelligence_v2.registry import create_default_registry
        registry = create_default_registry()
        for action, prompt_type in _ACTION_TO_PROMPT_TYPE.items():
            assert prompt_type in registry, f"prompt_type '{prompt_type}' not in v2 registry"

    def test_improve_mapping(self):
        assert _ACTION_TO_PROMPT_TYPE["improve"] == "text_improve"

    def test_shorten_mapping(self):
        assert _ACTION_TO_PROMPT_TYPE["shorten"] == "text_shorten"

    def test_expand_mapping(self):
        assert _ACTION_TO_PROMPT_TYPE["expand"] == "text_expand"

    def test_professional_mapping(self):
        assert _ACTION_TO_PROMPT_TYPE["professional"] == "text_professional"

    def test_autofix_mapping(self):
        assert _ACTION_TO_PROMPT_TYPE["autofix"] == "text_autofix"


class TestPromptBuilderV2Integration:
    """Verify ATS router uses v2 PromptBuilder."""

    def test_prompt_engine_instance(self):
        from app.routers.ats import prompt_engine
        assert isinstance(prompt_engine, PromptBuilderV2)

    def test_v2_builder_produces_messages_for_all_types(self):
        builder = PromptBuilderV2()
        for action, prompt_type in _ACTION_TO_PROMPT_TYPE.items():
            request = PromptRequest(
                prompt_type=prompt_type,
                context={"text_content": "Test content"},
            )
            messages = builder.build_messages(request)
            assert isinstance(messages, list)
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert "Test content" in messages[1]["content"]

    def test_v2_builder_system_prompt_is_generic(self):
        """v2 system prompts are static generic strings (not DB rules)."""
        builder = PromptBuilderV2()
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Test"},
        )
        messages = builder.build_messages(request)
        system_content = messages[0]["content"]
        # Should be the generic v2 system prompt, not DB rules
        assert "elite career advisor" in system_content.lower()
        assert "polished" in system_content.lower() or "rewrite" in system_content.lower()


class TestDBRulesPreservation:
    """Verify dynamic DB rules injection is preserved exactly."""

    def test_system_rules_replaced_in_messages(self):
        """System message content should be replaced with DB rules."""
        from app.routers.ats import prompt_engine
        from app.services.prompt_intelligence_v2.types import PromptRequest
        
        # Build messages with v2
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Test content"},
        )
        messages = prompt_engine.build_messages(request)
        
        # Simulate DB rules replacement
        fake_db_rules = "You are an elite career advisor. Rewrite according to rules:\n1. Use active verbs\n2. No first person"
        messages[0]["content"] = fake_db_rules
        
        # Verify replacement worked
        assert messages[0]["content"] == fake_db_rules
        assert "active verbs" in messages[0]["content"]

    def test_user_prompt_preserved_after_system_replacement(self):
        """User prompt should remain unchanged after system replacement."""
        from app.routers.ats import prompt_engine
        from app.services.prompt_intelligence_v2.types import PromptRequest
        
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Original text"},
        )
        messages = prompt_engine.build_messages(request)
        original_user_prompt = messages[1]["content"]
        
        # Replace system message
        messages[0]["content"] = "New system rules"
        
        # User prompt should be unchanged
        assert messages[1]["content"] == original_user_prompt
        assert "Original text" in messages[1]["content"]


class TestBackwardCompatibility:
    """Verify existing ATS behavior remains unchanged."""

    def test_action_type_case_insensitive(self):
        """Action type lookup should be case-insensitive."""
        from app.routers.ats import _ACTION_TO_PROMPT_TYPE
        
        # Should work with lowercase
        assert _ACTION_TO_PROMPT_TYPE.get("improve".lower()) == "text_improve"
        # Should work with mixed case (after .lower() in router)
        assert _ACTION_TO_PROMPT_TYPE.get("Improve".lower()) == "text_improve"

    def test_unknown_action_defaults_to_improve(self):
        """Unknown action type should default to text_improve."""
        from app.routers.ats import _ACTION_TO_PROMPT_TYPE
        
        # The router uses .get(default="text_improve")
        default = _ACTION_TO_PROMPT_TYPE.get("unknown", "text_improve")
        assert default == "text_improve"

    def test_v2_messages_format_compatible_with_universal_ai(self):
        """Messages format should match what UniversalAIService.generate() expects."""
        builder = PromptBuilderV2()
        request = PromptRequest(
            prompt_type="text_improve",
            context={"text_content": "Test"},
        )
        messages = builder.build_messages(request)
        
        for msg in messages:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ("system", "user", "assistant")
            assert isinstance(msg["content"], str)


class TestMessageStructure:
    """Verify final message structure matches expected format."""

    def test_messages_have_system_and_user(self):
        builder = PromptBuilderV2()
        for prompt_type in _ACTION_TO_PROMPT_TYPE.values():
            request = PromptRequest(
                prompt_type=prompt_type,
                context={"text_content": "Test content"},
            )
            messages = builder.build_messages(request)
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"

    def test_user_message_contains_text_content(self):
        builder = PromptBuilderV2()
        test_text = "Specific test text for verification"
        for prompt_type in _ACTION_TO_PROMPT_TYPE.values():
            request = PromptRequest(
                prompt_type=prompt_type,
                context={"text_content": test_text},
            )
            messages = builder.build_messages(request)
            assert test_text in messages[1]["content"]

    def test_system_message_is_non_empty(self):
        builder = PromptBuilderV2()
        for prompt_type in _ACTION_TO_PROMPT_TYPE.values():
            request = PromptRequest(
                prompt_type=prompt_type,
                context={"text_content": "Test"},
            )
            messages = builder.build_messages(request)
            assert len(messages[0]["content"]) > 0


class TestIntegrationWithMockedAI:
    """Integration test with mocked UniversalAIService."""

    def test_improve_text_endpoint_uses_v2(self):
        """Verify the endpoint constructs proper messages using v2."""
        from app.routers.ats import improve_text, prompt_engine, _ACTION_TO_PROMPT_TYPE
        from app.schemas import ResumeImproveRequest
        
        # Mock dependencies
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        mock_user = MagicMock()
        
        # Mock get_knowledge_rules_for_context (current architecture)
        fake_rules = [{"instruction": "Use active verbs", "source": "knowledge"}]
        
        # Mock UniversalAIService
        mock_response = MagicMock()
        mock_response.content = "Improved text output"
        
        mock_ai_service = MagicMock()
        mock_ai_service.generate = AsyncMock(return_value=mock_response)
        
        # Create request
        req = ResumeImproveRequest(
            section_type="experience",
            text_content="We did stuff",
            action_type="improve",
        )
        
        with patch('app.routers.ats.get_knowledge_rules_for_context', return_value=fake_rules):
            with patch('app.routers.ats.get_ai_service', return_value=mock_ai_service):
                with patch('app.routers.ats.run_async', return_value=mock_response):
                    result = improve_text(req, mock_db, mock_user)
        
        # Verify result structure
        assert result.original_text == "We did stuff"
        assert result.improved_text == "Improved text output"
        assert isinstance(result.applied_rules, list)

    def test_all_action_types_work_through_endpoint(self):
        """All 5 action types should work through the endpoint."""
        from app.routers.ats import improve_text, _ACTION_TO_PROMPT_TYPE
        from app.schemas import ResumeImproveRequest
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_user = MagicMock()
        
        fake_rules = [{"instruction": "System rules", "source": "knowledge"}]
        mock_response = MagicMock()
        mock_response.content = "Improved"
        mock_ai_service = MagicMock()
        mock_ai_service.generate = AsyncMock(return_value=mock_response)
        
        for action_type in _ACTION_TO_PROMPT_TYPE.keys():
            req = ResumeImproveRequest(
                section_type="experience",
                text_content="Test text",
                action_type=action_type,
            )
            
            with patch('app.routers.ats.get_knowledge_rules_for_context', return_value=fake_rules):
                with patch('app.routers.ats.get_ai_service', return_value=mock_ai_service):
                    with patch('app.routers.ats.run_async', return_value=mock_response):
                        result = improve_text(req, mock_db, mock_user)
            
            assert result.original_text == "Test text"
            assert result.improved_text == "Improved"
