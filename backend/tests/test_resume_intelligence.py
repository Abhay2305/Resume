"""Unit tests for Resume Intelligence Engine.

Tests the parser, normalizer, extractors, and knowledge builder
without requiring a database or API calls.
"""
import pytest

from app.services.resume_intelligence.parsers.parser import ResumeParser
from app.services.resume_intelligence.parsers.normalizer import ResumeNormalizer
from app.services.resume_intelligence.extractors.contact_extractor import ContactExtractor
from app.services.resume_intelligence.extractors.skill_extractor import SkillExtractor
from app.services.resume_intelligence.extractors.technology_extractor import TechnologyExtractor
from app.services.resume_intelligence.extractors.language_extractor import LanguageExtractor
from app.services.resume_intelligence.extractors.certification_extractor import CertificationExtractor
from app.services.resume_intelligence.extractors.education_extractor import EducationExtractor
from app.services.resume_intelligence.extractors.experience_extractor import ExperienceExtractor
from app.services.resume_intelligence.extractors.project_extractor import ProjectExtractor
from app.services.resume_intelligence.extractors.achievement_extractor import AchievementExtractor
from app.services.resume_intelligence.extractors.metric_extractor import MetricExtractor
from app.services.resume_intelligence.knowledge_builder import ResumeKnowledgeBuilder


# ============================================================
# ResumeParser Tests
# ============================================================

class TestResumeParser:
    def setup_method(self):
        self.parser = ResumeParser()

    def test_parse_empty_text(self):
        result = self.parser.parse("")
        assert result["sections"] == {}
        assert result["metadata"] == {}

    def test_parse_none_text(self):
        result = self.parser.parse(None)
        assert result["sections"] == {}

    def test_parse_basic_text(self):
        text = "John Doe\nPython developer with 5 years experience"
        result = self.parser.parse(text)
        assert result["raw_text"] == text
        assert "general" in result["sections"]
        assert result["metadata"]["word_count"] > 0

    def test_parse_with_sections(self):
        text = """John Doe
Contact
john@example.com

Summary
Senior developer with 10 years experience

Skills
Python, JavaScript, React

Experience
Google - Senior Engineer
- Built microservices
- Led team of 5"""
        result = self.parser.parse(text)
        assert "contact" in result["sections"]
        assert "summary" in result["sections"]
        assert "skills" in result["sections"]
        assert "experience" in result["sections"]

    def test_parse_removes_html(self):
        text = "<p>Hello</p><div>World</div>"
        result = self.parser.parse(text)
        assert "<p>" not in result["sections"].get("general", "")
        assert "Hello" in result["sections"].get("general", "")

    def test_metadata_has_bullets(self):
        text = "Experience\n- Built thing\n- Led team"
        result = self.parser.parse(text)
        assert result["metadata"]["has_bullet_points"] is True


# ============================================================
# ResumeNormalizer Tests
# ============================================================

class TestResumeNormalizer:
    def setup_method(self):
        self.normalizer = ResumeNormalizer()

    def test_normalize_empty(self):
        result = self.normalizer.normalize({"sections": {}, "metadata": {}})
        assert result["sections"] == {}

    def test_normalize_text(self):
        result = self.normalizer.normalize({
            "sections": {"summary": "  Hello   World  "},
            "metadata": {},
        })
        assert result["sections"]["summary"] == "Hello World"

    def test_normalize_list(self):
        items = ["Python", "python", "PYTHON", "JavaScript"]
        result = self.normalizer.normalize_list(items)
        assert len(result) == 2
        assert result == ["javascript", "python"]

    def test_normalize_date_with_month(self):
        result = self.normalizer.normalize_date("January 2020")
        assert result == "2020-01"

    def test_normalize_date_year_only(self):
        result = self.normalizer.normalize_date("2020")
        assert result == "2020"

    def test_normalize_experience_level(self):
        assert self.normalizer.normalize_experience_level("Senior") == "senior"
        assert self.normalizer.normalize_experience_level("Entry Level") == "junior"
        assert self.normalizer.normalize_experience_level("Lead") == "lead"


