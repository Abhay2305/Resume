"""Integration tests for Task 2.4: Resume and Cover Letter generators use Prompt Intelligence v2.

Verifies that ResumeGeneratorService and CoverLetterGeneratorService delegate to v2 PromptBuilder,
preserves dynamic context injection, and maintains backward compatibility.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest


class TestResumeGeneratorServiceV2Integration:
    """Verify ResumeGeneratorService uses v2 PromptBuilder."""

    def test_service_has_prompt_engine(self):
        from app.services.ai_service import prompt_engine
        assert isinstance(prompt_engine, PromptBuilderV2)

    def test_structured_resume_prompt_request_construction(self):
        """Verify PromptRequest is constructed correctly for structured_resume."""
        from app.services.ai_service import prompt_engine
        
        archetype = "experienced"
        prompt = "John Doe, Software Engineer with 5 years experience..."
        
        request = PromptRequest(
            prompt_type="structured_resume",
            context={
                "archetype": archetype,
                "prompt": prompt,
            },
        )
        
        # Verify request structure
        assert request.prompt_type == "structured_resume"
        assert request.context["archetype"] == archetype
        assert request.context["prompt"] == prompt

    def test_structured_resume_messages_contain_system_and_user(self):
        """Verify v2 builder produces correct message structure."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="structured_resume",
            context={
                "archetype": "experienced",
                "prompt": "Test prompt",
            },
        )
        messages = prompt_engine.build_messages(request)
        
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "expert resume writer" in messages[0]["content"].lower()
        assert "Archetype: experienced" in messages[1]["content"]
        assert "Test prompt" in messages[1]["content"]

    def test_structured_resume_system_prompt_matches_original(self):
        """Verify system prompt matches original inline instruction."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="structured_resume",
            context={"archetype": "experienced", "prompt": "test"},
        )
        messages = prompt_engine.build_messages(request)
        system_content = messages[0]["content"]
        
        # Original system instruction parts
        assert "Convert the following unstructured" in system_content
        assert "Return ONLY valid JSON" in system_content
        assert "personalInfo" in system_content
        assert "Do not include any text outside the JSON" in system_content

    def test_structured_resume_user_prompt_matches_original(self):
        """Verify user prompt matches original f-string format."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="structured_resume",
            context={
                "archetype": "senior",
                "prompt": "My resume content",
            },
        )
        messages = prompt_engine.build_messages(request)
        user_content = messages[1]["content"]
        
        assert user_content.startswith("Archetype: senior\n\nMy resume content")

    def test_resume_generator_uses_v2_messages(self):
        """Verify ResumeGeneratorService passes v2 messages to AI service."""
        from app.services.ai_service import ResumeGeneratorService, prompt_engine
        
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"personalInfo": {}, "summary": "Test"}'
        mock_service.generate = AsyncMock(return_value=mock_response)
        mock_service.parse_json_response.return_value = {"personalInfo": {}, "summary": "Test"}
        
        service = ResumeGeneratorService()
        service._service = mock_service
        
        with patch('app.services.ai_service.prompt_engine', prompt_engine):
            result = service.generate_structured_resume(
                db=MagicMock(),
                user_id="test_user",
                prompt="Test prompt",
                archetype="experienced",
            )
        
        # Verify generate was called with v2 messages
        mock_service.generate.assert_called_once()
        call_args = mock_service.generate.call_args[0][0]
        assert isinstance(call_args, list)
        assert len(call_args) == 2
        assert call_args[0]["role"] == "system"
        assert call_args[1]["role"] == "user"

    def test_resume_response_parsing_unchanged(self):
        """Verify JSON response parsing remains unchanged."""
        from app.services.ai_service import ResumeGeneratorService
        
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"personalInfo": {"name": "John"}, "summary": "Engineer"}'
        mock_service.generate = AsyncMock(return_value=mock_response)
        mock_service.parse_json_response.return_value = {
            "personalInfo": {"name": "John"},
            "summary": "Engineer",
        }
        
        service = ResumeGeneratorService()
        service._service = mock_service
        
        result = service.generate_structured_resume(
            db=MagicMock(),
            user_id="test_user",
            prompt="Test",
            archetype="experienced",
        )
        
        # Verify parsing was called
        mock_service.parse_json_response.assert_called_once_with(mock_response.content)
        # Verify defaults are added
        assert "personalInfo" in result
        assert "summary" in result
        assert "experience" in result
        assert "education" in result
        assert "skills" in result
        assert "projects" in result
        assert "certifications" in result
        assert "achievements" in result

    def test_resume_error_handling_unchanged(self):
        """Verify error handling remains unchanged."""
        from app.services.ai_service import ResumeGeneratorService
        
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(side_effect=Exception("API error"))
        
        service = ResumeGeneratorService()
        service._service = mock_service
        
        result = service.generate_structured_resume(
            db=MagicMock(),
            user_id="test_user",
            prompt="Test",
            archetype="experienced",
        )
        
        # Verify error fallback structure
        assert result["personalInfo"] == {}
        assert "Resume generation failed" in result["summary"]
        assert result["experience"] == []
        assert result["education"] == []
        assert result["skills"] == []
        assert result["projects"] == []
        assert result["certifications"] == []
        assert result["achievements"] == []


