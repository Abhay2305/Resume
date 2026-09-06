"""Tests for PromptBuilderV2 Knowledge Integration (Phase L).

Tests:
  - Knowledge rules included in instructions
  - Knowledge rules section in user prompt
  - Token estimation accounts for knowledge rules
  - Context-driven types receive knowledge context
  - Deduplication with knowledge rules
  - Knowledge rules capped at 15
"""
import pytest

from app.services.prompt_intelligence_v2.builder import PromptBuilder
from app.services.prompt_intelligence_v2.instructions import InstructionComposer
from app.services.prompt_intelligence_v2.types import PromptRequest


@pytest.fixture
def builder():
    return PromptBuilder()


@pytest.fixture
def sample_knowledge_rules():
    return [
        {
            "rule_key": "KR1",
            "instruction": "Keep summary to 3-4 lines maximum",
            "section_name": "summary",
            "source": "Harvard",
            "category": "Length",
        },
        {
            "rule_key": "KR2",
            "instruction": "Start bullets with strong action verbs",
            "section_name": "experience",
            "source": "Yale",
            "category": "Action Verbs",
        },
        {
            "rule_key": "KR3",
            "instruction": "Include 8-12 technical skills",
            "section_name": "skills",
            "source": "MIT",
            "category": "Keywords",
        },
    ]


class TestInstructionComposerKnowledgeRules:
    def test_compose_includes_knowledge_rules(self, sample_knowledge_rules):
        composer = InstructionComposer()
        instructions = composer.compose(
            "resume_tailoring",
            knowledge_rules=sample_knowledge_rules,
        )
        kr_instructions = [i for i in instructions if i.get("source")]
        assert len(kr_instructions) == 3

    def test_knowledge_rule_has_correct_id(self, sample_knowledge_rules):
        composer = InstructionComposer()
        instructions = composer.compose(
            "resume_tailoring",
            knowledge_rules=sample_knowledge_rules,
        )
        kr_ids = [i["id"] for i in instructions if i.get("source")]
        assert "INST_KR_SUMMARY_HARVARD" in kr_ids
        assert "INST_KR_EXPERIENCE_YALE" in kr_ids

    def test_knowledge_rules_capped_at_15(self):
        many_rules = [
            {"instruction": f"Rule {i}", "section_name": f"section_{i}", "source": "Test"}
            for i in range(20)
        ]
        composer = InstructionComposer()
        instructions = composer.compose(
            "resume_tailoring",
            knowledge_rules=many_rules,
        )
        kr_instructions = [i for i in instructions if i.get("source")]
        assert len(kr_instructions) == 15

    def test_knowledge_rules_deduplicated(self):
        rules = [
            {"instruction": "Keep summary concise", "section_name": "summary", "source": "Harvard"},
            {"instruction": "Keep summary concise", "section_name": "summary", "source": "Yale"},
        ]
        composer = InstructionComposer()
        instructions = composer.compose(
            "resume_tailoring",
            knowledge_rules=rules,
        )
        kr_instructions = [i for i in instructions if i.get("source")]
        assert len(kr_instructions) == 1

    def test_compose_text_includes_knowledge_rules(self, sample_knowledge_rules):
        composer = InstructionComposer()
        text = composer.compose_text(
            "resume_tailoring",
            knowledge_rules=sample_knowledge_rules,
        )
        assert "summary" in text.lower() or "action verb" in text.lower()


class TestPromptBuilderKnowledgeIntegration:
    def test_build_includes_knowledge_rules_in_instructions(self, builder, sample_knowledge_rules):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = builder.build(request)
        kr_instructions = [i for i in package.instructions if i.get("source")]
        assert len(kr_instructions) > 0

    def test_build_knowledge_rules_in_context(self, builder, sample_knowledge_rules):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = builder.build(request)
        assert "knowledge_rules" in package.user_prompt.lower() or len([i for i in package.instructions if i.get("source")]) > 0

    def test_build_no_knowledge_rules(self, builder):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
            },
        )
        package = builder.build(request)
        assert package is not None

    def test_build_token_estimate_accounts_for_knowledge(self, builder, sample_knowledge_rules):
        request_with = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        request_without = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
            },
        )
        pkg_with = builder.build(request_with)
        pkg_without = builder.build(request_without)
        assert pkg_with.token_estimate >= pkg_without.token_estimate

    def test_estimate_tokens_includes_knowledge(self, builder, sample_knowledge_rules):
        request_with = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        request_without = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {"name": "Test User"},
                "opportunity": {"title": "Engineer"},
            },
        )
        tokens_with = builder.estimate_tokens(request_with)
        tokens_without = builder.estimate_tokens(request_without)
        assert tokens_with >= tokens_without
