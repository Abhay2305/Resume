"""Unit tests for Gap Analysis Engine.

Tests:
  - SkillGapAnalyzer
  - TechnologyGapAnalyzer
  - ExperienceGapAnalyzer
  - EducationGapAnalyzer
  - CertificationGapAnalyzer
  - KeywordGapAnalyzer
  - GapAnalyzerOrchestrator
  - MatchScorer
  - RecommendationEngine
"""
import pytest
from unittest.mock import MagicMock

from app.services.gap_analysis.analyzers.skill_gap_analyzer import SkillGapAnalyzer
from app.services.gap_analysis.analyzers.technology_gap_analyzer import TechnologyGapAnalyzer
from app.services.gap_analysis.analyzers.experience_gap_analyzer import ExperienceGapAnalyzer
from app.services.gap_analysis.analyzers.education_gap_analyzer import EducationGapAnalyzer
from app.services.gap_analysis.analyzers.certification_gap_analyzer import CertificationGapAnalyzer
from app.services.gap_analysis.analyzers.keyword_gap_analyzer import KeywordGapAnalyzer
from app.services.gap_analysis.analyzers.gap_analyzer import GapAnalyzerOrchestrator
from app.services.gap_analysis.match_scorer import MatchScorer
from app.services.gap_analysis.recommendation_engine import RecommendationEngine


# ============================================================================
# SkillGapAnalyzer Tests
# ============================================================================

class TestSkillGapAnalyzer:
    def setup_method(self):
        self.analyzer = SkillGapAnalyzer()

    def test_exact_match(self):
        result = self.analyzer.analyze(
            required_skills=["Python", "JavaScript"],
            preferred_skills=[],
            resume_skills=["Python", "JavaScript", "TypeScript"],
        )
        assert result["required"]["score"] == 1.0
        assert "python" in result["required"]["matched"]
        assert "javascript" in result["required"]["matched"]

    def test_missing_skills(self):
        result = self.analyzer.analyze(
            required_skills=["Python", "React", "Docker"],
            preferred_skills=[],
            resume_skills=["Python"],
        )
        assert result["required"]["score"] < 1.0
        assert "python" in result["required"]["matched"]
        assert len(result["required"]["missing"]) == 2

    def test_synonym_match(self):
        result = self.analyzer.analyze(
            required_skills=["React", "Vue"],
            preferred_skills=[],
            resume_skills=["react.js", "vue.js"],
        )
        assert len(result["required"]["matched"]) == 2

    def test_preferred_skills(self):
        result = self.analyzer.analyze(
            required_skills=["Python"],
            preferred_skills=["AWS", "Docker"],
            resume_skills=["Python", "AWS"],
        )
        assert result["required"]["score"] == 1.0
        assert result["preferred"]["score"] == 0.5
        assert result["score"] > 0.5

    def test_empty_required(self):
        result = self.analyzer.analyze(
            required_skills=[],
            preferred_skills=["Python"],
            resume_skills=["Python"],
        )
        assert result["score"] == 1.0

    def test_empty_all(self):
        result = self.analyzer.analyze(
            required_skills=[],
            preferred_skills=[],
            resume_skills=[],
        )
        assert result["score"] == 1.0

    def test_case_insensitive(self):
        result = self.analyzer.analyze(
            required_skills=["PYTHON"],
            preferred_skills=[],
            resume_skills=["python"],
        )
        assert result["required"]["score"] == 1.0


# ============================================================================
# TechnologyGapAnalyzer Tests
# ============================================================================

class TestTechnologyGapAnalyzer:
    def setup_method(self):
        self.analyzer = TechnologyGapAnalyzer()

    def test_exact_match(self):
        result = self.analyzer.analyze(
            required_technologies={"frontend": ["React"], "backend": ["Node"]},
            resume_technologies={"frontend": ["React"], "backend": ["Node"], "database": ["PostgreSQL"]},
        )
        assert result["score"] == 1.0

    def test_missing_category(self):
        result = self.analyzer.analyze(
            required_technologies={"frontend": ["React"], "backend": ["Node"]},
            resume_technologies={"frontend": ["React"]},
        )
        assert result["score"] < 1.0
        assert "node" in result["categories"]["backend"]["missing"]

    def test_extra_technologies(self):
        result = self.analyzer.analyze(
            required_technologies={"frontend": ["React"]},
            resume_technologies={"frontend": ["React", "Vue", "Angular"]},
        )
        assert len(result["categories"]["frontend"]["extra"]) == 2

    def test_empty_required(self):
        result = self.analyzer.analyze(
            required_technologies={},
            resume_technologies={"frontend": ["React"]},
        )
        assert result["score"] == 1.0

    def test_get_all_technologies(self):
        techs = self.analyzer.get_all_technologies(
            {"frontend": ["React", "Vue"], "backend": ["Node"]}
        )
        assert len(techs) == 3

    def test_get_required_as_list(self):
        techs = self.analyzer.get_required_as_list(
            {"frontend": ["React"], "backend": ["Node", "Express"]}
        )
        assert len(techs) == 3