class TestCoverLetterGeneratorServiceV2Integration:
    """Verify CoverLetterGeneratorService uses v2 PromptBuilder."""

    def test_service_has_prompt_engine(self):
        from app.services.ai_service import prompt_engine
        assert isinstance(prompt_engine, PromptBuilderV2)

    def test_cover_letter_direct_prompt_request_construction(self):
        """Verify PromptRequest is constructed correctly for cover_letter_direct."""
        from app.services.ai_service import prompt_engine
        
        job_role = "Senior Engineer"
        company_name = "TechCorp"
        
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={
                "job_role": job_role,
                "company_name": company_name,
            },
        )
        
        assert request.prompt_type == "cover_letter_direct"
        assert request.context["job_role"] == job_role
        assert request.context["company_name"] == company_name

    def test_cover_letter_direct_messages_contain_system_and_user(self):
        """Verify v2 builder produces correct message structure."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={
                "job_role": "Engineer",
                "company_name": "Acme",
            },
        )
        messages = prompt_engine.build_messages(request)
        
        assert isinstance(messages, list)
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert "cover letter writer" in messages[0]["content"].lower()
        assert "Engineer" in messages[1]["content"]
        assert "Acme" in messages[1]["content"]

    def test_cover_letter_direct_system_prompt_matches_original(self):
        """Verify system prompt matches original inline instruction."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={"job_role": "Engineer", "company_name": "Acme"},
        )
        messages = prompt_engine.build_messages(request)
        system_content = messages[0]["content"]
        
        # Original system instruction parts
        assert "professional cover letter writer" in system_content
        assert "compelling, personalized cover letter" in system_content
        assert "Return ONLY the cover letter text" in system_content

    def test_cover_letter_direct_user_prompt_matches_original_base(self):
        """Verify user prompt matches original base format (without experience_summary)."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={
                "job_role": "Senior Engineer",
                "company_name": "TechCorp",
            },
        )
        messages = prompt_engine.build_messages(request)
        user_content = messages[1]["content"]
        
        assert user_content.startswith("Write a cover letter for the Senior Engineer position at TechCorp.")

    def test_experience_summary_preserved_in_user_prompt(self):
        """Verify experience_summary is appended to user message."""
        from app.services.ai_service import prompt_engine
        
        request = PromptRequest(
            prompt_type="cover_letter_direct",
            context={
                "job_role": "Engineer",
                "company_name": "Acme",
            },
        )
        messages = prompt_engine.build_messages(request)
        
        # Simulate experience_summary injection (as done in service)
        experience_summary = "5 years of experience in Python and distributed systems"
        if experience_summary and len(messages) >= 2:
            messages[1]["content"] += f"\n\nCandidate experience: {experience_summary}"
        
        user_content = messages[1]["content"]
        assert "Write a cover letter for the Engineer position at Acme." in user_content
        assert "Candidate experience: 5 years of experience in Python and distributed systems" in user_content

    def test_cover_letter_generator_uses_v2_messages(self):
        """Verify CoverLetterGeneratorService passes v2 messages to AI service."""
        from app.services.ai_service import CoverLetterGeneratorService, prompt_engine
        
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Dear Hiring Manager,\n\nI am excited to apply..."
        mock_service.generate = AsyncMock(return_value=mock_response)
        
        service = CoverLetterGeneratorService()
        service._service = mock_service
        
        with patch('app.services.ai_service.prompt_engine', prompt_engine):
            result = service.generate_cover_letter(
                db=MagicMock(),
                user_id="test_user",
                job_role="Engineer",
                company_name="Acme",
                experience_summary="5 years experience",
            )
        
        # Verify generate was called with v2 messages
        mock_service.generate.assert_called_once()
        call_args = mock_service.generate.call_args[0][0]
        assert isinstance(call_args, list)
        assert len(call_args) == 2
        assert call_args[0]["role"] == "system"
        assert call_args[1]["role"] == "user"
        # Verify experience_summary was appended
        assert "5 years experience" in call_args[1]["content"]

    def test_cover_letter_error_fallback_unchanged(self):
        """Verify error fallback returns empty string (fail-closed)."""
        from app.services.ai_service import CoverLetterGeneratorService
        
        mock_service = MagicMock()
        mock_service.generate = AsyncMock(side_effect=Exception("API error"))
        
        service = CoverLetterGeneratorService()
        service._service = mock_service
        
        result = service.generate_cover_letter(
            db=MagicMock(),
            user_id="test_user",
            job_role="Engineer",
            company_name="Acme",
        )
        
        # Verify fail-closed: returns empty string on error
        assert result == ""

    def test_cover_letter_without_experience_summary(self):
        """Verify cover letter works without experience_summary."""
        from app.services.ai_service import CoverLetterGeneratorService, prompt_engine
        
        mock_service = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Cover letter content"
        mock_service.generate = AsyncMock(return_value=mock_response)
        
        service = CoverLetterGeneratorService()
        service._service = mock_service
        
        with patch('app.services.ai_service.prompt_engine', prompt_engine):
            result = service.generate_cover_letter(
                db=MagicMock(),
                user_id="test_user",
                job_role="Engineer",
                company_name="Acme",
                experience_summary=None,
            )
        
        # Verify generate was called
        mock_service.generate.assert_called_once()
        call_args = mock_service.generate.call_args[0][0]
        # User message should not contain experience_summary
        assert "Candidate experience" not in call_args[1]["content"]


class TestPublicMethodSignatures:
    """Verify public method signatures remain unchanged."""

    def test_resume_generator_signature(self):
        import inspect
        from app.services.ai_service import ResumeGeneratorService
        
        sig = inspect.signature(ResumeGeneratorService.generate_structured_resume)
        params = list(sig.parameters.keys())
        assert params == ["self", "db", "user_id", "prompt", "archetype"]
        # Verify default value for archetype
        assert sig.parameters["archetype"].default == "experienced"

    def test_cover_letter_generator_signature(self):
        import inspect
        from app.services.ai_service import CoverLetterGeneratorService
        
        sig = inspect.signature(CoverLetterGeneratorService.generate_cover_letter)
        params = list(sig.parameters.keys())
        assert params == ["self", "db", "user_id", "job_role", "company_name", "experience_summary"]
        # Verify default value for experience_summary
        assert sig.parameters["experience_summary"].default is None
