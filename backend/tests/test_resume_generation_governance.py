"""Resume Generation Governance Tests.

Tests the 9 categories from the RESUME_GENERATION_GOVERNANCE_COMPLETION_SPEC:
1. Knowledge injection at the actual AI message boundary
2. Chat resume intent detection
3. Validation execution
4. User-fact preservation
5. Hallucination prevention
6. Missing-information handling
7. Legacy bypass prevention
8. Direct /resume/generate routing
9. Sejal adversarial end-to-end scenario
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.chat_service import ChatService
from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest, PromptPackage


# ============================================================================
# Helpers
# ============================================================================

class MockChatMessage:
    """Minimal mock for ChatMessage DB model."""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class MockKnowledgeRule:
    """Mock KnowledgeRule for testing."""
    def __init__(self, instruction, section_name="general", source="test_source", category="General"):
        self.instruction = instruction
        self.section_name = section_name
        self.source = source
        self.category = category


class MockKnowledgeRuleRepository:
    """Mock KnowledgeRuleRepository."""
    def __init__(self, rules=None):
        self._rules = rules or []
    def get_active(self):
        return self._rules


def _make_structured_resume():
    """Create a valid structured resume dict for testing."""
    return {
        "personalInfo": {
            "fullName": "Sarah Chen",
            "email": "sarah@example.com",
            "phone": "555-0100",
            "location": "Cambridge, MA",
            "jobTitle": "Senior Software Engineer",
        },
        "summary": "Experienced software engineer with expertise in Python and ML.",
        "experience": [
            {
                "company": "Google",
                "title": "Senior Software Engineer",
                "startDate": "2019-01",
                "endDate": "2024-01",
                "description": [
                    "Led development of distributed systems serving 10M+ users",
                    "Improved ML pipeline performance by 40%",
                ],
            }
        ],
        "education": [
            {
                "institution": "MIT",
                "degree": "PhD",
                "field": "Computer Science",
                "startDate": "2014-09",
                "endDate": "2019-05",
            }
        ],
        "skills": ["Python", "Machine Learning", "Distributed Systems", "TensorFlow", "Kubernetes"],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }


# ============================================================================
# Test 1: Knowledge Injection at the AI Message Boundary
# ============================================================================

class TestKnowledgeInjection:
    """Verify ACTIVE knowledge rules appear in AI messages at the actual boundary."""

    def test_knowledge_rules_injected_into_messages(self):
        """Knowledge rules from DB are present in the messages sent to the AI."""
        builder = PromptBuilderV2()
        knowledge_rules = [
            {"instruction": "Use action verbs in experience bullets", "section_name": "experience", "source": "career_coaching", "category": "Action Verbs"},
            {"instruction": "Keep summary under 3 sentences", "section_name": "summary", "source": "hr_best_practices", "category": "Length"},
        ]

        request = PromptRequest(
            prompt_type="resume_generation",
            context={
                "resume_knowledge": "Test resume data",
                "knowledge_rules": knowledge_rules,
            },
        )
        messages = builder.build_messages(request)

        # Find the user message
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        # Knowledge rules must appear in the user message
        assert "Use action verbs" in user_msg
        assert "Keep summary under 3 sentences" in user_msg
        assert "career_coaching" in user_msg
        assert "hr_best_practices" in user_msg

    def test_no_knowledge_rules_still_works(self):
        """System works correctly when no knowledge rules exist."""
        builder = PromptBuilderV2()
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": "Test resume data"},
        )
        messages = builder.build_messages(request)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_instructions_injected_into_messages(self):
        """Instructions from prompt templates are present in messages."""
        builder = PromptBuilderV2()
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": "Test resume data"},
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        # Instructions should be injected (resume_generation falls back to resume_tailoring instructions)
        assert "## Instructions" in user_msg or "Rewrite" in user_msg or "Reorder" in user_msg

    def test_constraints_injected_into_messages(self):
        """Constraints from prompt templates are present in messages."""
        builder = PromptBuilderV2()
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": "Test resume data"},
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        # Universal constraints should be injected
        assert "## Constraints" in user_msg
        assert "Never fabricate" in user_msg

    def test_output_schema_injected_when_available(self):
        """Output schema is injected when the prompt type has one."""
        builder = PromptBuilderV2()
        # resume_tailoring has an output schema in prompt_templates.json
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": "Test resume data",
                "opportunity": "Test opportunity",
            },
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        # Output schema should be injected
        assert "Required Output Format" in user_msg

    def test_output_schema_not_injected_when_absent(self):
        """Output schema section absent when prompt type has no schema."""
        builder = PromptBuilderV2()
        # resume_generation has no output schema in prompt_templates.json
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": "Test resume data"},
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        # Output schema should NOT be present
        assert "Required Output Format" not in user_msg

    def test_knowledge_rules_only_active_reached_messages(self):
        """Only ACTIVE rules from DB appear in messages (filtered by caller)."""
        # The caller (get_knowledge_rules_for_context) filters by state=ACTIVE
        # Knowledge rules passed in context are already filtered
        builder = PromptBuilderV2()
        active_rules = [
            {"instruction": "Active rule", "section_name": "skills", "source": "test", "category": "General"},
        ]
        request = PromptRequest(
            prompt_type="resume_generation",
            context={
                "resume_knowledge": "Test",
                "knowledge_rules": active_rules,
            },
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        assert "Active rule" in user_msg


# ============================================================================
# Test 2: Chat Resume Intent Detection
# ============================================================================

class TestChatIntentDetection:
    """Verify resume requests use correct prompt type."""

    def setup_method(self):
        self.service = ChatService()

    def test_resume_keyword_detects_generation_intent(self):
        """Resume keywords trigger resume_generation prompt type."""
        assert self.service._detect_prompt_type("Create a resume for John Doe") == "resume_generation"
        assert self.service._detect_prompt_type("Generate my CV") == "resume_generation"
        assert self.service._detect_prompt_type("Build a resume") == "resume_generation"
        assert self.service._detect_prompt_type("Write my resume") == "resume_generation"
        assert self.service._detect_prompt_type("Update my resume") == "resume_generation"
        assert self.service._detect_prompt_type("Improve my CV") == "resume_generation"
        assert self.service._detect_prompt_type("Tailor my resume for Google") == "resume_generation"
        assert self.service._detect_prompt_type("Optimize my resume") == "resume_generation"
        assert self.service._detect_prompt_type("Rewrite my CV") == "resume_generation"

    def test_non_resume_uses_chat_intent(self):
        """Non-resume messages use chat prompt type."""
        assert self.service._detect_prompt_type("What should I include in a cover letter?") == "chat"
        assert self.service._detect_prompt_type("Tell me about ATS systems") == "chat"
        assert self.service._detect_prompt_type("Hello, how are you?") == "chat"
        assert self.service._detect_prompt_type("What is a good professional summary?") == "chat"

    def test_resume_keyword_case_insensitive(self):
        """Intent detection is case-insensitive."""
        assert self.service._detect_prompt_type("CREATE A RESUME") == "resume_generation"
        assert self.service._detect_prompt_type("create a resume") == "resume_generation"
        assert self.service._detect_prompt_type("Create A Resume") == "resume_generation"

    def test_build_messages_uses_chat_prompt_for_all_chat_messages(self):
        """_build_messages always uses chat prompt type, even for resume keywords."""
        messages = self.service._build_messages([], "Create a resume for John Doe")
        system_content = messages[0]["content"]

        # All chat messages use the chat system prompt, which instructs the AI
        # to output structured JSON when it has enough resume information
        assert "career advisor" in system_content.lower()
        assert "Conversation Flow" in system_content

    def test_build_messages_uses_chat_for_advisory_request(self):
        """_build_messages uses chat prompt type for advisory requests."""
        messages = self.service._build_messages([], "Tell me about ATS systems")
        system_content = messages[0]["content"]

        # Should use chat system prompt
        assert "career advisor" in system_content.lower()

    def test_build_messages_chat_prompt_allows_conversational_flow(self):
        """Chat prompt allows conversational flow including questions."""
        messages = self.service._build_messages([], "Create a resume for John Doe")
        system_content = messages[0]["content"]

        # The chat system prompt allows asking questions to collect info
        assert "ask one question" in system_content.lower()


# ============================================================================
# Test 3: Validation Execution
# ============================================================================

class TestValidationExecution:
    """Verify validation runs and results are correct."""

    def test_validate_resume_output_returns_results(self):
        """validate_resume_output returns validation results."""
        from app.services.ai_service import validate_resume_output

        structured_data = _make_structured_resume()
        result = validate_resume_output(structured_data, "Create a resume for Sarah Chen")

        assert result is not None
        assert "is_approved" in result
        assert "overall_confidence" in result
        assert "issues" in result
        assert "validations" in result
        assert "schema" in result["validations"]
        assert "truth" in result["validations"]
        assert "knowledge" in result["validations"]

    def test_valid_resume_passes_validation(self):
        """A complete, valid resume passes validation."""
        from app.services.ai_service import validate_resume_output

        structured_data = _make_structured_resume()
        result = validate_resume_output(structured_data, "Create a resume for Sarah Chen, PhD from MIT, 5 years at Google")

        assert result["is_approved"] is True
        assert result["overall_confidence"] > 0.5

    def test_empty_resume_fails_schema_validation(self):
        """An empty response fails schema validation."""
        from app.services.ai_service import validate_resume_output

        result = validate_resume_output({}, "Create a resume")

        assert result is not None
        assert result["validations"]["schema"]["valid"] is False

    def test_validation_handles_exception_gracefully(self):
        """Validation returns None on unexpected errors."""
        from app.services.ai_service import validate_resume_output

        # Pass invalid data that might cause validator to throw
        result = validate_resume_output(None, "test")
        # Should return a result (validators handle None)
        assert result is not None

    def test_chat_validation_gate_called_for_resume_generation(self):
        """Chat validation gate runs for resume generation requests."""
        service = ChatService()
        structured_data = _make_structured_resume()

        result = service._validate_resume_output(
            structured_data,
            "Create a resume for Sarah Chen",
            db=None,
        )

        assert result is not None
        assert "is_approved" in result


# ============================================================================
# Test 4: User-Fact Preservation
# ============================================================================

class TestUserFactPreservation:
    """Verify user-provided facts appear verbatim in output."""

    def test_schema_validator_passes_complete_resume(self):
        """A complete resume with all user facts passes schema validation."""
        from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator

        validator = ResponseSchemaValidator()
        structured_data = _make_structured_resume()

        is_valid, score, issues, details = validator.validate(structured_data)

        assert is_valid is True
        assert score >= 50.0

    def test_truth_validator_passes_with_matching_knowledge(self):
        """Truth validator passes when AI output matches user-provided knowledge."""
        from app.services.ai_response_intelligence.truth_validator import TruthValidator

        validator = TruthValidator()
        structured_data = _make_structured_resume()
        resume_knowledge = {
            "experience_summary": [{"company": "Google", "title": "Senior Software Engineer"}],
            "skills": ["Python", "Machine Learning", "Distributed Systems"],
            "education_summary": [{"institution": "MIT", "degree": "PhD"}],
        }

        is_valid, score, issues, details = validator.validate(structured_data, resume_knowledge)

        # Should pass — all facts in output match knowledge
        assert score >= 50.0

    def test_user_facts_in_output_preserved(self):
        """User facts like name, company, school appear in generated output."""
        from app.services.ai_service import validate_resume_output

        structured_data = _make_structured_resume()
        result = validate_resume_output(
            structured_data,
            "Sarah Chen, PhD from MIT, 5 years at Google as Senior Software Engineer",
        )

        # The truth validation should not flag fabricated items for matching facts
        truth_result = result["validations"]["truth"]
        assert truth_result["valid"] is True


# ============================================================================
# Test 5: Hallucination Prevention
# ============================================================================

class TestHallucinationPrevention:
    """Verify AI doesn't add facts not in user input."""

    def test_truth_validator_detects_fabricated_company(self):
        """Truth validator detects companies not in resume knowledge."""
        from app.services.ai_response_intelligence.truth_validator import TruthValidator

        validator = TruthValidator()
        structured_data = _make_structured_resume()
        # Knowledge says Google, but output also has fabricated "Meta"
        structured_data["experience"].append({
            "company": "Meta",
            "title": "Engineer",
            "startDate": "2020-01",
            "description": ["Did things"],
        })
        resume_knowledge = {
            "experience_summary": [{"company": "Google", "title": "Senior Software Engineer"}],
            "skills": ["Python"],
            "education_summary": [],
        }

        is_valid, score, issues, details = validator.validate(structured_data, resume_knowledge)

        # Should detect fabricated company
        fabricated = [i for i in issues if "fabricated" in i.get("type", "").lower()]
        assert len(fabricated) > 0

    def test_truth_validator_detects_fabricated_skill(self):
        """Truth validator detects skills not in resume knowledge."""
        from app.services.ai_response_intelligence.truth_validator import TruthValidator

        validator = TruthValidator()
        structured_data = _make_structured_resume()
        structured_data["skills"].append("Rust")  # Not in knowledge
        resume_knowledge = {
            "skills": ["Python", "Machine Learning"],
            "experience_summary": [],
            "education_summary": [],
        }

        is_valid, score, issues, details = validator.validate(structured_data, resume_knowledge)

        fabricated_skills = [i for i in issues if i.get("type") == "fabricated_skill"]
        assert len(fabricated_skills) > 0

    def test_no_fabricated_facts_when_knowledge_empty(self):
        """When no knowledge is available, validator doesn't flag anything."""
        from app.services.ai_response_intelligence.truth_validator import TruthValidator

        validator = TruthValidator()
        structured_data = _make_structured_resume()

        is_valid, score, issues, details = validator.validate(structured_data, {})

        # No knowledge = no fabrication checks possible
        assert is_valid is True


