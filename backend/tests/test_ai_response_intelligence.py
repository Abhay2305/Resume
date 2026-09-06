"""Tests for the AI Response Intelligence Engine.

Tests schema validation, truth validation, knowledge validation,
gap validation, diff generation, change classification,
confidence scoring, and approval package building.
"""
import json
import pytest
from unittest.mock import MagicMock

from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator
from app.services.ai_response_intelligence.truth_validator import TruthValidator
from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator
from app.services.ai_response_intelligence.gap_validator import GapValidator
from app.services.ai_response_intelligence.diff_engine import DiffEngine
from app.services.ai_response_intelligence.change_classifier import ChangeClassifier
from app.services.ai_response_intelligence.confidence_engine import ConfidenceEngine
from app.services.ai_response_intelligence.approval_builder import ApprovalPackageBuilder


# ============================================================
# ResponseSchemaValidator Tests
# ============================================================

class TestResponseSchemaValidator:
    def setup_method(self):
        self.validator = ResponseSchemaValidator()

    def test_valid_response(self):
        response = {
            "summary": "Senior developer with 5+ years of experience.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "startDate": "2020-01",
                    "description": ["Built scalable systems"],
                }
            ],
            "skills": ["Python", "FastAPI", "Docker"],
        }
        is_valid, score, issues, details = self.validator.validate(response)
        assert is_valid is True
        assert score >= 80
        assert len(issues) == 0

    def test_missing_required_sections(self):
        response = {"summary": "Test summary"}
        is_valid, score, issues, details = self.validator.validate(response)
        assert is_valid is False
        assert any(i["type"] == "missing_section" for i in issues)

    def test_empty_response(self):
        is_valid, score, issues, details = self.validator.validate({})
        assert is_valid is False
        assert score == 0.0

    def test_none_response(self):
        is_valid, score, issues, details = self.validator.validate(None)
        assert is_valid is False

    def test_invalid_summary_type(self):
        response = {
            "summary": 123,
            "experience": [],
            "skills": ["Python"],
        }
        is_valid, score, issues, details = self.validator.validate(response)
        assert any(i["type"] == "invalid_type" for i in issues)

    def test_empty_skills(self):
        response = {
            "summary": "Test summary here",
            "experience": [],
            "skills": [],
        }
        is_valid, score, issues, details = self.validator.validate(response)
        assert any(i["type"] == "empty_section" for i in issues)

    def test_experience_missing_fields(self):
        response = {
            "summary": "Test summary",
            "experience": [{"title": "Engineer"}],
            "skills": ["Python"],
        }
        is_valid, score, issues, details = self.validator.validate(response)
        assert any(i["type"] == "missing_field" for i in issues)

    def test_custom_output_schema(self):
        response = {
            "summary": "Test",
            "experience": [],
            "skills": [],
        }
        schema = {
            "required": ["summary", "experience"],
            "properties": {
                "summary": {"type": "string"},
                "experience": {"type": "array"},
            }
        }
        is_valid, score, issues, details = self.validator.validate(response, schema)
        assert is_valid is True


# ============================================================
# TruthValidator Tests
# ============================================================