# ============================================================================
# ExperienceGapAnalyzer Tests
# ============================================================================

class TestExperienceGapAnalyzer:
    def setup_method(self):
        self.analyzer = ExperienceGapAnalyzer()

    def test_sufficient_years(self):
        result = self.analyzer.analyze(
            required_years=5,
            required_roles=[],
            required_responsibilities=[],
            resume_experience={"total_years": 7, "roles": []},
        )
        assert result["years"]["sufficient"] is True
        assert result["years"]["score"] == 1.0

    def test_insufficient_years(self):
        result = self.analyzer.analyze(
            required_years=5,
            required_roles=[],
            required_responsibilities=[],
            resume_experience={"total_years": 3, "roles": []},
        )
        assert result["years"]["sufficient"] is False
        assert result["years"]["deficit"] == 2
        assert result["years"]["score"] == 0.5

    def test_close_years(self):
        result = self.analyzer.analyze(
            required_years=5,
            required_roles=[],
            required_responsibilities=[],
            resume_experience={"total_years": 4, "roles": []},
        )
        assert result["years"]["score"] == 0.8

    def test_role_match(self):
        result = self.analyzer.analyze(
            required_years=None,
            required_roles=["Senior Engineer", "Tech Lead"],
            required_responsibilities=[],
            resume_experience={"total_years": 5, "roles": ["Senior Software Engineer", "Tech Lead"]},
        )
        assert result["roles"]["score"] >= 0.5

    def test_no_required_years(self):
        result = self.analyzer.analyze(
            required_years=None,
            required_roles=[],
            required_responsibilities=[],
            resume_experience={"total_years": 3, "roles": []},
        )
        assert result["years"]["score"] == 1.0

    def test_keyword_overlap(self):
        result = self.analyzer.analyze(
            required_years=None,
            required_roles=[],
            required_responsibilities=["design microservices", "lead team"],
            resume_experience={"total_years": 5, "roles": [], "responsibilities": ["design and build microservices"]},
        )
        assert result["responsibilities"]["score"] >= 0.5


# ============================================================================
# EducationGapAnalyzer Tests
# ============================================================================

class TestEducationGapAnalyzer:
    def setup_method(self):
        self.analyzer = EducationGapAnalyzer()

    def test_sufficient_degree(self):
        result = self.analyzer.analyze(
            required_degree="Bachelor's",
            required_field=None,
            resume_education={"degrees": ["Bachelor of Science", "Master of Science"], "fields_of_study": ["Computer Science"]},
        )
        assert result["degree"]["sufficient"] is True
        assert result["degree"]["score"] == 1.0

    def test_insufficient_degree(self):
        result = self.analyzer.analyze(
            required_degree="Master's",
            required_field=None,
            resume_education={"degrees": ["Bachelor of Science"], "fields_of_study": ["Computer Science"]},
        )
        assert result["degree"]["sufficient"] is False
        assert result["degree"]["score"] == 0.7

    def test_no_degree(self):
        result = self.analyzer.analyze(
            required_degree="Bachelor's",
            required_field=None,
            resume_education={"degrees": [], "fields_of_study": []},
        )
        assert result["degree"]["sufficient"] is False
        assert result["degree"]["score"] == 0.3

    def test_field_match(self):
        result = self.analyzer.analyze(
            required_degree=None,
            required_field="Computer Science",
            resume_education={"degrees": ["BS"], "fields_of_study": ["Computer Science"]},
        )
        assert result["field"]["match"] is True
        assert result["field"]["score"] == 1.0

    def test_field_no_match(self):
        result = self.analyzer.analyze(
            required_degree=None,
            required_field="Computer Science",
            resume_education={"degrees": ["BS"], "fields_of_study": ["Business"]},
        )
        assert result["field"]["match"] is False
        assert result["field"]["score"] == 0.5

    def test_no_requirements(self):
        result = self.analyzer.analyze(
            required_degree=None,
            required_field=None,
            resume_education={"degrees": ["BS"], "fields_of_study": ["CS"]},
        )
        assert result["score"] == 1.0

    def test_degree_levels(self):
        assert self.analyzer._get_degree_level("Bachelor's") == 4
        assert self.analyzer._get_degree_level("Master's") == 5
        assert self.analyzer._get_degree_level("PhD") == 6


