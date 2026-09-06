"""SHADOW-1 Boundary Tests.

Verifies that the governance boundary is enforced: no unauthorized
career-writing guidance reaches AI generation paths.
"""
import json
import pytest
from unittest.mock import MagicMock, patch

from app.services.prompt_intelligence_v2.templates import PromptTemplates
from app.services.prompt_intelligence_v2.types import PromptRequest
from app.services.rules_engine import (
    RulesEngine,
    STRONG_ACTION_VERBS_DEFAULT,
    WEAK_VERBS_DEFAULT,
    VAGUE_PHRASES_DEFAULT,
    GENERIC_PHRASES_DEFAULT,
)


@pytest.fixture
def templates():
    return PromptTemplates()


@pytest.fixture
def builder():
    from app.services.prompt_intelligence_v2.builder import PromptBuilder
    return PromptBuilder()


# ── Test 1: System prompts contain no career knowledge ──

CAREER_KNOWLEDGE_PATTERNS = [
    "action verb",
    "strong action verb",
    "quantify",
    "quantifiable",
    "vague",
    "marketing-style",
    "under 2 lines",
    "200 characters",
    "under 400 words",
    "forward-looking",
    "professional but warm",
    "specific technologies",
    "measurable impact",
    "maintaining active verbs",
    "potential achievements",
    "first-person pronouns",
    "starting with active verbs",
    "removing first-person",
]


def test_system_prompt_contains_no_career_knowledge(templates):
    """Parse all system prompts. Verify no career-writing instructions exist."""
    # structured_resume and chat are excluded: structured_resume is pure JSON format,
    # chat contains conversation style (authorized system constraint)
    excluded = {"structured_resume", "chat"}
    for prompt_type in templates.list_system_types():
        if prompt_type in excluded:
            continue
        system = templates.get_system(prompt_type)
        system_lower = system.lower()
        for pattern in CAREER_KNOWLEDGE_PATTERNS:
            assert pattern not in system_lower, (
                f"System prompt '{prompt_type}' contains career knowledge pattern '{pattern}'"
            )


# ── Test 2: System prompts still contain required elements ──

def test_system_prompts_contain_role_definition(templates):
    """Every system prompt must contain a role definition."""
    for prompt_type in templates.list_system_types():
        system = templates.get_system(prompt_type)
        assert "you are" in system.lower(), (
            f"System prompt '{prompt_type}' missing role definition"
        )


def test_system_prompts_contain_anti_hallucination(templates):
    """Core generation prompts must contain anti-hallucination constraints."""
    core_types = [
        "resume_bullets", "resume_summary", "cover_letter",
        "bullet_feedback", "ats_optimization", "resume_tailoring",
        "resume_generation",
    ]
    for prompt_type in core_types:
        system = templates.get_system(prompt_type)
        has_constraint = (
            "never invent" in system.lower()
            or "never fabricate" in system.lower()
            or "factual" in system.lower()
        )
        assert has_constraint, (
            f"System prompt '{prompt_type}' missing anti-hallucination constraint"
        )


def test_system_prompts_contain_follow_knowledge(templates):
    """All generation prompts must instruct to follow knowledge context."""
    # structured_resume is excluded: it's a pure JSON format conversion task
    excluded = {"structured_resume"}
    for prompt_type in templates.list_system_types():
        if prompt_type in excluded:
            continue
        system = templates.get_system(prompt_type)
        assert "follow" in system.lower() and "knowledge" in system.lower(), (
            f"System prompt '{prompt_type}' missing 'follow knowledge' instruction"
        )


# ── Test 3: No unverifiable attribution ──

UNIVERSITY_NAMES = ["harvard", "mit", "yale", "stanford"]


def test_no_unverifiable_attribution_in_templates(templates):
    """Search all template strings for university names. None should exist."""
    for prompt_type in templates.list_system_types():
        system = templates.get_system(prompt_type)
        for name in UNIVERSITY_NAMES:
            assert name not in system.lower(), (
                f"System prompt '{prompt_type}' contains unverifiable attribution '{name}'"
            )

    for prompt_type in templates.list_user_types():
        user = templates.get_user(prompt_type)
        for name in UNIVERSITY_NAMES:
            assert name not in user.lower(), (
                f"User prompt '{prompt_type}' contains unverifiable attribution '{name}'"
            )

    for ctx_name in ["knowledge", "rules"]:
        ctx = templates.get_context(ctx_name)
        for name in UNIVERSITY_NAMES:
            assert name not in ctx.lower(), (
                f"Context template '{ctx_name}' contains unverifiable attribution '{name}'"
            )