class TestTruthValidator:
    def setup_method(self):
        self.validator = TruthValidator()

    def test_truthful_response(self):
        response = {
            "summary": "Developer at Tech Corp",
            "experience": [
                {"title": "Engineer", "company": "Tech Corp", "startDate": "2020"}
            ],
            "skills": ["Python", "FastAPI"],
        }
        knowledge = {
            "skills": ["Python", "FastAPI", "Docker"],
            "experience_summary": [
                {"title": "Engineer", "company": "Tech Corp"}
            ],
            "education_summary": [],
            "certifications": [],
        }
        is_valid, score, issues, details = self.validator.validate(response, knowledge)
        assert is_valid is True
        assert score >= 80

    def test_fabricated_company(self):
        response = {
            "summary": "Developer",
            "experience": [
                {"title": "Engineer", "company": "Fake Corp", "startDate": "2020"}
            ],
            "skills": ["Python"],
        }
        knowledge = {
            "skills": ["Python"],
            "experience_summary": [
                {"title": "Engineer", "company": "Real Corp"}
            ],
            "education_summary": [],
            "certifications": [],
        }
        is_valid, score, issues, details = self.validator.validate(response, knowledge)
        assert any(i["type"] == "fabricated_company" for i in issues)

    def test_fabricated_skill(self):
        response = {
            "summary": "Developer",
            "experience": [],
            "skills": ["Python", "FakeSkill"],
        }
        knowledge = {
            "skills": ["Python"],
            "experience_summary": [],
            "education_summary": [],
            "certifications": [],
        }
        is_valid, score, issues, details = self.validator.validate(response, knowledge)
        assert any(i["type"] == "fabricated_skill" for i in issues)

    def test_no_knowledge(self):
        response = {"summary": "Test", "experience": [], "skills": ["Python"]}
        is_valid, score, issues, details = self.validator.validate(response, {})
        assert is_valid is True

    def test_empty_response(self):
        is_valid, score, issues, details = self.validator.validate({}, {"skills": ["Python"]})
        assert is_valid is False

    def test_removed_experience(self):
        response = {
            "summary": "Developer",
            "experience": [],
            "skills": ["Python"],
        }
        knowledge = {
            "skills": ["Python"],
            "experience_summary": [
                {"title": "Engineer", "company": "Tech Corp"}
            ],
            "education_summary": [],
            "certifications": [],
        }
        is_valid, score, issues, details = self.validator.validate(response, knowledge)
        assert any(i["type"] == "removed_experience" for i in issues)

    def test_inflated_metric(self):
        response = {
            "summary": "Developer",
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Tech Corp",
                    "startDate": "2020",
                    "description": ["Improved performance by 150%"],
                }
            ],
            "skills": ["Python"],
        }
        knowledge = {
            "skills": ["Python"],
            "experience_summary": [{"title": "Engineer", "company": "Tech Corp"}],
            "education_summary": [],
            "certifications": [],
        }
        is_valid, score, issues, details = self.validator.validate(response, knowledge)
        assert any(i["type"] == "inflated_metric" for i in issues)


# ============================================================
# KnowledgeValidator Tests
# ============================================================

class TestKnowledgeValidator:
    def setup_method(self):
        self.validator = KnowledgeValidator()

    def test_valid_response(self):
        response = {
            "summary": "Developer with 5+ years experience",
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Tech",
                    "startDate": "2020",
                    "description": ["Built systems serving 1M users"],
                }
            ],
            "skills": ["Python"],
        }
        rules = [
            {
                "rule_key": "HARVARD_EXP_001",
                "source": "Harvard",
                "section_name": "experience",
                "category": "experience",
                "instruction": "Use strong action verbs",
                "reason": "Impact",
                "priority": "high",
                "is_active": True,
            }
        ]
        is_valid, score, issues, details = self.validator.validate(response, rules)
        assert is_valid is True

    def test_no_rules(self):
        response = {"summary": "Test", "experience": [], "skills": []}
        is_valid, score, issues, details = self.validator.validate(response, [])
        assert is_valid is True

    def test_rule_violation(self):
        response = {
            "summary": "I am a developer",
            "experience": [],
            "skills": [],
        }
        rules = [
            {
                "rule_key": "HARVARD_SUM_001",
                "source": "Harvard",
                "section_name": "summary",
                "category": "summary",
                "instruction": "No first person - avoid using I",
                "reason": "Professional tone",
                "priority": "high",
                "is_active": True,
            }
        ]
        is_valid, score, issues, details = self.validator.validate(response, rules)
        assert any(i["type"] == "rule_violation" for i in issues)

    def test_weak_verbs(self):
        response = {
            "summary": "Developer",
            "experience": [
                {
                    "title": "Engineer",
                    "company": "Tech",
                    "startDate": "2020",
                    "description": ["Responsible for managing the team"],
                }
            ],
            "skills": [],
        }
        rules = [
            {
                "rule_key": "HARVARD_EXP_001",
                "source": "Harvard",
                "section_name": "experience",
                "category": "experience",
                "instruction": "Use strong action verbs",
                "reason": "Impact",
                "priority": "high",
                "is_active": True,
            }
        ]
        is_valid, score, issues, details = self.validator.validate(response, rules)
        assert any(i["type"] == "rule_violation" for i in issues)