# ============================================================
# ContactExtractor Tests
# ============================================================

class TestContactExtractor:
    def setup_method(self):
        self.extractor = ContactExtractor()

    def test_extract_email(self):
        sections = {"contact": "john.doe@example.com"}
        result = self.extractor.extract(sections)
        assert any(e["entity_value"] == "john.doe@example.com" for e in result["entities"])

    def test_extract_phone(self):
        sections = {"contact": "555-123-4567"}
        result = self.extractor.extract(sections)
        assert any(e["entity_metadata"]["contact_type"] == "phone" for e in result["entities"])

    def test_extract_linkedin(self):
        sections = {"contact": "linkedin.com/in/johndoe"}
        result = self.extractor.extract(sections)
        assert any("linkedin" in e["entity_value"] for e in result["entities"])

    def test_extract_github(self):
        sections = {"contact": "github.com/johndoe"}
        result = self.extractor.extract(sections)
        assert any("github" in e["entity_value"] for e in result["entities"])

    def test_extract_empty(self):
        sections = {}
        result = self.extractor.extract(sections)
        assert len(result["entities"]) == 0


# ============================================================
# SkillExtractor Tests
# ============================================================

class TestSkillExtractor:
    def setup_method(self):
        self.extractor = SkillExtractor()

    def test_extract_skills_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_skills_from_skills_section(self):
        sections = {"skills": "Python, JavaScript, React, Docker"}
        result = self.extractor.extract(sections)
        values = [e["entity_value"] for e in result["entities"]]
        assert "python" in values
        assert "javascript" in values

    def test_extract_skills_from_general(self):
        sections = {"general": "Experienced in Python and AWS"}
        result = self.extractor.extract(sections)
        values = [e["entity_value"] for e in result["entities"]]
        assert "python" in values


# ============================================================
# TechnologyExtractor Tests
# ============================================================

class TestTechnologyExtractor:
    def setup_method(self):
        self.extractor = TechnologyExtractor()

    def test_extract_technologies_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_technologies(self):
        sections = {"skills": "React, Django, PostgreSQL, AWS, Docker"}
        result = self.extractor.extract(sections)
        types = set(e["entity_type"] for e in result["entities"])
        assert len(types) > 0


# ============================================================
# LanguageExtractor Tests
# ============================================================

class TestLanguageExtractor:
    def setup_method(self):
        self.extractor = LanguageExtractor()

    def test_extract_languages_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_languages(self):
        sections = {"skills": "Python, JavaScript, Go, Rust"}
        result = self.extractor.extract(sections)
        values = [e["entity_value"] for e in result["entities"]]
        assert "python" in values
        assert "javascript" in values


# ============================================================
# CertificationExtractor Tests
# ============================================================

class TestCertificationExtractor:
    def setup_method(self):
        self.extractor = CertificationExtractor()

    def test_extract_certs_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_certs(self):
        sections = {"certifications": "AWS Certified Solutions Architect, PMP"}
        result = self.extractor.extract(sections)
        assert len(result["entities"]) > 0


# ============================================================
# EducationExtractor Tests
# ============================================================

class TestEducationExtractor:
    def setup_method(self):
        self.extractor = EducationExtractor()

    def test_extract_education_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_degrees(self):
        sections = {"education": "Bachelor of Science in Computer Science\nMaster of Business Administration"}
        result = self.extractor.extract(sections)
        values = [e["entity_value"] for e in result["entities"]]
        assert any("bachelor" in v for v in values)
        assert any("master" in v for v in values)

    def test_extract_fields(self):
        sections = {"education": "BS in Computer Science from MIT"}
        result = self.extractor.extract(sections)
        values = [e["entity_value"] for e in result["entities"]]
        assert "computer science" in values


# ============================================================
# ExperienceExtractor Tests
# ============================================================