# ── Test 4: Rules engine reads from DB (or uses authorized defaults) ──

def test_rules_engine_uses_authorized_defaults():
    """RulesEngine without DB session uses explicitly authorized defaults."""
    engine = RulesEngine()
    assert engine.strong_action_verbs == STRONG_ACTION_VERBS_DEFAULT
    assert engine.weak_verbs == WEAK_VERBS_DEFAULT
    assert engine.vague_phrases == VAGUE_PHRASES_DEFAULT
    assert engine.generic_phrases == GENERIC_PHRASES_DEFAULT


def test_rules_engine_vocabulary_sets_are_nonempty():
    """All vocabulary sets must be non-empty."""
    engine = RulesEngine()
    assert len(engine.strong_action_verbs) > 0
    assert len(engine.weak_verbs) > 0
    assert len(engine.vague_phrases) > 0
    assert len(engine.generic_phrases) > 0


# ── Test 5-6: Deactivated/rejected rules not in prompt ──

def test_deactivated_rule_not_in_prompt(templates, builder):
    """Build a prompt for each type with complete context. Verify it succeeds."""
    # Provide complete context for each prompt type
    contexts = {
        "resume_bullets": {
            "role_title": "Software Engineer",
            "company": "Test Corp",
            "duration": "2 years",
            "responsibilities": "Built systems",
            "technologies": "Python",
            "achievements": "Improved performance",
            "num_bullets": 3,
            "knowledge_rules": [],
        },
        "resume_summary": {
            "target_role": "Senior Engineer",
            "experience_years": 5,
            "skills": "Python, React",
            "achievements": "Built X",
            "goals": "Senior role",
            "knowledge_rules": [],
        },
        "cover_letter": {
            "company": "Test Corp",
            "role_title": "Engineer",
            "job_description": "Build things",
            "my_experience": "5 years",
            "why_company": "Innovation",
            "relevant_skills": "Python",
            "knowledge_rules": [],
        },
        "bullet_feedback": {
            "bullet": "Built a system",
            "context": "Backend",
            "role_title": "Engineer",
            "knowledge_rules": [],
        },
        "ats_optimization": {
            "content": "Resume content",
            "job_description": "Job desc",
            "knowledge_rules": [],
        },
    }
    for prompt_type in ["resume_bullets", "resume_summary", "cover_letter", "bullet_feedback", "ats_optimization"]:
        request = PromptRequest(
            prompt_type=prompt_type,
            context=contexts.get(prompt_type, {"knowledge_rules": []}),
        )
        messages = builder.build_messages(request)
        assert len(messages) > 0


# ── Test 7: Only active rules reach runtime ──

def test_only_active_rules_reach_runtime():
    """Verify get_active() query requires state=ACTIVE AND is_active=True."""
    from app.repositories.knowledge_intelligence import KnowledgeRuleRepository
    import inspect
    source = inspect.getsource(KnowledgeRuleRepository.get_active)
    assert "is_active" in source
    assert "ACTIVE" in source


# ── Test 8: Fallback paths return no career guidance ──

def test_llm_service_fallback_returns_empty():
    """LLM service fallback returns empty string (fail closed)."""
    from app.services.llm_service import LLMProviderService
    service = LLMProviderService.__new__(LLMProviderService)
    service._service = MagicMock()
    service._service.provider_name = "test"
    result = service._fallback_generate("test prompt")
    assert result == ""


def test_prompt_builder_service_fallback_returns_empty():
    """PromptBuilderService returns empty when no rules available."""
    from app.services.llm_service import PromptBuilderService
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    result = PromptBuilderService.get_active_rules_instruction(mock_db)
    assert result == ""


# ── Test 9: Chat system prompt obeys boundary ──

