"""Unit tests for Opportunity Intelligence Engine."""
import pytest


class TestOpportunityParser:
    """Tests for OpportunityParser."""

    def test_parse_empty_text(self):
        from app.services.opportunity.parsers.parser import OpportunityParser

        parser = OpportunityParser()
        result = parser.parse("")

        assert result["raw_text"] == ""
        assert result["sections"] == {}
        assert result["metadata"] == {}

    def test_parse_basic_text(self):
        from app.services.opportunity.parsers.parser import OpportunityParser

        parser = OpportunityParser()
        text = "We are looking for a Python developer with 5 years of experience."
        result = parser.parse(text)

        assert result["raw_text"] == text
        assert "general" in result["sections"]
        assert result["metadata"]["word_count"] > 0

    def test_parse_with_sections(self):
        from app.services.opportunity.parsers.parser import OpportunityParser

        parser = OpportunityParser()
        text = """Requirements:
- Python
- Django
- PostgreSQL

Responsibilities:
- Build APIs
- Write tests"""

        result = parser.parse(text)

        assert "requirements" in result["sections"]
        assert "responsibilities" in result["sections"]

    def test_preprocess_removes_html(self):
        from app.services.opportunity.parsers.parser import OpportunityParser

        parser = OpportunityParser()
        text = "<p>Hello <b>World</b></p>"
        result = parser.parse(text)

        assert "<p>" not in result["sections"].get("general", "")
        assert "<b>" not in result["sections"].get("general", "")


class TestOpportunityNormalizer:
    """Tests for OpportunityNormalizer."""

    def test_normalize_empty(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()
        result = normalizer.normalize({"sections": {}, "metadata": {}})

        assert result["sections"] == {}

    def test_normalize_text(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()
        result = normalizer.normalize({"sections": {"general": "  Hello   World  "}, "metadata": {}})

        assert result["sections"]["general"] == "Hello World"

    def test_normalize_list(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()
        result = normalizer.normalize_list(["Python", "python", "PYTHON", ""])

        assert result == ["python"]

    def test_normalize_employment_type(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()

        assert normalizer.normalize_employment_type("Full Time") == "full-time"
        assert normalizer.normalize_employment_type("contract") == "contract"
        assert normalizer.normalize_employment_type("intern") == "internship"

    def test_normalize_remote_policy(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()

        assert normalizer.normalize_remote_policy("Work from home") == "remote"
        assert normalizer.normalize_remote_policy("Hybrid") == "hybrid"
        assert normalizer.normalize_remote_policy("In office") == "onsite"

    def test_normalize_experience_level(self):
        from app.services.opportunity.parsers.normalizer import OpportunityNormalizer

        normalizer = OpportunityNormalizer()

        assert normalizer.normalize_experience_level("Junior") == "junior"
        assert normalizer.normalize_experience_level("Senior") == "senior"
        assert normalizer.normalize_experience_level("Lead") == "lead"


class TestSkillExtractor:
    """Tests for SkillExtractor."""

    def test_extract_skills_empty(self):
        from app.services.opportunity.extractors.skill_extractor import SkillExtractor

        extractor = SkillExtractor()
        result = extractor.extract({})

        assert result["entities"] == []

    def test_extract_skills_from_requirements(self):
        from app.services.opportunity.extractors.skill_extractor import SkillExtractor

        extractor = SkillExtractor()
        result = extractor.extract({"requirements": "Python, Django, PostgreSQL"})

        skills = [e["entity_value"] for e in result["entities"]]
        assert "python" in skills
        assert "django" in skills
        assert "postgresql" in skills

    def test_extract_skills_from_preferred(self):
        from app.services.opportunity.extractors.skill_extractor import SkillExtractor

        extractor = SkillExtractor()
        result = extractor.extract({"preferred": "Nice to have: React, TypeScript"})

        skills = [e["entity_value"] for e in result["entities"]]
        assert "react" in skills
        assert "typescript" in skills
        # Should be marked as not required
        for e in result["entities"]:
            if e["entity_value"] in ["react", "typescript"]:
                assert e["is_required"] is False


class TestTechnologyExtractor:
    """Tests for TechnologyExtractor."""

    def test_extract_technologies_empty(self):
        from app.services.opportunity.extractors.technology_extractor import TechnologyExtractor

        extractor = TechnologyExtractor()
        result = extractor.extract({})

        assert result["entities"] == []

    def test_extract_technologies(self):
        from app.services.opportunity.extractors.technology_extractor import TechnologyExtractor

        extractor = TechnologyExtractor()
        result = extractor.extract({"general": "Experience with AWS, Docker, Kubernetes"})

        techs = [(e["entity_value"], e["entity_type"]) for e in result["entities"]]
        assert ("aws", "cloud_platform") in techs
        assert ("docker", "devops_tool") in techs
        assert ("kubernetes", "devops_tool") in techs


class TestExperienceExtractor:
    """Tests for ExperienceExtractor."""

    def test_extract_years(self):
        from app.services.opportunity.extractors.experience_extractor import ExperienceExtractor

        extractor = ExperienceExtractor()
        result = extractor.extract({"general": "5+ years of experience"})

        assert result["parsed_data"].get("min_experience_years") == 5

    def test_extract_level(self):
        from app.services.opportunity.extractors.experience_extractor import ExperienceExtractor

        extractor = ExperienceExtractor()
        result = extractor.extract({"general": "Senior Python Developer"})

        assert result["parsed_data"].get("experience_level") == "senior"

    def test_extract_education(self):
        from app.services.opportunity.extractors.experience_extractor import ExperienceExtractor

        extractor = ExperienceExtractor()
        result = extractor.extract({"general": "Bachelor's degree in Computer Science"})

        education = [e["entity_value"] for e in result["entities"]]
        assert any("bachelor" in e.lower() for e in education)


class TestLocationExtractor:
    """Tests for LocationExtractor."""

    def test_extract_remote(self):
        from app.services.opportunity.extractors.location_extractor import LocationExtractor

        extractor = LocationExtractor()
        result = extractor.extract({"general": "Remote position"})

        assert result["parsed_data"].get("remote_policy") == "remote"

    def test_extract_location(self):
        from app.services.opportunity.extractors.location_extractor import LocationExtractor

        extractor = LocationExtractor()
        result = extractor.extract({"general": "Position in San Francisco"})

        locations = [e["entity_value"] for e in result["entities"]]
        assert "san francisco" in locations

    def test_extract_employment_type(self):
        from app.services.opportunity.extractors.location_extractor import LocationExtractor

        extractor = LocationExtractor()
        result = extractor.extract({"general": "Full-time position"})

        assert result["parsed_data"].get("employment_type") == "full-time"
