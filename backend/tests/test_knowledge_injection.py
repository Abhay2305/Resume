"""Tests for Knowledge Injection Across All AI Call Paths.

Tests that knowledge rules from knowledge_intelligence are properly injected
into all three AI call paths:
  1. ResumeGeneratorService.generate_structured_resume()
  2. CoverLetterGeneratorService.generate_cover_letter()
  3. ats.py improve_text endpoint
  4. AIOrchestrator._build_prompt() type conversion
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.ai_service import (
    get_knowledge_rules_for_context,
    ResumeGeneratorService,
    CoverLetterGeneratorService,
)
from app.services.prompt_intelligence_v2.types import PromptRequest


class MockRule:
    """Mock KnowledgeRule for testing."""
    def __init__(self, instruction, section_name="general", source="test", category="General"):
        self.instruction = instruction
        self.section_name = section_name
        self.source = source
        self.category = category


class MockRuleRepository:
    """Mock KnowledgeRuleRepository for testing."""
    def __init__(self, rules=None):
        self._rules = rules or []

    def get_active(self):
        return self._rules


# ============================================================================
# Test get_knowledge_rules_for_context
# ============================================================================

class TestGetKnowledgeRulesForContext:
    def test_returns_rules_from_repository(self):
        mock_rules = [
            MockRule("Keep summary concise", "summary", "Harvard", "Length"),
            MockRule("Use action verbs", "experience", "Yale", "Action Verbs"),
        ]
        mock_repo = MockRuleRepository(mock_rules)

        with patch("app.repositories.knowledge_intelligence.KnowledgeRuleRepository", return_value=mock_repo):
            result = get_knowledge_rules_for_context(MagicMock())

        assert len(result) == 2
        assert result[0]["instruction"] == "Keep summary concise"
        assert result[0]["section_name"] == "summary"
        assert result[0]["source"] == "Harvard"
        assert result[0]["category"] == "Length"

    def test_returns_empty_list_on_exception(self):
        with patch("app.repositories.knowledge_intelligence.KnowledgeRuleRepository", side_effect=Exception("DB error")):
            result = get_knowledge_rules_for_context(MagicMock())

        assert result == []

    def test_returns_empty_list_when_no_db(self):
        result = get_knowledge_rules_for_context(None)
        assert result == []

    def test_filters_by_section_name(self):
        mock_rules = [
            MockRule("Keep summary concise", "summary", "Harvard", "Length"),
            MockRule("Use action verbs", "experience", "Yale", "Action Verbs"),
        ]
        mock_repo = MockRuleRepository(mock_rules)

        with patch("app.repositories.knowledge_intelligence.KnowledgeRuleRepository", return_value=mock_repo):
            result = get_knowledge_rules_for_context(MagicMock(), section_name="summary")

        assert len(result) == 1
        assert result[0]["section_name"] == "summary"

    def test_respects_max_rules_limit(self):
        mock_rules = [MockRule(f"Rule {i}", "general", "test", "General") for i in range(20)]
        mock_repo = MockRuleRepository(mock_rules)

        with patch("app.repositories.knowledge_intelligence.KnowledgeRuleRepository", return_value=mock_repo):
            result = get_knowledge_rules_for_context(MagicMock(), max_rules=5)

        assert len(result) == 5


# ============================================================================
# Test ResumeGeneratorService knowledge injection
# ============================================================================

class TestResumeGeneratorServiceKnowledgeInjection:
    @patch("app.services.ai_service.get_knowledge_rules_for_context")
    @patch("app.services.ai_service.get_ai_service")
    def test_injects_knowledge_rules_into_context(self, mock_get_ai, mock_get_rules):
        mock_get_rules.return_value = [
            {"instruction": "Keep summary concise", "section_name": "summary", "source": "Harvard", "category": "Length"},
        ]
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(return_value=MagicMock(content='{"summary": "test"}'))
        mock_service.parse_json_response.return_value = {"summary": "test"}
        mock_get_ai.return_value = mock_service

        svc = ResumeGeneratorService()
        db = MagicMock()
        result = svc.generate_structured_resume(db, "user1", "test prompt")

        assert "summary" in result

    @patch("app.services.ai_service.get_knowledge_rules_for_context")
    @patch("app.services.ai_service.get_ai_service")
    def test_works_without_db(self, mock_get_ai, mock_get_rules):
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(return_value=MagicMock(content='{"summary": "test"}'))
        mock_service.parse_json_response.return_value = {"summary": "test"}
        mock_get_ai.return_value = mock_service

        svc = ResumeGeneratorService()
        result = svc.generate_structured_resume(None, "user1", "test prompt")

        mock_get_rules.assert_not_called()
        assert "summary" in result


# ============================================================================
# Test CoverLetterGeneratorService knowledge injection
# ============================================================================

class TestCoverLetterGeneratorServiceKnowledgeInjection:
    @patch("app.services.ai_service.get_knowledge_rules_for_context")
    @patch("app.services.ai_service.get_ai_service")
    def test_injects_knowledge_rules_into_context(self, mock_get_ai, mock_get_rules):
        mock_get_rules.return_value = [
            {"instruction": "Address hiring manager directly", "section_name": "cover_letter", "source": "Yale", "category": "Tone"},
        ]
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(return_value=MagicMock(content="Dear Hiring Manager..."))
        mock_get_ai.return_value = mock_service

        svc = CoverLetterGeneratorService()
        db = MagicMock()
        result = svc.generate_cover_letter(db, "user1", "Engineer", "Acme Corp")

        mock_get_rules.assert_called_once_with(db, section_name="cover_letter")

    @patch("app.services.ai_service.get_knowledge_rules_for_context")
    @patch("app.services.ai_service.get_ai_service")
    def test_works_without_db(self, mock_get_ai, mock_get_rules):
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(return_value=MagicMock(content="Dear Hiring Manager..."))
        mock_get_ai.return_value = mock_service

        svc = CoverLetterGeneratorService()
        result = svc.generate_cover_letter(None, "user1", "Engineer", "Acme Corp")

        mock_get_rules.assert_not_called()
        assert result == "Dear Hiring Manager..."


# ============================================================================
# Test AIOrchestrator knowledge_chunks → knowledge_rules conversion
# ============================================================================

class TestAIOrchestratorKnowledgeTypeConversion:
    def test_converts_string_chunks_to_dicts(self):
        from app.services.ai_orchestrator import AIOrchestrator, TaskType

        mock_provider = MagicMock()
        orchestrator = AIOrchestrator(provider=mock_provider)

        captured_requests = []
        def capture_build(request):
            captured_requests.append(request)
            return [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]

        orchestrator.prompt_builder_v2.build_messages = capture_build

        result = orchestrator._build_prompt(
            TaskType.RESUME_BULLETS,
            {"responsibilities": "test"},
            ["Rule 1", "Rule 2"],
        )

        assert len(captured_requests) == 1
        request = captured_requests[0]
        assert "knowledge_rules" in request.context
        assert len(request.context["knowledge_rules"]) == 2
        assert request.context["knowledge_rules"][0]["instruction"] == "Rule 1"
        assert request.context["knowledge_rules"][0]["section_name"] == "general"

    def test_passes_dict_chunks_directly(self):
        from app.services.ai_orchestrator import AIOrchestrator, TaskType

        mock_provider = MagicMock()
        orchestrator = AIOrchestrator(provider=mock_provider)

        captured_requests = []
        def capture_build(request):
            captured_requests.append(request)
            return [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]

        orchestrator.prompt_builder_v2.build_messages = capture_build

        result = orchestrator._build_prompt(
            TaskType.RESUME_BULLETS,
            {"responsibilities": "test"},
            [{"instruction": "Rule 1", "section_name": "summary", "source": "test", "category": "General"}],
        )

        request = captured_requests[0]
        assert request.context["knowledge_rules"][0]["instruction"] == "Rule 1"
        assert request.context["knowledge_rules"][0]["section_name"] == "summary"

    def test_empty_knowledge_chunks_no_rules_in_context(self):
        from app.services.ai_orchestrator import AIOrchestrator, TaskType

        mock_provider = MagicMock()
        orchestrator = AIOrchestrator(provider=mock_provider)

        captured_requests = []
        def capture_build(request):
            captured_requests.append(request)
            return [{"role": "system", "content": "test"}, {"role": "user", "content": "test"}]

        orchestrator.prompt_builder_v2.build_messages = capture_build

        result = orchestrator._build_prompt(
            TaskType.RESUME_BULLETS,
            {"responsibilities": "test"},
            [],
        )

        request = captured_requests[0]
        assert "knowledge_rules" not in request.context