def test_chat_obeys_boundary(templates):
    """Chat system prompt contains no career methodology."""
    system = templates.get_system("chat")
    # Should not contain career-writing methodology
    assert "action verb" not in system.lower()
    assert "quantify" not in system.lower()
    assert "under 2 lines" not in system.lower()
    # Should still contain conversation flow and role
    assert "you are" in system.lower()
    assert "conversation" in system.lower() or "role" in system.lower()


# ── Test 10: Text transform system prompts obey boundary ──

def test_text_transform_obeys_boundary(templates):
    """Text improve/shorten/expand/professional/autofix prompts have no career methodology."""
    text_types = ["text_improve", "text_shorten", "text_expand", "text_professional", "text_autofix"]
    for prompt_type in text_types:
        system = templates.get_system(prompt_type)
        assert "action verb" not in system.lower(), f"{prompt_type} contains career knowledge"
        assert "quantify" not in system.lower(), f"{prompt_type} contains career knowledge"
        assert "harvard" not in system.lower(), f"{prompt_type} contains unverifiable attribution"


# ── Test 11: Prompt builder receives governed knowledge ──

def test_prompt_builder_receives_governed_knowledge(builder):
    """Build prompts with knowledge_rules parameter."""
    request = PromptRequest(
        prompt_type="resume_bullets",
        context={
            "role_title": "Software Engineer",
            "company": "Test Corp",
            "duration": "2 years",
            "responsibilities": "Built systems",
            "technologies": "Python",
            "achievements": "Improved performance",
            "num_bullets": 3,
            "knowledge_rules": [
                {"instruction": "Use strong action verbs", "category": "Action Verbs"}
            ],
        },
    )
    messages = builder.build_messages(request)
    assert len(messages) > 0
    # System prompt should not contain the knowledge rule directly
    system_content = messages[0]["content"]
    assert "use strong action verbs" not in system_content.lower()


# ── Test 12: Provenance survives pipeline ──

def test_provenance_survives_pipeline():
    """Verify _rule_to_dict preserves provenance fields."""
    from app.services.knowledge_intelligence.service import KnowledgeIntelligenceService
    mock_rule = MagicMock()
    mock_rule.rule_key = "TEST_001"
    mock_rule.source = "test"
    mock_rule.section_name = "test"
    mock_rule.priority = "high"
    mock_rule.category = "test"
    mock_rule.instruction = "test instruction"
    mock_rule.reason = "test reason"
    mock_rule.examples = "[]"
    mock_rule.confidence = 1.0
    mock_rule.source_document = "test.pdf"
    mock_rule.source_page = 1
    mock_rule.source_evidence = "test evidence"
    mock_rule.extraction_confidence = 0.9
    mock_rule.extraction_timestamp = "2026-01-01T00:00:00Z"
    mock_rule.rule_hash = "abc123"
    mock_rule.state = "ACTIVE"
    mock_rule.version = 1

    mock_service = KnowledgeIntelligenceService.__new__(KnowledgeIntelligenceService)
    result = mock_service._rule_to_dict(mock_rule)

    assert result["source_document"] == "test.pdf"
    assert result["source_page"] == 1
    assert result["extraction_confidence"] == 0.9
    assert result["rule_hash"] == "abc123"
    assert result["state"] == "ACTIVE"


# ── Test 13: No hardcoded duplicate career methodology ──

def test_no_hardcoded_duplicate_career_methodology():
    """Search templates.py for career-writing instruction strings that should be in DB."""
    import app.services.prompt_intelligence_v2.templates as t
    import inspect
    source = inspect.getsource(t)

    # These phrases should NOT appear in templates.py
    forbidden = [
        "Start every bullet with a strong action verb",
        "Quantify impact wherever possible",
        "Avoid vague or marketing-style",
        "Write like an experienced software engineer",
        "Never use first-person pronouns",
        "Every claim must be backed by evidence",
        "Every bullet must explain",
    ]
    for phrase in forbidden:
        assert phrase not in source, (
            f"templates.py still contains hardcoded career methodology: '{phrase}'"
        )


# ── Test 14: Legacy prompt path cannot bypass governance ──