# ============================================================================
# CertificationGapAnalyzer Tests
# ============================================================================

class TestCertificationGapAnalyzer:
    def setup_method(self):
        self.analyzer = CertificationGapAnalyzer()

    def test_exact_match(self):
        result = self.analyzer.analyze(
            required_certifications=["AWS Solutions Architect"],
            preferred_certifications=[],
            resume_certifications=["AWS Solutions Architect"],
        )
        assert result["required"]["score"] == 1.0

    def test_missing_cert(self):
        result = self.analyzer.analyze(
            required_certifications=["AWS Solutions Architect", "PMP"],
            preferred_certifications=[],
            resume_certifications=["AWS Solutions Architect"],
        )
        assert result["required"]["score"] == 0.5
        assert "pmp" in result["required"]["missing"]

    def test_preferred_cert(self):
        result = self.analyzer.analyze(
            required_certifications=[],
            preferred_certifications=["AWS Solutions Architect"],
            resume_certifications=["AWS Solutions Architect"],
        )
        assert result["preferred"]["score"] == 1.0

    def test_cert_equivalence(self):
        assert self.analyzer._cert_equivalent("aws", "amazon web services") is True
        assert self.analyzer._cert_equivalent("azure", "microsoft azure") is True
        assert self.analyzer._cert_equivalent("gcp", "google cloud platform") is True

    def test_no_certs(self):
        result = self.analyzer.analyze(
            required_certifications=[],
            preferred_certifications=[],
            resume_certifications=[],
        )
        assert result["score"] == 1.0

    def test_get_all_certifications(self):
        certs = self.analyzer.get_all_certifications(["AWS", "PMP", "Azure"])
        assert len(certs) == 3


# ============================================================================
# KeywordGapAnalyzer Tests
# ============================================================================

class TestKeywordGapAnalyzer:
    def setup_method(self):
        self.analyzer = KeywordGapAnalyzer()

    def test_found_keywords(self):
        result = self.analyzer.analyze(
            ats_keywords=["python", "react", "aws"],
            resume_text="I have experience with Python, React, and AWS services.",
        )
        assert result["score"] == 1.0
        assert len(result["found"]) == 3
        assert len(result["missing"]) == 0

    def test_missing_keywords(self):
        result = self.analyzer.analyze(
            ats_keywords=["python", "react", "aws"],
            resume_text="I have experience with Python only.",
        )
        assert result["score"] < 1.0
        assert len(result["missing"]) == 2

    def test_weak_keyword(self):
        result = self.analyzer.analyze(
            ats_keywords=["python"],
            resume_text="Python is a language. I use Python daily.",
        )
        assert len(result["found"]) == 1
        assert result["found"][0]["density"] in ("moderate", "strong")

    def test_keyword_in_summary(self):
        result = self.analyzer.analyze(
            ats_keywords=["python"],
            resume_text="General experience.",
            resume_summary="Python developer with 5 years experience.",
        )
        assert len(result["found"]) == 1
        assert result["found"][0]["in_summary"] is True

    def test_empty_keywords(self):
        result = self.analyzer.analyze(
            ats_keywords=[],
            resume_text="Some text",
        )
        assert result["score"] == 1.0

    def test_get_missing_keywords(self):
        missing = self.analyzer.get_missing_keywords(
            ["python", "react", "aws"],
            "I have Python experience.",
        )
        assert len(missing) == 2

    def test_get_keyword_density(self):
        density = self.analyzer.get_keyword_density(
            "Python is great. I use Python daily.",
            ["python", "react"],
        )
        assert density["python"] == 2
        assert density["react"] == 0


# ============================================================================
# MatchScorer Tests
# ============================================================================