class TestExperienceExtractor:
    def setup_method(self):
        self.extractor = ExperienceExtractor()

    def test_extract_experience_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_entries(self):
        sections = {"experience": """Google - Senior Engineer
Jan 2020 - Present
- Built microservices
- Led team

Microsoft - Developer
Jun 2018 - Dec 2019
- Built APIs"""}
        result = self.extractor.extract(sections)
        assert "experience_entries" in result["parsed_data"]
        entries = result["parsed_data"]["experience_entries"]
        assert len(entries) == 2
        assert entries[0]["company"] == "Google"
        assert entries[0]["role"] == "Senior Engineer"


# ============================================================
# ProjectExtractor Tests
# ============================================================

class TestProjectExtractor:
    def setup_method(self):
        self.extractor = ProjectExtractor()

    def test_extract_projects_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_projects(self):
        sections = {"projects": """Resume Builder
- Built a full-stack resume builder
- Technologies: React, Python, PostgreSQL"""}
        result = self.extractor.extract(sections)
        assert "projects" in result["parsed_data"]
        assert len(result["parsed_data"]["projects"]) == 1
        assert result["parsed_data"]["projects"][0]["name"] == "Resume Builder"


# ============================================================
# AchievementExtractor Tests
# ============================================================

class TestAchievementExtractor:
    def setup_method(self):
        self.extractor = AchievementExtractor()

    def test_extract_achievements_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_with_metrics(self):
        sections = {"experience": "- Increased revenue by 35%\n- Reduced costs by $50,000"}
        result = self.extractor.extract(sections)
        assert len(result["entities"]) > 0


# ============================================================
# MetricExtractor Tests
# ============================================================

class TestMetricExtractor:
    def setup_method(self):
        self.extractor = MetricExtractor()

    def test_extract_metrics_empty(self):
        result = self.extractor.extract({})
        assert result["entities"] == []

    def test_extract_percentages(self):
        sections = {"experience": "- Improved performance by 40%"}
        result = self.extractor.extract(sections)
        assert any("40%" in e["entity_value"] for e in result["entities"])

    def test_extract_currency(self):
        sections = {"experience": "- Saved $100,000 annually"}
        result = self.extractor.extract(sections)
        assert any("$" in e["entity_value"] for e in result["entities"])


# ============================================================
# ResumeKnowledgeBuilder Tests
# ============================================================

class TestResumeKnowledgeBuilder:
    def setup_method(self):
        self.builder = ResumeKnowledgeBuilder()

    def test_build_empty(self):
        knowledge = self.builder.build([], {})
        assert knowledge["skills"] == []
        assert knowledge["technologies"] == {}
        assert knowledge["summary"] == ""

    def test_build_with_entities(self):
        entities = [
            {"entity_type": "skill", "entity_value": "python"},
            {"entity_type": "skill", "entity_value": "javascript"},
            {"entity_type": "technology", "entity_value": "react"},
            {"entity_type": "technology", "entity_value": "django"},
            {"entity_type": "certification", "entity_value": "AWS Solutions Architect"},
            {"entity_type": "degree", "entity_value": "bachelor"},
            {"entity_type": "field_of_study", "entity_value": "computer science"},
        ]
        parsed_data = {"summary": "Senior developer"}

        knowledge = self.builder.build(entities, parsed_data)
        assert "python" in knowledge["skills"]
        assert "javascript" in knowledge["skills"]
        assert "technology" in knowledge["technologies"]
        assert "AWS Solutions Architect" in knowledge["certifications"]
        assert knowledge["summary"] == "Senior developer"

    def test_build_experience_summary(self):
        entities = [
            {"entity_type": "role", "entity_value": "Engineer"},
            {"entity_type": "company", "entity_value": "Google"},
        ]
        parsed_data = {
            "experience_entries": [
                {"role": "Engineer", "company": "Google", "start_date": "Jan 2020", "end_date": "Present", "bullets": ["Built stuff"]}
            ]
        }
        knowledge = self.builder.build(entities, parsed_data)
        assert len(knowledge["experience_summary"]) == 1
        assert knowledge["experience_summary"][0]["role"] == "Engineer"
