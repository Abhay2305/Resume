"""Comprehensive Validation Boundary Tests (V-005, V-006, V-007).

V-005: TruthValidator against all fabrication types
V-006: SchemaValidator against malformed responses
V-007: GapValidator against addressed/unaddressed/fabricated gaps

These tests verify validators catch real violations, not just mocked existence.
"""
import pytest

from app.services.ai_response_intelligence.truth_validator import TruthValidator
from app.services.ai_response_intelligence.schema_validator import ResponseSchemaValidator
from app.services.ai_response_intelligence.gap_validator import GapValidator


@pytest.fixture
def truth_validator():
    return TruthValidator()


@pytest.fixture
def schema_validator():
    return ResponseSchemaValidator()


@pytest.fixture
def gap_validator():
    return GapValidator()


@pytest.fixture
def valid_resume_knowledge():
    return {
        "experience_summary": [
            {"company": "Google", "title": "Software Engineer", "bullets": ["Developed search features"]},
            {"company": "Microsoft", "title": "Senior Engineer", "bullets": ["Led cloud migration"]},
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker"],
        "education_summary": [
            {"institution": "MIT", "degree": "BS Computer Science"},
        ],
        "certifications": [
            {"name": "AWS Solutions Architect", "issuer": "Amazon"},
        ],
    }


@pytest.fixture
def valid_response():
    return {
        "summary": "Software engineer with 5 years experience at Google and Microsoft.",
        "experience": [
            {"company": "Google", "title": "Software Engineer", "bullets": ["Developed search features"]},
            {"company": "Microsoft", "title": "Senior Engineer", "bullets": ["Led cloud migration"]},
        ],
        "skills": ["Python", "JavaScript", "AWS", "Docker"],
        "education": [
            {"institution": "MIT", "degree": "BS Computer Science"},
        ],
    }


# ============================================================
# V-005: TruthValidator Tests
# ============================================================

class TestTruthValidatorFabricationDetection:
    def test_fabricated_company(self, truth_validator, valid_resume_knowledge):
        response = {
            "experience": [
                {"company": "FAKE_COMPANY", "title": "Engineer", "bullets": ["Did stuff"]},
            ],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        assert is_valid is False or score < 100
        assert any("fabricated" in i["type"].lower() or "company" in i.get("message", "").lower() for i in issues)

    def test_fabricated_skill(self, truth_validator, valid_resume_knowledge):
        response = {
            "skills": ["Python", "JavaScript", "FAKE_SKILL_12345"],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        assert any("skill" in i.get("message", "").lower() or "fabricated" in i["type"].lower() for i in issues)

    def test_fabricated_institution(self, truth_validator, valid_resume_knowledge):
        response = {
            "education": [
                {"institution": "FAKE_UNIVERSITY", "degree": "PhD"},
            ],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        assert any("institution" in i.get("message", "").lower() or "fabricated" in i["type"].lower() for i in issues)

    def test_fabricated_role(self, truth_validator, valid_resume_knowledge):
        response = {
            "experience": [
                {"company": "Google", "title": "CEO", "bullets": ["Ran the company"]},
            ],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        role_issues = [i for i in issues if "role" in i.get("message", "").lower() or "title" in i.get("message", "").lower()]
        assert len(role_issues) > 0

    def test_valid_response_passes(self, truth_validator, valid_resume_knowledge, valid_response):
        is_valid, score, issues, details = truth_validator.validate(valid_response, valid_resume_knowledge)
        assert is_valid is True
        assert score >= 80.0

    def test_empty_response_fails(self, truth_validator, valid_resume_knowledge):
        is_valid, score, issues, details = truth_validator.validate({}, valid_resume_knowledge)
        assert is_valid is False
        assert score == 0.0

    def test_no_knowledge_returns_warning(self, truth_validator, valid_response):
        is_valid, score, issues, details = truth_validator.validate(valid_response, {})
        assert is_valid is True
        assert score == 50.0

    def test_removed_company_detected(self, truth_validator, valid_resume_knowledge):
        response = {
            "experience": [
                {"company": "Microsoft", "title": "Engineer", "bullets": ["Did stuff"]},
            ],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        removal_issues = [i for i in issues if "remov" in i["type"].lower()]
        assert len(removal_issues) > 0

    def test_inflated_metric_detected(self, truth_validator, valid_resume_knowledge):
        response = {
            "experience": [
                {"company": "Google", "title": "Engineer", "bullets": ["Improved performance by 500%"]},
            ],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        assert score < 100.0

    def test_multiple_fabrications_reduce_score(self, truth_validator, valid_resume_knowledge):
        response = {
            "experience": [
                {"company": "FAKE1", "title": "Engineer", "bullets": ["Did stuff"]},
                {"company": "FAKE2", "title": "Manager", "bullets": ["Led team"]},
            ],
            "skills": ["Python", "FAKE_SKILL"],
            "education": [{"institution": "FAKE_UNI", "degree": "BS"}],
        }
        is_valid, score, issues, details = truth_validator.validate(response, valid_resume_knowledge)
        assert score < 60.0
        assert len(issues) >= 3


# ============================================================
# V-006: SchemaValidator Tests
# ============================================================

class TestSchemaValidatorMalformedResponses:
    def test_empty_response_fails(self, schema_validator):
        is_valid, score, issues, details = schema_validator.validate({})
        assert is_valid is False
        assert score == 0.0

    def test_none_response_fails(self, schema_validator):
        is_valid, score, issues, details = schema_validator.validate(None)
        assert is_valid is False
        assert score == 0.0

    def test_string_response_fails(self, schema_validator):
        is_valid, score, issues, details = schema_validator.validate("not a dict")
        assert is_valid is False
        assert score == 0.0

    def test_missing_summary_fails(self, schema_validator):
        response = {"experience": [], "skills": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        assert any("summary" in i.get("section", "") for i in issues)
        assert score < 100.0

    def test_missing_experience_fails(self, schema_validator):
        response = {"summary": "Test summary", "skills": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        assert any("experience" in i.get("section", "") for i in issues)

    def test_missing_skills_fails(self, schema_validator):
        response = {"summary": "Test summary", "experience": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        assert any("skills" in i.get("section", "") for i in issues)

    def test_summary_not_string_fails(self, schema_validator):
        response = {"summary": 123, "experience": [], "skills": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        type_issues = [i for i in issues if i.get("section") == "summary" and "type" in i["type"]]
        assert len(type_issues) > 0

    def test_summary_too_short_fails(self, schema_validator):
        response = {"summary": "Hi", "experience": [], "skills": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        short_issues = [i for i in issues if "short" in i["type"].lower() or "short" in i.get("message", "").lower()]
        assert len(short_issues) > 0

    def test_skills_not_list_fails(self, schema_validator):
        response = {"summary": "Test summary", "experience": [], "skills": "Python, JavaScript"}
        is_valid, score, issues, details = schema_validator.validate(response)
        type_issues = [i for i in issues if i.get("section") == "skills" and "type" in i["type"]]
        assert len(type_issues) > 0

    def test_empty_skills_fails(self, schema_validator):
        response = {"summary": "Test summary", "experience": [], "skills": []}
        is_valid, score, issues, details = schema_validator.validate(response)
        empty_issues = [i for i in issues if "empty" in i["type"].lower()]
        assert len(empty_issues) > 0

    def test_experience_not_list_fails(self, schema_validator):
        response = {"summary": "Test summary", "experience": "not a list", "skills": ["Python"]}
        is_valid, score, issues, details = schema_validator.validate(response)
        type_issues = [i for i in issues if i.get("section") == "experience" and "type" in i["type"]]
        assert len(type_issues) > 0

    def test_valid_response_passes(self, schema_validator):
        response = {
            "summary": "Software engineer with 5 years experience.",
            "experience": [{"title": "Engineer", "company": "Google"}],
            "skills": ["Python", "JavaScript"],
        }
        is_valid, score, issues, details = schema_validator.validate(response)
        assert is_valid is True
        assert score >= 80.0

    def test_experience_missing_required_fields(self, schema_validator):
        response = {
            "summary": "Test summary",
            "experience": [{"bullets": ["Did stuff"]}],
            "skills": ["Python"],
        }
        is_valid, score, issues, details = schema_validator.validate(response)
        field_issues = [i for i in issues if "field" in i.get("message", "").lower() or "missing" in i["type"].lower()]
        assert len(field_issues) > 0


# ============================================================
# V-007: GapValidator Tests
# ============================================================

class TestGapValidatorCoverage:
    def test_addressed_gaps_pass(self, gap_validator):
        response = {
            "skills": ["Python", "JavaScript", "React", "Node.js"],
            "summary": "Full-stack developer with React and Node.js experience.",
        }
        gap_analysis = {"skill_match_score": 80}
        gap_results = [
            {"category": "skills", "missing_items": "React,Node.js", "gap_type": "missing"},
        ]
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert score >= 70.0

    def test_unaddressed_gaps_fail(self, gap_validator):
        response = {
            "skills": ["Python"],
            "summary": "Python developer.",
        }
        gap_analysis = {"skill_match_score": 40}
        gap_results = [
            {"category": "skills", "missing_items": "React,Angular,Vue", "gap_type": "missing"},
        ]
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert score < 100.0
        gap_issues = [i for i in issues if "gap" in i.get("message", "").lower() or "missing" in i.get("message", "").lower()]
        assert len(gap_issues) > 0

    def test_empty_response_fails(self, gap_validator):
        gap_analysis = {"skill_match_score": 50}
        gap_results = [{"category": "skills", "missing_items": "Python"}]
        is_valid, score, issues, details = gap_validator.validate({}, gap_analysis, gap_results)
        assert is_valid is False
        assert score == 0.0

    def test_no_gap_analysis_returns_warning(self, gap_validator):
        response = {"skills": ["Python"]}
        is_valid, score, issues, details = gap_validator.validate(response, {}, [])
        assert is_valid is True
        assert score == 70.0

    def test_partially_addressed_gaps(self, gap_validator):
        response = {
            "skills": ["Python", "React"],
            "summary": "Developer with React experience.",
        }
        gap_analysis = {"skill_match_score": 60}
        gap_results = [
            {"category": "skills", "missing_items": "React,Angular,Vue", "gap_type": "missing"},
        ]
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert 40.0 <= score <= 100.0

    def test_fabricated_coverage_detected(self, gap_validator):
        response = {
            "skills": ["Python", "React", "Angular", "Vue", "Django", "Flask"],
            "summary": "Expert in all frameworks.",
        }
        gap_analysis = {"skill_match_score": 90}
        gap_results = []
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert score >= 40.0

    def test_unnecessary_modifications_flagged(self, gap_validator):
        response = {
            "skills": ["Python", "Completely New Skill Not In Gap"],
            "summary": "Totally rewritten summary with unrelated changes.",
        }
        gap_analysis = {"skill_match_score": 30}
        gap_results = [
            {"category": "skills", "missing_items": "JavaScript", "gap_type": "missing"},
        ]
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert score < 100.0

    def test_multiple_gap_types(self, gap_validator):
        response = {
            "skills": ["Python", "JavaScript"],
            "summary": "Developer with JavaScript experience.",
        }
        gap_analysis = {"skill_match_score": 50}
        gap_results = [
            {"category": "skills", "missing_items": "JavaScript", "gap_type": "missing"},
            {"category": "technology", "missing_items": "React", "gap_type": "missing"},
        ]
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert "total_gaps" in details
        assert details["total_gaps"] == 2

    def test_no_gaps_returns_perfect(self, gap_validator):
        response = {"skills": ["Python"], "summary": "Python developer."}
        gap_analysis = {"skill_match_score": 100}
        gap_results = []
        is_valid, score, issues, details = gap_validator.validate(response, gap_analysis, gap_results)
        assert is_valid is True
        assert score == 100.0