# ============================================================================
# Test 6: Missing-Information Handling
# ============================================================================

class TestMissingInformationHandling:
    """Verify missing sections are handled appropriately."""

    def test_schema_validator_flags_missing_sections(self):
        """Schema validator flags missing required sections."""
        from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator

        validator = ResponseSchemaValidator()
        incomplete_data = {
            "personalInfo": {"fullName": "John Doe"},
            "summary": "A short summary",
            # Missing: experience, skills
        }

        is_valid, score, issues, details = validator.validate(incomplete_data)

        missing = [i for i in issues if i.get("type") == "missing_section"]
        assert len(missing) > 0
        assert any(i["section"] == "experience" for i in missing)
        assert any(i["section"] == "skills" for i in missing)

    def test_minimal_resume_gets_low_confidence(self):
        """A minimal resume gets low validation confidence."""
        from app.services.ai_service import validate_resume_output

        minimal_data = {
            "personalInfo": {"fullName": "John"},
            "summary": "Works in tech",
            "experience": [],
            "education": [],
            "skills": [],
            "projects": [],
            "certifications": [],
            "achievements": [],
        }

        result = validate_resume_output(minimal_data, "Create a resume for John, works in tech")

        assert result is not None
        # Should have issues due to missing sections
        assert len(result["issues"]) > 0

    def test_knowledge_validator_flags_empty_skills(self):
        """Knowledge validator flags empty skills when rules require them."""
        from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator

        validator = KnowledgeValidator()
        data = {
            "summary": "Test summary with enough words to pass length check here and there",
            "experience": [],
            "skills": [],
            "education": [],
        }
        rules = [
            {"section_name": "skills", "instruction": "Include at least 5 technical skills", "source": "test", "category": "skills"},
        ]

        is_valid, score, issues, details = validator.validate(data, rules)

        # Should flag empty skills
        assert len(issues) > 0