# ============================================================
# GapValidator Tests
# ============================================================

class TestGapValidator:
    def setup_method(self):
        self.validator = GapValidator()

    def test_gaps_addressed(self):
        response = {
            "summary": "Developer",
            "experience": [],
            "skills": ["Python", "Docker", "Kubernetes"],
        }
        gap_analysis = {"overall_match_score": 0.6}
        gap_results = [
            {
                "category": "skills",
                "missing_items": "Docker,Kubernetes",
                "matched_items": "Python",
            }
        ]
        is_valid, score, issues, details = self.validator.validate(
            response, gap_analysis, gap_results
        )
        assert is_valid is True
        assert details["gaps_addressed"] >= 1

    def test_gap_not_addressed(self):
        response = {
            "summary": "Developer",
            "experience": [],
            "skills": ["Python"],
        }
        gap_analysis = {"overall_match_score": 0.5}
        gap_results = [
            {
                "category": "skills",
                "missing_items": "Docker,Kubernetes",
                "matched_items": "Python",
            }
        ]
        is_valid, score, issues, details = self.validator.validate(
            response, gap_analysis, gap_results
        )
        assert any(i["type"] == "gap_not_addressed" for i in issues)

    def test_no_gap_analysis(self):
        response = {"summary": "Test", "experience": [], "skills": []}
        is_valid, score, issues, details = self.validator.validate(response, {}, [])
        assert is_valid is True

    def test_unnecessary_modification(self):
        response = {
            "summary": "Developer",
            "experience": [],
            "skills": ["Python"],
            "education": [{"degree": "BS"}],
        }
        gap_analysis = {"overall_match_score": 0.5}
        gap_results = [
            {"category": "skills", "missing_items": "Docker", "matched_items": "Python"}
        ]
        is_valid, score, issues, details = self.validator.validate(
            response, gap_analysis, gap_results
        )
        assert any(i["type"] == "unnecessary_modification" for i in issues)


# ============================================================
# DiffEngine Tests
# ============================================================

class TestDiffEngine:
    def setup_method(self):
        self.engine = DiffEngine()

    def test_no_changes(self):
        original = {"summary": "Test", "skills": ["Python"]}
        response = {"summary": "Test", "skills": ["Python"]}
        diffs, summary = self.engine.generate_diff(original, response)
        assert summary["total_changes"] == 0

    def test_added_skill(self):
        original = {"summary": "Test", "skills": ["Python"]}
        response = {"summary": "Test", "skills": ["Python", "Docker"]}
        diffs, summary = self.engine.generate_diff(original, response)
        assert any(d["change_type"] == "added" for d in diffs)

    def test_removed_skill(self):
        original = {"summary": "Test", "skills": ["Python", "Docker"]}
        response = {"summary": "Test", "skills": ["Python"]}
        diffs, summary = self.engine.generate_diff(original, response)
        assert any(d["change_type"] == "removed" for d in diffs)

    def test_modified_summary(self):
        original = {"summary": "Old summary"}
        response = {"summary": "New summary"}
        diffs, summary = self.engine.generate_diff(original, response)
        assert any(d["change_type"] == "modified" for d in diffs)

    def test_added_experience(self):
        original = {"experience_summary": []}
        response = {"experience": [{"company": "New Corp", "title": "Engineer"}]}
        diffs, summary = self.engine.generate_diff(original, response)
        assert any(d["change_type"] == "added" for d in diffs)

    def test_removed_experience(self):
        original = {"experience_summary": [{"company": "Old Corp", "title": "Dev"}]}
        response = {"experience": []}
        diffs, summary = self.engine.generate_diff(original, response)
        assert any(d["change_type"] == "removed" for d in diffs)

    def test_summary_structure(self):
        original = {"summary": "Old", "skills": ["Python"]}
        response = {"summary": "New", "skills": ["Python", "Docker"]}
        diffs, summary = self.engine.generate_diff(original, response)
        assert "by_type" in summary
        assert "by_section" in summary