class TestMatchScorer:
    def setup_method(self):
        self.scorer = MatchScorer()

    def test_perfect_scores(self):
        gap_results = {
            "skills": {"score": 1.0},
            "technology": {"score": 1.0},
            "experience": {"score": 1.0},
            "education": {"score": 1.0},
            "certifications": {"score": 1.0},
            "keywords": {"score": 1.0},
        }
        scores = self.scorer.calculate_scores(gap_results)
        assert scores["overall_match_score"] == 1.0

    def test_zero_scores(self):
        gap_results = {
            "skills": {"score": 0.0},
            "technology": {"score": 0.0},
            "experience": {"score": 0.0},
            "education": {"score": 0.0},
            "certifications": {"score": 0.0},
            "keywords": {"score": 0.0},
        }
        scores = self.scorer.calculate_scores(gap_results)
        assert scores["overall_match_score"] == 0.0

    def test_mixed_scores(self):
        gap_results = {
            "skills": {"score": 0.8},
            "technology": {"score": 0.6},
            "experience": {"score": 1.0},
            "education": {"score": 1.0},
            "certifications": {"score": 0.5},
            "keywords": {"score": 0.7},
        }
        scores = self.scorer.calculate_scores(gap_results)
        assert 0.0 <= scores["overall_match_score"] <= 1.0

    def test_empty_results(self):
        scores = self.scorer.calculate_scores({})
        assert scores["overall_match_score"] == 0.0

    def test_match_levels(self):
        assert self.scorer.get_match_level(0.95) == "excellent"
        assert self.scorer.get_match_level(0.8) == "good"
        assert self.scorer.get_match_level(0.6) == "moderate"
        assert self.scorer.get_match_level(0.3) == "weak"
        assert self.scorer.get_match_level(0.1) == "poor"

    def test_weights_sum_to_one(self):
        total = sum(self.scorer.WEIGHTS.values())
        assert abs(total - 1.0) < 0.01


# ============================================================================
# RecommendationEngine Tests
# ============================================================================