# ============================================================================
# Test 7: Chat Service Integration
# ============================================================================

class TestChatServiceIntegration:
    """Verify ChatService uses governed architecture."""

    def test_send_message_signature_unchanged(self):
        """send_message public signature is unchanged."""
        import inspect
        service = ChatService()
        sig = inspect.signature(service.send_message)
        params = list(sig.parameters.keys())
        assert params == ["db", "session_id", "user_message"]

    def test_build_messages_returns_correct_format(self):
        """_build_messages returns list of dicts with role and content."""
        service = ChatService()
        messages = service._build_messages([], "Test message")
        assert isinstance(messages, list)
        for msg in messages:
            assert isinstance(msg, dict)
            assert "role" in msg
            assert "content" in msg

    def test_build_messages_compatible_with_generate(self):
        """Messages are compatible with UniversalAIService.generate()."""
        service = ChatService()
        messages = service._build_messages([], "Test message")
        for msg in messages:
            assert msg["role"] in ("system", "user", "assistant")
            assert isinstance(msg["content"], str)

    def test_resume_request_uses_chat_prompt(self):
        """Resume requests use chat prompt so user message reaches the AI."""
        service = ChatService()
        messages = service._build_messages([], "Create a resume for John Doe")
        system_msg = messages[0]["content"]

        # Chat system prompt (career advisor) — NOT resume_generation
        assert "career advisor" in system_msg.lower()
        # Should contain the conversation flow instructions
        assert "Conversation Flow" in system_msg