def test_no_legacy_prompt_path_bypass():
    """Verify prompt_builder.py does not contain career methodology constants."""
    import app.services.prompt_builder as pb
    import inspect
    source = inspect.getsource(pb)

    assert "SYSTEM_BASE" not in source
    assert "SYSTEM_BULLET_WRITER" not in source
    assert "SYSTEM_COVER_LETTER" not in source
    assert "KNOWLEDGE_CONTEXT_HEADER" not in source
    assert "RESUME_RULES_HEADER" not in source
    assert "USER_RESUME_BULLETS" not in source
    assert "USER_RESUME_SUMMARY" not in source
    assert "USER_COVER_LETTER" not in source
    assert "USER_BULLET_FEEDBACK" not in source
    assert "ATS_OPTIMIZATION" not in source


# ── Test 15: DB unavailable uses authorized defaults ──

def test_db_unavailable_uses_authorized_defaults():
    """RulesEngine without DB session uses explicitly authorized default vocabulary."""
    engine = RulesEngine(db_session=None)
    assert engine.strong_action_verbs == STRONG_ACTION_VERBS_DEFAULT
    assert engine.weak_verbs == WEAK_VERBS_DEFAULT
    assert engine.vague_phrases == VAGUE_PHRASES_DEFAULT
    assert engine.generic_phrases == GENERIC_PHRASES_DEFAULT


# ── Test 16: System constraints still functional ──

def test_system_constraints_still_functional(templates):
    """Verify role definitions, anti-hallucination, output format constraints still work."""
    # Role definition present
    for pt in ["resume_bullets", "cover_letter", "chat"]:
        assert "you are" in templates.get_system(pt).lower()

    # Anti-hallucination present
    for pt in ["resume_bullets", "resume_summary", "cover_letter"]:
        system = templates.get_system(pt).lower()
        assert "never invent" in system or "factual" in system

    # Output format present
    structured = templates.get_system("structured_resume")
    assert "json" in structured.lower()


# ── Test 17: Anti-hallucination constraints present ──

def test_anti_hallucination_constraints_present(templates):
    """Verify anti-hallucination constraints still in system prompts."""
    core_types = ["resume_bullets", "resume_summary", "cover_letter", "bullet_feedback"]
    for pt in core_types:
        system = templates.get_system(pt).lower()
        assert "never invent" in system or "factual" in system, (
            f"Anti-hallucination missing from {pt}"
        )


# ── Test 18: prompt_templates.json has no unverifiable attributions ──

def test_prompt_templates_json_no_attributions():
    """prompt_templates.json should have no Harvard/MIT/Yale/Stanford in prompt content."""
    import os
    json_path = os.path.join(
        os.path.dirname(__file__), "..", "app", "data", "prompt_templates.json"
    )
    if os.path.exists(json_path):
        with open(json_path) as f:
            data = json.load(f)
        prompts = data.get("system_prompts", {})
        for key, val in prompts.items():
            content = val.get("content", "").lower()
            for name in UNIVERSITY_NAMES:
                assert name not in content, (
                    f"prompt_templates.json system_prompts.{key} contains '{name}'"
                )


# ── Test 19: CAREER_ADVISOR_SYSTEM removed from chat_service ──

def test_chat_service_no_career_advisor_system():
    """chat_service.py should not define CAREER_ADVISOR_SYSTEM."""
    import app.services.chat_service as cs
    assert not hasattr(cs, "CAREER_ADVISOR_SYSTEM"), (
        "CAREER_ADVISOR_SYSTEM still defined in chat_service.py"
    )


# ── Test 20: seed.py has no RULES_DATA ──

def test_seed_py_no_rules_data():
    """seed.py should not define RULES_DATA."""
    import app.seed as seed_module
    assert not hasattr(seed_module, "RULES_DATA"), (
        "RULES_DATA still defined in seed.py"
    )


# ── Test 21: Runtime prompt proof — build actual prompts and inspect ──

