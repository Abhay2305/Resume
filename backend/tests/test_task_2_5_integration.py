"""Integration tests for Task 2.5: PromptIntelligenceService uses Prompt Intelligence v2.

Verifies that PromptIntelligenceService.build_prompt() delegates to v2 PromptBuilder,
preserves DB persistence, version tracking, audit logging, and backward compatibility.
"""
import pytest
from unittest.mock import MagicMock, patch

from app.services.prompt_intelligence_v2.builder import PromptBuilder as PromptBuilderV2
from app.services.prompt_intelligence_v2.types import PromptRequest, PromptPackage


def _make_service():
    """Create a PromptIntelligenceService with mocked DB and repos."""
    from app.services.prompt_intelligence.service import PromptIntelligenceService
    mock_db = MagicMock()
    service = PromptIntelligenceService(mock_db)
    # Replace real repos/audit/version with mocks
    service.package_repo = MagicMock()
    service.template_repo = MagicMock()
    service.audit_service = MagicMock()
    service.version_service = MagicMock()
    return service


class TestPromptIntelligenceServiceV2Integration:
    """Verify PromptIntelligenceService uses v2 PromptBuilder."""

    def test_service_has_prompt_engine(self):
        service = _make_service()
        assert isinstance(service.prompt_engine, PromptBuilderV2)

    def test_service_no_longer_has_assembler(self):
        service = _make_service()
        assert not hasattr(service, 'assembler')

    def test_build_v2_context_transforms_resume_knowledge(self):
        service = _make_service()

        resume_knowledge = {
            "summary": "Senior Engineer",
            "skills": ["Python", "FastAPI"],
            "technologies": {"backend": ["Python"]},
            "experience_summary": {"total_years": 5},
            "education_summary": {"degree": "BS CS"},
            "certifications": ["AWS"],
            "projects": [{"name": "Project X"}],
            "achievements": ["Reduced latency 40%"],
            "total_experience_years": 5,
        }

        result = service._build_v2_context(
            resume_knowledge=resume_knowledge,
            opportunity_entities=[],
            opportunity_parsed=None,
            gap_data={"overall_match_score": 85},
            knowledge_ctx=None,
        )

        assert result["resume_knowledge"] == resume_knowledge
        assert result["gap_analysis"] == {"overall_match_score": 85}
        assert result["opportunity"] == {
            "entities": {},
            "responsibilities": [],
            "benefits": [],
            "ats_keywords": [],
        }

    def test_build_v2_context_includes_knowledge_context(self):
        service = _make_service()

        knowledge_ctx = {"summary_rules": "[]", "ats_rules": "[]"}

        result = service._build_v2_context(
            resume_knowledge={},
            opportunity_entities=[],
            opportunity_parsed=None,
            gap_data={},
            knowledge_ctx=knowledge_ctx,
        )

        assert result["knowledge_context"] == knowledge_ctx

    def test_build_v2_context_omits_none_knowledge_context(self):
        service = _make_service()

        result = service._build_v2_context(
            resume_knowledge={},
            opportunity_entities=[],
            opportunity_parsed=None,
            gap_data={},
            knowledge_ctx=None,
        )

        assert "knowledge_context" not in result

    def test_build_v2_context_transforms_opportunity_entities(self):
        service = _make_service()

        entities = [
            {"entity_type": "skill", "entity_value": "Python", "is_required": True},
            {"entity_type": "skill", "entity_value": "FastAPI", "is_required": False},
        ]
        parsed = {
            "responsibilities": ["Build APIs"],
            "benefits": ["Remote work"],
            "ats_keywords": ["python", "fastapi"],
        }

        result = service._build_v2_context(
            resume_knowledge={},
            opportunity_entities=entities,
            opportunity_parsed=parsed,
            gap_data={},
            knowledge_ctx=None,
        )

        opp = result["opportunity"]
        assert opp["entities"] == {"skill": ["Python", "FastAPI"]}
        assert opp["responsibilities"] == ["Build APIs"]
        assert opp["benefits"] == ["Remote work"]
        assert opp["ats_keywords"] == ["python", "fastapi"]

    def test_build_resume_context_backward_compat(self):
        service = _make_service()

        resume_knowledge = {
            "summary": "Test",
            "skills": ["Python"],
            "experience_summary": {"years": 5},
            "education_summary": {"degree": "BS"},
        }

        result = service._build_resume_context(resume_knowledge)

        assert result["summary"] == "Test"
        assert result["skills"] == ["Python"]
        assert result["experience"] == {"years": 5}
        assert result["education"] == {"degree": "BS"}

    def test_build_resume_context_empty_when_none(self):
        service = _make_service()

        result = service._build_resume_context(None)
        assert result == {}

    def test_build_prompt_calls_v2_engine(self):
        service = _make_service()

        # Mock DB queries
        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[{"role": "system", "content": "System prompt"}, {"role": "user", "content": "User prompt"}],
                instructions=[],
                constraints=[],
                output_schema=None,
                token_estimate=100,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
                prompt_type="resume_tailoring",
            )

            mock_build.assert_called_once()
            call_args = mock_build.call_args
            assert isinstance(call_args[0][0], PromptRequest)
            assert call_args[0][0].prompt_type == "resume_tailoring"

    def test_build_prompt_persists_to_db(self):
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[],
                instructions=[{"id": "INST_1"}],
                constraints=[{"id": "CONST_1"}],
                output_schema={"type": "object"},
                token_estimate=150,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
            )

            service.package_repo.create.assert_called_once()
            create_args = service.package_repo.create.call_args[0][0]
            assert create_args["user_id"] == "user-123"
            assert create_args["gap_analysis_id"] == "gap-123"
            assert create_args["prompt_type"] == "resume_tailoring"
            assert create_args["system_prompt"] == "System prompt"
            assert create_args["total_tokens_estimate"] == 150
            assert create_args["is_validated"] is True
            assert create_args["instructions"] == [{"id": "INST_1"}]
            assert create_args["constraints"] == [{"id": "CONST_1"}]
            assert create_args["output_schema"] == {"type": "object"}

    def test_build_prompt_returns_correct_shape(self):
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[],
                instructions=[{"id": "INST_1"}],
                constraints=[{"id": "CONST_1"}],
                output_schema={"type": "object"},
                token_estimate=100,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            result = service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
            )

            assert "package" in result
            assert "validation" in result
            assert "tokens_estimate" in result
            assert result["validation"]["is_valid"] is True
            assert result["tokens_estimate"] == 100

    def test_build_prompt_preserves_version_tracking(self):
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        # Mock template exists
        mock_template = MagicMock()
        mock_template.id = "tmpl-123"
        service.template_repo.get_by_id.return_value = mock_template

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[],
                instructions=[],
                constraints=[],
                output_schema=None,
                token_estimate=100,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
                template_id="tmpl-123",
            )

            service.version_service.create_version.assert_called_once()
            version_args = service.version_service.create_version.call_args[1]
            assert version_args["template_id"] == "tmpl-123"
            assert version_args["system_prompt"] == "System prompt"

    def test_build_prompt_preserves_audit_logging(self):
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[],
                instructions=[],
                constraints=[],
                output_schema=None,
                token_estimate=100,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
            )

            service.audit_service.log_create.assert_called_once()
            audit_args = service.audit_service.log_create.call_args[1]
            assert audit_args["user_id"] == "user-123"
            assert audit_args["entity_type"] == "prompt_built"
            assert audit_args["entity_id"] == "pkg-123"
            assert audit_args["details"]["prompt_type"] == "resume_tailoring"
            assert audit_args["details"]["gap_analysis_id"] == "gap-123"

    def test_build_prompt_raises_on_missing_gap_analysis(self):
        service = _make_service()

        service.db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError, match="Gap analysis not found"):
            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="nonexistent",
            )

    def test_build_prompt_uses_v2_token_estimate(self):
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        with patch.object(service, '_get_resume_knowledge', return_value={"summary": "Test"}), \
             patch.object(service, '_get_opportunity_entities', return_value=[]), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=None), \
             patch.object(service, '_build_gap_data', return_value={"overall_match_score": 80}), \
             patch.object(service, '_get_knowledge_context', return_value=None), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System prompt",
                user_prompt="User prompt",
                messages=[],
                instructions=[],
                constraints=[],
                output_schema=None,
                token_estimate=250,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            result = service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
            )

            assert result["tokens_estimate"] == 250

    def test_create_template_still_works(self):
        service = _make_service()

        service.template_repo.get_by_key.return_value = None
        mock_template = MagicMock()
        service.template_repo.create.return_value = mock_template

        result = service.create_template(
            template_key="test_key",
            name="Test Template",
            prompt_type="resume_tailoring",
            category="generation",
            content="Test content",
        )

        service.template_repo.create.assert_called_once()
        assert result == mock_template

    def test_create_template_raises_on_duplicate_key(self):
        service = _make_service()

        service.template_repo.get_by_key.return_value = MagicMock()

        with pytest.raises(ValueError, match="already exists"):
            service.create_template(
                template_key="existing_key",
                name="Test",
                prompt_type="resume_tailoring",
                category="generation",
                content="Test",
            )

    def test_get_templates_still_works(self):
        service = _make_service()

        service.template_repo.get_all.return_value = ([MagicMock()], 1)

        items, total = service.get_templates()

        assert total == 1
        assert len(items) == 1

    def test_get_packages_by_user_still_works(self):
        service = _make_service()

        service.package_repo.get_by_user_id.return_value = ([MagicMock()], 1)

        items, total = service.get_packages_by_user("user-123")

        assert total == 1
        assert len(items) == 1

    def test_v2_engine_replaces_old_assembler(self):
        """Verify v2 engine produces valid PromptPackage for resume_tailoring."""
        engine = PromptBuilderV2()

        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": {
                    "summary": "Senior Engineer",
                    "skills": ["Python", "FastAPI"],
                },
                "opportunity": {
                    "entities": {"skill": ["Python"]},
                    "responsibilities": ["Build APIs"],
                },
                "gap_analysis": {
                    "overall_match_score": 85,
                },
            },
        )

        package = engine.build(request)

        assert isinstance(package, PromptPackage)
        assert package.prompt_type == "resume_tailoring"
        assert len(package.system_prompt) > 0
        assert len(package.messages) == 2
        assert package.messages[0]["role"] == "system"
        assert package.messages[1]["role"] == "user"
        assert package.token_estimate > 0

    def test_build_prompt_preserves_context_fields_for_db(self):
        """Verify DB receives separate context fields, not just combined user prompt."""
        service = _make_service()

        mock_gap = MagicMock()
        mock_gap.id = "gap-123"
        mock_gap.resume_profile_id = "rp-123"
        mock_gap.opportunity_id = "opp-123"
        service.db.query.return_value.filter.return_value.first.return_value = mock_gap

        resume_knowledge = {"summary": "Test", "skills": ["Python"]}
        opportunity_entities = [{"entity_type": "skill", "entity_value": "Python", "is_required": True}]
        opportunity_parsed = {"responsibilities": ["Build APIs"]}
        gap_data = {"overall_match_score": 80}
        knowledge_ctx = {"summary_rules": "[]"}

        with patch.object(service, '_get_resume_knowledge', return_value=resume_knowledge), \
             patch.object(service, '_get_opportunity_entities', return_value=opportunity_entities), \
             patch.object(service, '_get_opportunity_parsed_data', return_value=opportunity_parsed), \
             patch.object(service, '_build_gap_data', return_value=gap_data), \
             patch.object(service, '_get_knowledge_context', return_value=knowledge_ctx), \
             patch.object(service.prompt_engine, 'build') as mock_build:

            mock_build.return_value = PromptPackage(
                prompt_type="resume_tailoring",
                system_prompt="System",
                user_prompt="User",
                messages=[],
                instructions=[],
                constraints=[],
                output_schema=None,
                token_estimate=100,
                template_version="1.0",
            )

            mock_package = MagicMock()
            mock_package.id = "pkg-123"
            service.package_repo.create.return_value = mock_package

            service.build_prompt(
                user_id="user-123",
                gap_analysis_id="gap-123",
            )

            create_args = service.package_repo.create.call_args[0][0]

            # Verify separate context fields are stored
            assert "resume_context" in create_args
            assert "opportunity_context" in create_args
            assert "gap_context" in create_args
            assert "knowledge_context" in create_args

            # Verify resume_context structure (backward compat format)
            assert create_args["resume_context"]["summary"] == "Test"
            assert create_args["resume_context"]["skills"] == ["Python"]

            # Verify opportunity_context structure
            assert "entities" in create_args["opportunity_context"]
            assert create_args["opportunity_context"]["responsibilities"] == ["Build APIs"]

            # Verify gap_context
            assert create_args["gap_context"]["overall_match_score"] == 80

            # Verify knowledge_context
            assert create_args["knowledge_context"]["summary_rules"] == "[]"