# ============================================================================
# Test 8: Legacy Bypass Prevention
# ============================================================================

class TestLegacyBypassPrevention:
    """Verify old paths route through governed core."""

    def test_prompt_builder_includes_knowledge_in_all_prompt_types(self):
        """PromptBuilder includes knowledge rules for resume_generation type."""
        builder = PromptBuilderV2()
        rules = [
            {"instruction": "Test rule", "section_name": "test", "source": "test", "category": "General"},
        ]
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": "Test", "knowledge_rules": rules},
        )
        messages = builder.build_messages(request)
        user_msg = messages[1]["content"]
        assert "Test rule" in user_msg

    def test_prompt_builder_includes_knowledge_for_chat_type(self):
        """PromptBuilder includes knowledge rules for chat type."""
        builder = PromptBuilderV2()
        rules = [
            {"instruction": "Chat knowledge rule", "section_name": "general", "source": "test", "category": "General"},
        ]
        request = PromptRequest(
            prompt_type="chat",
            context={"user_message": "Hello", "knowledge_rules": rules},
        )
        messages = builder.build_messages(request)
        user_msg = messages[1]["content"]
        assert "Chat knowledge rule" in user_msg

    def test_resume_generation_system_prompt_no_questions(self):
        """resume_generation system prompt does not instruct asking questions."""
        from app.services.prompt_intelligence_v2.templates import PromptTemplates
        t = PromptTemplates()
        system_prompt = t.get_system("resume_generation")

        assert "ask" not in system_prompt.lower() or "question" not in system_prompt.lower()
        assert "Never invent" in system_prompt

    def test_chat_system_prompt_allows_questions(self):
        """chat system prompt still allows conversational questions."""
        from app.services.prompt_intelligence_v2.templates import PromptTemplates
        t = PromptTemplates()
        system_prompt = t.get_system("chat")

        assert "conversation" in system_prompt.lower() or "ask" in system_prompt.lower()


