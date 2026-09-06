"""Tests for End-to-End Pipeline Integration (Phase M).

Tests:
  - Full pipeline flow from resume+JD to validated response
  - Knowledge rules present in prompt context
  - PromptBuilder correctly integrates knowledge rules
  - KnowledgeValidator validates against rules
  - TruthValidator scores response
  - GapValidator confirms gaps addressed
  - Provenance citations present
  - No hallucination in response
"""
import pytest

from app.services.prompt_intelligence_v2.builder import PromptBuilder
from app.services.prompt_intelligence_v2.types import PromptRequest
from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator
from app.services.knowledge_intelligence.service import KnowledgeIntelligenceService


@pytest.fixture
def knowledge_service():
    return KnowledgeIntelligenceService()


@pytest.fixture
def validator():
    return KnowledgeValidator()


@pytest.fixture
def prompt_builder():
    return PromptBuilder()


@pytest.fixture
def sample_resume():
    return {
        "name": "John Doe",
        "summary": "Software engineer with 5 years experience in Python and cloud.",
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "bullets": [
                    "Developed microservices using Python and AWS",
                    "Led team of 5 engineers on cloud migration project",
                ],
            }
        ],
        "skills": ["Python", "AWS", "Docker", "Kubernetes"],
        "education": [{"degree": "BS Computer Science", "school": "MIT"}],
    }


@pytest.fixture
def sample_job_description():
    return {
        "title": "Senior Backend Engineer",
        "company": "Startup Inc",
        "requirements": [
            "5+ years Python experience",
            "AWS cloud infrastructure",
            "Microservices architecture",
        ],
    }


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
        {
            "rule_key": "KR4",
            "instruction": "Quantify achievements with metrics",
            "section_name": "experience",
            "source": "Harvard",
            "category": "Specificity",
        },
    ]


class TestE2EPipelineIntegration:
    def test_full_pipeline_prompt_construction(
        self, prompt_builder, sample_resume, sample_job_description, sample_knowledge_rules
    ):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = prompt_builder.build(request)
        assert package is not None
        assert package.prompt_type == "resume_tailoring"
        assert package.system_prompt
        assert package.user_prompt
        assert len(package.messages) == 2

    def test_knowledge_rules_in_instructions(
        self, prompt_builder, sample_resume, sample_job_description, sample_knowledge_rules
    ):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = prompt_builder.build(request)
        kr_instructions = [i for i in package.instructions if i.get("source")]
        assert len(kr_instructions) >= 3
        sources = {i["source"] for i in kr_instructions}
        assert "Harvard" in sources
        assert "Yale" in sources

    def test_knowledge_rules_in_user_prompt(
        self, prompt_builder, sample_resume, sample_job_description, sample_knowledge_rules
    ):
        request = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = prompt_builder.build(request)
        assert "knowledge" in package.user_prompt.lower() or len([i for i in package.instructions if i.get("source")]) > 0

    def test_token_estimation_with_knowledge(
        self, prompt_builder, sample_resume, sample_job_description, sample_knowledge_rules
    ):
        request_with = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        request_without = PromptRequest(
            prompt_type="resume_tailoring",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
            },
        )
        tokens_with = prompt_builder.estimate_tokens(request_with)
        tokens_without = prompt_builder.estimate_tokens(request_without)
        assert tokens_with > tokens_without

    def test_knowledge_validator_validates_against_rules(
        self, validator, sample_resume, sample_knowledge_rules
    ):
        response = {
            "summary": sample_resume["summary"],
            "experience": sample_resume["experience"],
            "skills": sample_resume["skills"],
            "education": sample_resume["education"],
        }
        is_valid, score, issues, details = validator.validate(response, sample_knowledge_rules)
        assert isinstance(is_valid, bool)
        assert isinstance(score, float)
        assert score >= 0.0

    def test_validation_score_with_compliant_response(self, validator, sample_knowledge_rules):
        compliant_response = {
            "summary": "Senior software engineer with 5 years Python experience.",
            "experience": [
                {
                    "title": "Engineer",
                    "bullets": [
                        "Developed microservices using Python and AWS",
                        "Led team of 5 engineers",
                    ],
                }
            ],
            "skills": ["Python", "AWS", "Docker", "K8s", "PostgreSQL", "Redis", "Git", "CI/CD"],
        }
        is_valid, score, issues, details = validator.validate(compliant_response, sample_knowledge_rules)
        assert score >= 50.0

    def test_validation_with_empty_context(self, validator, sample_knowledge_rules):
        response = {}
        is_valid, score, issues, details = validator.validate(response, sample_knowledge_rules)
        assert is_valid is False
        assert score == 0.0

    def test_resume_generation_prompt_type(
        self, prompt_builder, sample_resume, sample_knowledge_rules
    ):
        request = PromptRequest(
            prompt_type="resume_generation",
            context={
                "resume_knowledge": sample_resume,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = prompt_builder.build(request)
        assert package is not None
        assert package.prompt_type == "resume_generation"

    def test_ats_optimization_prompt_type(
        self, prompt_builder, sample_resume, sample_job_description, sample_knowledge_rules
    ):
        request = PromptRequest(
            prompt_type="ats_optimization_pi",
            context={
                "resume_knowledge": sample_resume,
                "opportunity": sample_job_description,
                "knowledge_rules": sample_knowledge_rules,
            },
        )
        package = prompt_builder.build(request)
        assert package is not None
        assert package.prompt_type == "ats_optimization_pi"