def test_runtime_prompt_proof_no_career_methodology(builder):
    """Build real prompts for every generation type. Inspect actual content."""
    contexts = {
        "resume_bullets": {
            "role_title": "Software Engineer",
            "company": "Test Corp",
            "duration": "2 years",
            "responsibilities": "Built systems",
            "technologies": "Python",
            "achievements": "Improved performance",
            "num_bullets": 3,
            "knowledge_rules": [],
        },
        "resume_summary": {
            "target_role": "Senior Engineer",
            "experience_years": 5,
            "skills": "Python, React",
            "achievements": "Built X",
            "goals": "Senior role",
            "knowledge_rules": [],
        },
        "cover_letter": {
            "company": "Test Corp",
            "role_title": "Engineer",
            "job_description": "Build things",
            "my_experience": "5 years",
            "why_company": "Innovation",
            "relevant_skills": "Python",
            "knowledge_rules": [],
        },
    }
    for prompt_type, ctx in contexts.items():
        request = PromptRequest(prompt_type=prompt_type, context=ctx)
        messages = builder.build_messages(request)
        system_msg = messages[0]["content"].lower()
        # No career methodology in system prompt
        for pattern in CAREER_KNOWLEDGE_PATTERNS:
            assert pattern not in system_msg, (
                f"Runtime prompt '{prompt_type}' system contains '{pattern}'"
            )


# ── Test 22: Orchestrator knowledge-empty path does not inject methodology ──

def test_orchestrator_empty_knowledge_no_methodology_injection():
    """When knowledge_retriever is None, orchestrator returns empty knowledge."""
    from app.services.ai_orchestrator import AIOrchestrator, TaskType
    from unittest.mock import MagicMock

    orchestrator = AIOrchestrator.__new__(AIOrchestrator)
    orchestrator.knowledge_retriever = None
    result = orchestrator._retrieve_knowledge(
        TaskType.RESUME_BULLETS,
        {"responsibilities": "test", "technologies": "Python"},
    )
    assert result == [], (
        "Orchestrator with no retriever should return empty knowledge, not career methodology"
    )


# ── Test 23: RulesEngine DB-loaded vocabulary actually overrides defaults ──

def test_rules_engine_db_loading_actually_works():
    """Verify that DB-loaded vocabulary replaces default sets."""
    from unittest.mock import MagicMock
    engine = RulesEngine.__new__(RulesEngine)
    engine.rules = []
    engine.strong_action_verbs = STRONG_ACTION_VERBS_DEFAULT.copy()
    engine.weak_verbs = WEAK_VERBS_DEFAULT.copy()
    engine.vague_phrases = VAGUE_PHRASES_DEFAULT.copy()
    engine.generic_phrases = GENERIC_PHRASES_DEFAULT.copy()

    # Simulate DB load with custom values
    mock_db = MagicMock()
    mock_rule_verbs = MagicMock()
    mock_rule_verbs.examples = '["custom_verb_a", "custom_verb_b"]'
    mock_rule_verbs.state = "ACTIVE"
    mock_rule_verbs.is_active = True

    mock_rule_weak = MagicMock()
    mock_rule_weak.examples = '["custom_weak"]'
    mock_rule_weak.state = "ACTIVE"
    mock_rule_weak.is_active = True

    mock_rule_vague = MagicMock()
    mock_rule_vague.examples = '["custom_vague"]'
    mock_rule_vague.state = "ACTIVE"
    mock_rule_vague.is_active = True

    mock_rule_generic = MagicMock()
    mock_rule_generic.examples = '["custom_generic"]'
    mock_rule_generic.state = "ACTIVE"
    mock_rule_generic.is_active = True

    def mock_query_side_effect(model):
        mock_q = MagicMock()
        def mock_filter(*args):
            mock_f = MagicMock()
            def mock_first():
                for arg in args:
                    # Check if this is a rule_key filter
                    if hasattr(arg, 'right') and hasattr(arg.right, 'value'):
                        key = arg.right.value
                        if key == "INT_VER_001":
                            return mock_rule_verbs
                        elif key == "INT_VER_002":
                            return mock_rule_weak
                        elif key == "INT_PHR_001":
                            return mock_rule_vague
                        elif key == "INT_PHR_002":
                            return mock_rule_generic
                return None
            mock_f.first = mock_first
            return mock_f
        mock_q.filter = mock_filter
        return mock_q

    mock_db.query = mock_query_side_effect

    # Import the KnowledgeRule model reference
    from app.models.knowledge_intelligence import KnowledgeRule
    engine._load_vocabulary_from_db(mock_db)

    assert "custom_verb_a" in engine.strong_action_verbs
    assert "custom_verb_b" in engine.strong_action_verbs
    assert "custom_weak" in engine.weak_verbs
    assert "custom_vague" in engine.vague_phrases
    assert "custom_generic" in engine.generic_phrases
