"""Tests for KnowledgeValidator completion (Phase I).

Tests:
  - _validate_skills_rules() full implementation
  - _verify_rule_coverage() full implementation
  - Valid rule compliance
  - Missing rule coverage
  - Invalid skill behavior
  - Rule category coverage
  - Provenance-aware validation
  - Edge cases
  - No-rule/empty-context behavior
"""
import pytest

from app.services.ai_response_intelligence.knowledge_validator import KnowledgeValidator


@pytest.fixture
def validator():
    return KnowledgeValidator()


@pytest.fixture
def sample_rules():
    return [
        {"rule_key": "R1", "source": "Harvard", "section_name": "summary", "instruction": "Keep summary concise", "category": "Length"},
        {"rule_key": "R2", "source": "Harvard", "section_name": "experience", "instruction": "Use strong action verbs", "category": "Action Verbs"},
        {"rule_key": "R3", "source": "MIT", "section_name": "skills", "instruction": "Include technical skills", "category": "Keywords"},
        {"rule_key": "R4", "source": "Yale", "section_name": "skills", "instruction": "Group skills by category", "category": "Formatting"},
        {"rule_key": "R5", "source": "ATS", "section_name": "skills", "instruction": "Keep skills concise and brief", "category": "Length"},
        {"rule_key": "R6", "source": "Harvard", "section_name": "education", "instruction": "Include relevant coursework", "category": "Specificity"},
        {"rule_key": "R7", "source": "ATS", "section_name": "ats", "instruction": "Use keywords naturally", "category": "Keywords"},
    ]


class TestValidateSkillsRules:
    def test_empty_skills_with_rules(self, validator, sample_rules):
        response = {"skills": []}
        issues = validator._validate_skills_rules(response, sample_rules)
        assert len(issues) > 0
        assert any("empty" in i["message"].lower() for i in issues)

    def test_skills_with_grouping_rule(self, validator, sample_rules):
        response = {"skills": ["Python", "JavaScript"]}
        issues = validator._validate_skills_rules(response, sample_rules)
        assert any("group" in i["message"].lower() for i in issues)

    def test_skills_with_grouping_satisfied(self, validator):
        rules = [{"rule_key": "R1", "source": "Test", "section_name": "skills", "instruction": "Group skills by category"}]
        response = {"skills": [{"category": "Programming", "items": ["Python"]}]}
        issues = validator._validate_skills_rules(response, rules)
        assert not any("group" in i["message"].lower() for i in issues)

    def test_no_technical_skills(self, validator):
        rules = [{"rule_key": "R1", "source": "Test", "section_name": "skills", "instruction": "Include technical skills"}]
        response = {"skills": ["Communication", "Leadership"]}
        issues = validator._validate_skills_rules(response, rules)
        assert any("technical" in i["message"].lower() for i in issues)

    def test_technical_skills_present(self, validator):
        rules = [{"rule_key": "R1", "source": "Test", "section_name": "skills", "instruction": "Include technical skills"}]
        response = {"skills": ["Python", "JavaScript", "SQL"]}
        issues = validator._validate_skills_rules(response, rules)
        assert not any("technical" in i["message"].lower() for i in issues)

    def test_skills_too_long(self, validator):
        rules = [{"rule_key": "R1", "source": "Test", "section_name": "skills", "instruction": "Keep skills concise and brief"}]
        response = {"skills": [f"Skill{i}" for i in range(25)]}
        issues = validator._validate_skills_rules(response, rules)
        assert any("concise" in i["message"].lower() or "25" in i["message"] for i in issues)

    def test_non_list_skills(self, validator, sample_rules):
        response = {"skills": "not a list"}
        issues = validator._validate_skills_rules(response, sample_rules)
        assert issues == []

    def test_no_skills_rules(self, validator):
        response = {"skills": ["Python"]}
        issues = validator._validate_skills_rules(response, [])
        assert issues == []


class TestVerifyRuleCoverage:
    def test_summary_without_rules(self, validator):
        response = {"summary": "Professional summary"}
        issues = validator._verify_rule_coverage(response, [])
        assert any("summary" in i["category"] for i in issues)

    def test_summary_with_rules(self, validator, sample_rules):
        response = {"summary": "Professional summary"}
        issues = validator._verify_rule_coverage(response, sample_rules)
        assert not any("summary" in i.get("category", "") and "unsupported" in i.get("type", "") for i in issues)

    def test_experience_without_rules(self, validator):
        response = {"experience": [{"title": "Engineer"}]}
        issues = validator._verify_rule_coverage(response, [])
        assert any("experience" in i["category"] for i in issues)

    def test_experience_with_rules(self, validator, sample_rules):
        response = {"experience": [{"title": "Engineer"}]}
        issues = validator._verify_rule_coverage(response, sample_rules)
        assert not any("experience" in i.get("category", "") and "unsupported" in i.get("type", "") for i in issues)

    def test_skills_without_rules(self, validator):
        response = {"skills": ["Python"]}
        issues = validator._verify_rule_coverage(response, [])
        assert any("skills" in i["category"] for i in issues)

    def test_skills_with_rules(self, validator, sample_rules):
        response = {"skills": ["Python"]}
        issues = validator._verify_rule_coverage(response, sample_rules)
        assert not any("skills" in i.get("category", "") and "unsupported" in i.get("type", "") for i in issues)

    def test_education_without_rules(self, validator):
        response = {"education": [{"degree": "BS"}]}
        issues = validator._verify_rule_coverage(response, [])
        assert any("education" in i["category"] for i in issues)

    def test_empty_response(self, validator, sample_rules):
        issues = validator._verify_rule_coverage({}, sample_rules)
        assert issues == []

    def test_no_rules_all_sections_present(self, validator):
        response = {
            "summary": "Test",
            "experience": [{"title": "E"}],
            "skills": ["S"],
            "education": [{"degree": "D"}],
        }
        issues = validator._verify_rule_coverage(response, [])
        assert len(issues) == 4


class TestValidateIntegration:
    def test_full_validation_with_all_sections(self, validator, sample_rules):
        response = {
            "summary": "Professional with 5 years experience",
            "experience": [{"title": "Engineer", "description": ["Led team of 5"]}],
            "skills": ["Python", "JavaScript"],
            "education": [{"degree": "BS CS"}],
        }
        is_valid, score, issues, details = validator.validate(response, sample_rules)
        assert isinstance(is_valid, bool)
        assert isinstance(score, float)
        assert isinstance(issues, list)
        assert isinstance(details, dict)

    def test_validation_with_empty_rules(self, validator):
        response = {"summary": "Test"}
        is_valid, score, issues, details = validator.validate(response, [])
        assert is_valid is True
        assert score == 60.0

    def test_validation_with_empty_response(self, validator, sample_rules):
        is_valid, score, issues, details = validator.validate({}, sample_rules)
        assert is_valid is False
        assert score == 0.0

    def test_score_never_negative(self, validator):
        many_rules = [
            {"rule_key": f"R{i}", "source": "Test", "section_name": "summary", "instruction": f"Rule {i}"}
            for i in range(50)
        ]
        response = {"summary": "I am a professional"}
        is_valid, score, issues, details = validator.validate(response, many_rules)
        assert score >= 0.0

    def test_score_never_exceeds_100(self, validator, sample_rules):
        response = {
            "summary": "Professional with 5 years experience",
            "experience": [{"title": "Engineer", "description": ["Led team"]}],
            "skills": ["Python"],
        }
        is_valid, score, issues, details = validator.validate(response, sample_rules)
        assert score <= 100.0
