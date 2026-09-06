"""Extractor Orchestrator.

Coordinates all extractors to extract entities from parsed resume data.
"""
from typing import Any, Dict

from app.services.resume_intelligence.extractors.achievement_extractor import AchievementExtractor
from app.services.resume_intelligence.extractors.certification_extractor import CertificationExtractor
from app.services.resume_intelligence.extractors.contact_extractor import ContactExtractor
from app.services.resume_intelligence.extractors.education_extractor import EducationExtractor
from app.services.resume_intelligence.extractors.experience_extractor import ExperienceExtractor
from app.services.resume_intelligence.extractors.language_extractor import LanguageExtractor
from app.services.resume_intelligence.extractors.metric_extractor import MetricExtractor
from app.services.resume_intelligence.extractors.project_extractor import ProjectExtractor
from app.services.resume_intelligence.extractors.skill_extractor import SkillExtractor
from app.services.resume_intelligence.extractors.summary_extractor import SummaryExtractor
from app.services.resume_intelligence.extractors.technology_extractor import TechnologyExtractor


class ExtractorOrchestrator:
    """Orchestrates all extractors to extract entities from sections."""

    def __init__(self):
        self.contact_extractor = ContactExtractor()
        self.skill_extractor = SkillExtractor()
        self.technology_extractor = TechnologyExtractor()
        self.language_extractor = LanguageExtractor()
        self.certification_extractor = CertificationExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.project_extractor = ProjectExtractor()
        self.achievement_extractor = AchievementExtractor()
        self.metric_extractor = MetricExtractor()
        self.summary_extractor = SummaryExtractor()

    def extract(self, sections: Dict[str, str], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all entities from sections.

        Args:
            sections: Detected sections from parser.
            metadata: Metadata from parser.

        Returns:
            Dictionary with 'entities' list and 'parsed_data' dict.
        """
        all_entities = []
        all_parsed_data = {}

        extractors = [
            self.contact_extractor,
            self.summary_extractor,
            self.skill_extractor,
            self.technology_extractor,
            self.language_extractor,
            self.certification_extractor,
            self.education_extractor,
            self.experience_extractor,
            self.project_extractor,
            self.achievement_extractor,
            self.metric_extractor,
        ]

        for extractor in extractors:
            result = extractor.extract(sections)
            all_entities.extend(result.get("entities", []))
            all_parsed_data.update(result.get("parsed_data", {}))

        return {
            "entities": all_entities,
            "parsed_data": all_parsed_data,
        }