class TestRecommendationEngine:
    def setup_method(self):
        self.engine = RecommendationEngine()

    def test_skill_recommendations(self):
        gap_results = {
            "skills": {
                "required": {"missing": ["python", "react"], "matched": ["javascript"]},
                "preferred": {"missing": ["aws"]},
                "score": 0.3,
            },
            "technology": {"categories": {}, "score": 1.0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(gap_results, {"skills": ["javascript"]}, [])
        skill_recs = [r for r in recs if r["category"] == "skills"]
        assert len(skill_recs) >= 2

    def test_technology_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {
                "categories": {
                    "frontend": {"missing": ["react"], "score": 0.5},
                },
                "score": 0.5,
            },
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(gap_results, {}, [])
        tech_recs = [r for r in recs if r["category"] == "technologies"]
        assert len(tech_recs) >= 1

    def test_experience_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {"categories": {}, "score": 1.0},
            "experience": {
                "years": {"sufficient": False, "required": 5, "actual": 3, "deficit": 2},
                "roles": {"missing": ["Tech Lead"]},
                "score": 0.5,
            },
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(gap_results, {}, [])
        exp_recs = [r for r in recs if r["category"] == "experience"]
        assert len(exp_recs) >= 1

    def test_education_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {"categories": {}, "score": 1.0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {
                "degree": {"sufficient": False, "required": "Master's"},
                "field": {"match": False, "required": "Computer Science"},
                "score": 0.3,
            },
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(gap_results, {}, [])
        edu_recs = [r for r in recs if r["category"] == "education"]
        assert len(edu_recs) >= 1

    def test_certification_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {"categories": {}, "score": 1.0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {
                "required": {"missing": ["PMP"]},
                "preferred": {"missing": ["AWS"]},
                "score": 0.0,
            },
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(gap_results, {}, [])
        cert_recs = [r for r in recs if r["category"] == "certifications"]
        assert len(cert_recs) >= 1

    def test_keyword_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {"categories": {}, "score": 1.0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": ["kubernetes"], "weak": ["docker"], "score": 0.5},
        }
        recs = self.engine.generate(gap_results, {}, [])
        kw_recs = [r for r in recs if r["category"] == "keywords"]
        assert len(kw_recs) >= 1

    def test_general_recommendations(self):
        gap_results = {
            "skills": {"required": {"missing": [], "matched": []}, "preferred": {"missing": []}, "score": 1.0},
            "technology": {"categories": {}, "score": 1.0},
            "experience": {"years": {"sufficient": True}, "roles": {"missing": []}, "score": 1.0},
            "education": {"degree": {"sufficient": True}, "field": {"match": True}, "score": 1.0},
            "certifications": {"required": {"missing": []}, "preferred": {"missing": []}, "score": 1.0},
            "keywords": {"missing": [], "weak": [], "score": 1.0},
        }
        recs = self.engine.generate(
            gap_results,
            {"summary": "Short", "projects": [{"name": "Proj", "description": "Short"}], "achievements": []},
            [],
        )
        assert len(recs) >= 1

    def test_deduplication(self):
        recs = [
            {"category": "skills", "action": "add_skill", "target_item": "python", "description": "Add python", "priority": "high"},
            {"category": "skills", "action": "add_skill", "target_item": "python", "description": "Add python", "priority": "high"},
        ]
        unique = self.engine._deduplicate_recommendations(recs)
        assert len(unique) == 1


# ============================================================================
# GapAnalyzerOrchestrator Tests
# ============================================================================

class TestGapAnalyzerOrchestrator:
    def setup_method(self):
        self.orchestrator = GapAnalyzerOrchestrator()

    def test_full_analysis(self):
        resume_knowledge = {
            "skills": ["Python", "JavaScript"],
            "technologies": {"frontend": ["React"], "backend": ["Node"]},
            "experience_summary": {"entries": [{"role": "Engineer"}]},
            "education_summary": {"degrees": ["Bachelor's"], "fields_of_study": ["CS"]},
            "certifications": ["AWS"],
            "summary": "Python developer",
            "total_experience_years": 5,
        }
        entities = [
            {"entity_type": "skill", "entity_value": "Python", "is_required": True},
            {"entity_type": "skill", "entity_value": "React", "is_required": True},
            {"entity_type": "framework", "entity_value": "React", "is_required": True},
            {"entity_type": "framework", "entity_value": "Vue", "is_required": False},
        ]
        parsed_data = {"ats_keywords": ["python", "react", "javascript"]}

        result = self.orchestrator.analyze(resume_knowledge, entities, parsed_data)

        assert "skills" in result
        assert "technology" in result
        assert "experience" in result
        assert "education" in result
        assert "certifications" in result
        assert "keywords" in result

    def test_empty_resume(self):
        result = self.orchestrator.analyze({}, [], None)
        assert "skills" in result
        assert result["skills"]["required"]["score"] == 1.0

    def test_empty_opportunity(self):
        resume_knowledge = {
            "skills": ["Python"],
            "technologies": {},
            "experience_summary": {},
            "education_summary": {},
            "certifications": [],
            "summary": "",
            "total_experience_years": 3,
        }
        result = self.orchestrator.analyze(resume_knowledge, [], None)
        assert result["skills"]["required"]["score"] == 1.0

    def test_extract_skills_from_entities(self):
        entities = [
            {"entity_type": "skill", "entity_value": "Python", "is_required": True},
            {"entity_type": "skill", "entity_value": "Docker", "is_required": False},
        ]
        required, preferred = self.orchestrator._extract_skills_from_entities(entities)
        assert "Python" in required
        assert "Docker" in preferred

    def test_extract_technologies_from_entities(self):
        entities = [
            {"entity_type": "framework", "entity_value": "React"},
            {"entity_type": "database", "entity_value": "PostgreSQL"},
            {"entity_type": "cloud_platform", "entity_value": "AWS"},
        ]
        techs = self.orchestrator._extract_technologies_from_entities(entities)
        assert "frontend" in techs
        assert "database" in techs
        assert "cloud" in techs

    def test_extract_experience_from_entities(self):
        entities = [
            {"entity_type": "experience_level", "entity_value": "5+ years", "entity_metadata": {"years": "5"}},
            {"entity_type": "role", "entity_value": "Senior Engineer"},
        ]
        info = self.orchestrator._extract_experience_from_entities(entities)
        assert info["required_years"] == 5
        assert "Senior Engineer" in info["required_roles"]

    def test_extract_education_from_entities(self):
        entities = [
            {"entity_type": "education", "entity_value": "Bachelor's"},
            {"entity_type": "education", "entity_value": "Computer Science"},
        ]
        info = self.orchestrator._extract_education_from_entities(entities)
        assert info["required_degree"] == "Bachelor's"
        assert info["required_field"] == "Computer Science"

    def test_extract_certs_from_entities(self):
        entities = [
            {"entity_type": "certification", "entity_value": "AWS", "is_required": True},
            {"entity_type": "certification", "entity_value": "PMP", "is_required": False},
        ]
        required, preferred = self.orchestrator._extract_certs_from_entities(entities)
        assert "AWS" in required
        assert "PMP" in preferred

    def test_extract_ats_keywords(self):
        parsed_data = {"ats_keywords": ["python", "react", "aws"]}
        keywords = self.orchestrator._extract_ats_keywords(parsed_data)
        assert len(keywords) == 3

    def test_extract_ats_keywords_none(self):
        keywords = self.orchestrator._extract_ats_keywords(None)
        assert keywords == []