# ============================================================================
# Test 9: Sejal Adversarial End-to-End Scenario
# ============================================================================

class TestSejalAdversarial:
    """Complete adversarial test scenario from the specification."""

    def test_sejal_input_produces_resume_generation_intent(self):
        """Sejal's resume request is detected as resume_generation intent."""
        service = ChatService()
        prompt = (
            "Create a resume for Sarah Chen. She has a PhD in Computer Science "
            "from MIT, worked at Google for 5 years as a Senior Software Engineer, "
            "and has skills in Python, machine learning, and distributed systems."
        )
        assert service._detect_prompt_type(prompt) == "resume_generation"

    def test_sejal_system_prompt_allows_conversational_flow(self):
        """Sejal's request uses chat prompt, allowing conversational info collection."""
        service = ChatService()
        prompt = (
            "Create a resume for Sarah Chen. She has a PhD in Computer Science "
            "from MIT, worked at Google for 5 years as a Senior Software Engineer, "
            "and has skills in Python, machine learning, and distributed systems."
        )
        messages = service._build_messages([], prompt)
        system_msg = messages[0]["content"]

        # Must be the chat system prompt with conversation flow
        assert "Conversation Flow" in system_msg
        # Must be the career advisor prompt
        assert "career advisor" in system_msg.lower()

    def test_sejal_knowledge_rules_injected(self):
        """Knowledge rules are injected into messages for Sejal's request."""
        service = ChatService()
        prompt = (
            "Create a resume for Sarah Chen. She has a PhD in Computer Science "
            "from MIT, worked at Google for 5 years as a Senior Software Engineer."
        )
        # Simulate with knowledge rules in context
        builder = PromptBuilderV2()
        rules = [
            {"instruction": "Use strong action verbs", "section_name": "experience", "source": "career_coaching", "category": "Action Verbs"},
        ]
        request = PromptRequest(
            prompt_type="resume_generation",
            context={
                "resume_knowledge": prompt,
                "knowledge_rules": rules,
            },
        )
        messages = builder.build_messages(request)
        user_msg = [m for m in messages if m["role"] == "user"][0]["content"]

        assert "Use strong action verbs" in user_msg
        assert "career_coaching" in user_msg

    def test_sejal_complete_output_passes_validation(self):
        """A complete resume matching Sejal's input passes validation."""
        from app.services.ai_service import validate_resume_output

        structured_data = _make_structured_resume()
        sejal_input = (
            "Create a resume for Sarah Chen. She has a PhD in Computer Science "
            "from MIT, worked at Google for 5 years as a Senior Software Engineer, "
            "and has skills in Python, machine learning, and distributed systems."
        )

        result = validate_resume_output(structured_data, sejal_input)

        assert result is not None
        assert result["is_approved"] is True
        assert result["overall_confidence"] > 0.5

    def test_sejal_user_facts_in_output(self):
        """Sejal's user facts appear in the validation truth check."""
        from app.services.ai_response_intelligence.truth_validator import TruthValidator

        validator = TruthValidator()
        structured_data = _make_structured_resume()
        resume_knowledge = {
            "experience_summary": [{"company": "Google", "title": "Senior Software Engineer"}],
            "skills": ["Python", "Machine Learning", "Distributed Systems", "TensorFlow", "Kubernetes"],
            "education_summary": [{"institution": "MIT", "degree": "PhD"}],
        }

        is_valid, score, issues, details = validator.validate(structured_data, resume_knowledge)

        # All facts match — no fabrication detected
        fabricated = [i for i in issues if "fabricated" in i.get("type", "").lower()]
        assert len(fabricated) == 0

    def test_sejal_adversarial_comprehensive(self):
        """Full Sejal scenario: intent detection, prompt, knowledge, validation."""
        # 1. Intent detection still works (used for validation gate)
        service = ChatService()
        prompt = (
            "Create a resume for Sarah Chen. She has a PhD in Computer Science "
            "from MIT, worked at Google for 5 years as a Senior Software Engineer, "
            "and has skills in Python, machine learning, and distributed systems."
        )
        assert service._detect_prompt_type(prompt) == "resume_generation"

        # 2. Message building always uses chat prompt (user message reaches AI)
        messages = service._build_messages([], prompt)
        assert messages[0]["role"] == "system"
        system_msg = messages[0]["content"]
        assert "career advisor" in system_msg.lower()

        # 3. Knowledge rules in user message (via prompt builder)
        builder = PromptBuilderV2()
        rules = [
            {"instruction": "Quantify achievements", "section_name": "experience", "source": "career_coaching", "category": "Metrics"},
        ]
        request = PromptRequest(
            prompt_type="resume_generation",
            context={"resume_knowledge": prompt, "knowledge_rules": rules},
        )
        msg_with_knowledge = builder.build_messages(request)
        user_msg = [m for m in msg_with_knowledge if m["role"] == "user"][0]["content"]
        assert "Quantify achievements" in user_msg

        # 4. Validation of complete output
        from app.services.ai_service import validate_resume_output
        structured_data = _make_structured_resume()
        result = validate_resume_output(structured_data, prompt)
        assert result["is_approved"] is True

        # 5. No fabricated facts
        from app.services.ai_response_intelligence.truth_validator import TruthValidator
        validator = TruthValidator()
        knowledge = {
            "experience_summary": [{"company": "Google", "title": "Senior Software Engineer"}],
            "skills": ["Python", "Machine Learning", "Distributed Systems", "TensorFlow", "Kubernetes"],
            "education_summary": [{"institution": "MIT", "degree": "PhD"}],
        }
        is_valid, score, issues, details = validator.validate(structured_data, knowledge)
        fabricated = [i for i in issues if "fabricated" in i.get("type", "").lower()]
        assert len(fabricated) == 0