# ============================================================
# ChangeClassifier Tests
# ============================================================

class TestChangeClassifier:
    def setup_method(self):
        self.classifier = ChangeClassifier()

    def test_classify_added_skill(self):
        diffs = [
            {
                "section": "skills",
                "change_type": "added",
                "original_value": None,
                "new_value": "Docker",
            }
        ]
        gap_results = [{"category": "skills", "missing_items": "Docker"}]
        changes = self.classifier.classify(diffs, gap_results)
        assert len(changes) == 1
        assert changes[0]["category"] == "skills"
        assert changes[0]["change_type"] == "added"
        assert changes[0]["risk_level"] == "low"

    def test_classify_removed_experience(self):
        diffs = [
            {
                "section": "experience",
                "change_type": "removed",
                "original_value": "Engineer at Tech Corp",
                "new_value": None,
            }
        ]
        changes = self.classifier.classify(diffs, [])
        assert len(changes) == 1
        assert changes[0]["risk_level"] == "high"

    def test_classify_modified_summary(self):
        diffs = [
            {
                "section": "summary",
                "change_type": "modified",
                "original_value": "Old",
                "new_value": "New",
            }
        ]
        changes = self.classifier.classify(diffs, [])
        assert changes[0]["risk_level"] == "medium"

    def test_group_by_category(self):
        changes = [
            {"category": "skills", "change_type": "added"},
            {"category": "skills", "change_type": "added"},
            {"category": "experience", "change_type": "modified"},
        ]
        grouped = self.classifier.get_changes_by_category(changes)
        assert len(grouped["skills"]) == 2
        assert len(grouped["experience"]) == 1


# ============================================================
# ConfidenceEngine Tests
# ============================================================

class TestConfidenceEngine:
    def setup_method(self):
        self.engine = ConfidenceEngine()

    def test_high_confidence_for_gap_addressed(self):
        changes = [
            {
                "category": "skills",
                "change_type": "added",
                "description": "Added Docker",
                "risk_level": "low",
                "supporting_gap_id": "gap-1",
            }
        ]
        validation_reports = {
            "schema_valid": True,
            "truth_valid": True,
            "knowledge_valid": True,
            "gap_valid": True,
        }
        knowledge_rules = [
            {
                "rule_key": "SKILL_001",
                "source": "Harvard",
                "section_name": "skills",
                "is_active": True,
            }
        ]
        gap_results = [{"category": "skills", "missing_items": "Docker"}]

        scores = self.engine.calculate(
            changes, validation_reports, knowledge_rules, gap_results
        )
        assert len(scores) == 1
        assert scores[0]["score"] >= 70

    def test_low_confidence_for_removal(self):
        changes = [
            {
                "category": "experience",
                "change_type": "removed",
                "description": "Removed experience",
                "risk_level": "high",
            }
        ]
        validation_reports = {
            "schema_valid": True,
            "truth_valid": False,
            "knowledge_valid": True,
            "gap_valid": True,
        }
        scores = self.engine.calculate(changes, validation_reports, [], [])
        assert scores[0]["score"] < 50

    def test_overall_confidence(self):
        scores = [{"score": 80}, {"score": 90}]
        overall = self.engine.calculate_overall_confidence(scores)
        assert overall == 85.0

    def test_empty_scores(self):
        overall = self.engine.calculate_overall_confidence([])
        assert overall == 0.0


# ============================================================
# ApprovalPackageBuilder Tests
# ============================================================

class TestApprovalPackageBuilder:
    def setup_method(self):
        self.builder = ApprovalPackageBuilder()

    def test_build_package(self):
        changes = [
            {
                "category": "skills",
                "change_type": "added",
                "description": "Added Docker",
                "risk_level": "low",
            }
        ]
        confidence_scores = [
            {
                "score": 85,
                "risk_level": "low",
                "supporting_rule_id": "RULE_001",
                "supporting_rule_source": "Harvard",
                "supporting_gap_id": "gap-1",
                "validation_result": {"schema_valid": True, "truth_valid": True},
                "reasons": ["Addresses gap"],
            }
        ]
        validation_reports = {
            "schema_valid": True,
            "truth_valid": True,
            "knowledge_valid": True,
            "gap_valid": True,
        }
        knowledge_rules = [
            {
                "rule_key": "RULE_001",
                "source": "Harvard",
                "section_name": "skills",
                "instruction": "Add relevant skills",
                "reason": "ATS optimization",
                "priority": "high",
            }
        ]
        gap_results = [{"category": "skills", "missing_items": "Docker"}]
        diff_summary = {"total_changes": 1, "by_type": {"added": 1}, "by_section": {"skills": 1}}

        package = self.builder.build(
            changes, confidence_scores, validation_reports,
            knowledge_rules, gap_results, diff_summary
        )

        assert "approved_changes" in package
        assert "rejected_changes" in package
        assert "warnings" in package
        assert "supporting_rules" in package
        assert "diff_summary" in package
        assert "validation_summary" in package
        assert package["total_changes"] == 1
        assert package["approved_count"] >= 0

    def test_empty_changes(self):
        package = self.builder.build([], [], {}, [], [], {})
        assert package["total_changes"] == 0
        assert len(package["approved_changes"]) == 0


# ============================================================
# Repository Tests
# ============================================================

class TestAIResponseIntelligenceRepository:
    def setup_method(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.base import Base

        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def teardown_method(self):
        self.db.close()

    def test_create_validation(self):
        from app.repositories.ai_response_intelligence import AIResponseValidationRepository

        repo = AIResponseValidationRepository(self.db)
        validation = repo.create({
            "ai_execution_id": "exec-1",
            "prompt_package_id": "pkg-1",
            "user_id": "user-1",
            "status": "pending",
        })
        self.db.commit()

        assert validation.id is not None
        assert validation.ai_execution_id == "exec-1"
        assert validation.status == "pending"

    def test_get_by_id(self):
        from app.repositories.ai_response_intelligence import AIResponseValidationRepository

        repo = AIResponseValidationRepository(self.db)
        validation = repo.create({
            "ai_execution_id": "exec-1",
            "prompt_package_id": "pkg-1",
            "user_id": "user-1",
            "status": "pending",
        })
        self.db.commit()

        found = repo.get_by_id(validation.id)
        assert found is not None
        assert found.id == validation.id

    def test_get_by_user_id(self):
        from app.repositories.ai_response_intelligence import AIResponseValidationRepository

        repo = AIResponseValidationRepository(self.db)
        repo.create({
            "ai_execution_id": "exec-1",
            "prompt_package_id": "pkg-1",
            "user_id": "user-1",
            "status": "pending",
        })
        repo.create({
            "ai_execution_id": "exec-2",
            "prompt_package_id": "pkg-2",
            "user_id": "user-2",
            "status": "pending",
        })
        self.db.commit()

        items, total = repo.get_by_user_id("user-1")
        assert total == 1
        assert items[0].user_id == "user-1"

    def test_create_diff(self):
        from app.repositories.ai_response_intelligence import ResumeDiffRepository

        repo = ResumeDiffRepository(self.db)
        diff = repo.create({
            "validation_id": "val-1",
            "section": "skills",
            "change_type": "added",
            "new_value": "Docker",
        })
        self.db.commit()

        assert diff.id is not None
        assert diff.section == "skills"

    def test_create_change_set(self):
        from app.repositories.ai_response_intelligence import ChangeSetRepository

        repo = ChangeSetRepository(self.db)
        change = repo.create({
            "validation_id": "val-1",
            "category": "skills",
            "change_type": "added",
            "description": "Added Docker",
            "risk_level": "low",
        })
        self.db.commit()

        assert change.id is not None
        assert change.category == "skills"
